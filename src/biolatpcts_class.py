from bcc import BCC
from time import sleep
from threading import Event
import json
import os
import logging


class biolatpcts:
    MSEC = 1000
    SEC = 1000 * 1000

    def __init__(self, device: str, interval: int = 3, percentiles: list = [1,10,25,50,75,95,99]):
        self._deivce = device
        self._interval = interval
        self._percentiles = percentiles
        self._MSEC = 1000
        self._SEC = 1000 * 1000
        self._verbose = 0
        bpf_source = """
        #include <linux/blk_types.h>
        #include <linux/blkdev.h>
        #include <linux/blk-mq.h>
        #include <linux/time64.h>

        BPF_PERCPU_ARRAY(rwdf_100ms, u64, 400);
        BPF_PERCPU_ARRAY(rwdf_1ms, u64, 400);
        BPF_PERCPU_ARRAY(rwdf_10us, u64, 400);

        RAW_TRACEPOINT_PROBE(block_rq_complete)
        {
                // TP_PROTO(struct request *rq, blk_status_t error, unsigned int nr_bytes)
                struct request *rq = (void *)ctx->args[0];
                unsigned int cmd_flags;
                u64 dur;
                size_t base, slot;

                if (!rq->__START_TIME_FIELD__)
                        return 0;

                if (!rq->__RQ_DISK__ ||
                    rq->__RQ_DISK__->major != __MAJOR__ ||
                    rq->__RQ_DISK__->first_minor != __MINOR__)
                        return 0;

                cmd_flags = rq->cmd_flags;
                switch (cmd_flags & REQ_OP_MASK) {
                case REQ_OP_READ:
                        base = 0;
                        break;
                case REQ_OP_WRITE:
                        base = 100;
                        break;
                case REQ_OP_DISCARD:
                        base = 200;
                        break;
                case REQ_OP_FLUSH:
                        base = 300;
                        break;
                default:
                        return 0;
                }

                dur = bpf_ktime_get_ns() - rq->__START_TIME_FIELD__;

                slot = min_t(size_t, div_u64(dur, 100 * NSEC_PER_MSEC), 99);
                rwdf_100ms.increment(base + slot);
                if (slot)
                        return 0;

                slot = min_t(size_t, div_u64(dur, NSEC_PER_MSEC), 99);
                rwdf_1ms.increment(base + slot);
                if (slot)
                        return 0;

                slot = min_t(size_t, div_u64(dur, 10 * NSEC_PER_USEC), 99);
                rwdf_10us.increment(base + slot);
                return 0;
        }
        """
        pcts = self._percentiles.split(',')
        pcts.sort(key=lambda x: float(x))
        stat = os.stat('/dev/' + self._deivce)
        major = os.major(stat.st_rdev)
        minor = os.minor(stat.st_rdev)
        start_time_field = 'io_start_time_ns'
        bpf_source = bpf_source.replace('__START_TIME_FIELD__', start_time_field)
        bpf_source = bpf_source.replace('__MAJOR__', str(major))
        bpf_source = bpf_source.replace('__MINOR__', str(minor))

    def run(self):
        if BPF.kernel_struct_has_field(b'request', b'rq_disk') == 1:
            bpf_source = bpf_source.replace('__RQ_DISK__', 'rq_disk')
        else:
            bpf_source = bpf_source.replace('__RQ_DISK__', 'q->disk')

        bpf = BPF(text=bpf_source)
        cur_rwdf_100ms = bpf["rwdf_100ms"]
        cur_rwdf_1ms = bpf["rwdf_1ms"]
        cur_rwdf_10us = bpf["rwdf_10us"]

        last_rwdf_100ms = [0] * 400
        last_rwdf_1ms = [0] * 400
        last_rwdf_10us = [0] * 400

        rwdf_100ms = [0] * 400
        rwdf_1ms = [0] * 400
        rwdf_10us = [0] * 400

        io_type = ["read", "write", "discard", "flush"]

        keep_running = True
        result_req = Event()
        result_req.set();
        while keep_running:
            result_req.wait(self._interval if self._interval > 0 else None)
            result_req.clear()

            update_last_rwdf = self._interval > 0
            force_update_last_rwdf = False
            rwdf_total = [0] * 4;

            for i in range(400):
                v = cur_rwdf_100ms.sum(i).value
                rwdf_100ms[i] = max(v - last_rwdf_100ms[i], 0)
                if update_last_rwdf:
                    last_rwdf_100ms[i] = v

                v = cur_rwdf_1ms.sum(i).value
                rwdf_1ms[i] = max(v - last_rwdf_1ms[i], 0)
                if update_last_rwdf:
                    last_rwdf_1ms[i] = v

                v = cur_rwdf_10us.sum(i).value
                rwdf_10us[i] = max(v - last_rwdf_10us[i], 0)
                if update_last_rwdf:
                    last_rwdf_10us[i] = v

                rwdf_total[int(i / 100)] += rwdf_100ms[i]
            
            rwdf_lat = []
            for i in range(4):
                left = i * 100
                right = left + 100
                rwdf_lat.append(
                    self.calc_lat_pct(self._percentiles, 
                                rwdf_total[i],
                                rwdf_100ms[left:right],
                                rwdf_1ms[left:right],
                                rwdf_10us[left:right]))
            result = {}
            for iot in range(4):
                lats = {}
                for pi in range(len(self._percentiles)):
                    lats[self._percentiles[pi]] = rwdf_lat[iot][pi] / self._SEC
                result[io_type[iot]] = lats
            logging.info(json.dumps(result), flush=True)
 
    def calc_lat_pct(self, req_pcts, total, lat_100ms, lat_1ms, lat_10us):
        pcts = [0] * len(req_pcts)

        if total == 0:
            return pcts

        data = [(100 * self._MSEC, lat_100ms), (self._MSEC, lat_1ms), (10, lat_10us)]
        data_sel = 0
        idx = 100
        counted = 0

        for pct_idx in reversed(range(len(req_pcts))):
            req = float(req_pcts[pct_idx])
            while True:
                last_counted = counted
                (gran, slots) = data[data_sel]
                (idx, counted) = self.find_pct(req, total, slots, idx, counted)
                if self._verbose > 1:
                    print('pct_idx={} req={} gran={} idx={} counted={} total={}'
                        .format(pct_idx, req, gran, idx, counted, total))
                if idx > 0 or data_sel == len(data) - 1:
                    break
                counted = last_counted
                data_sel += 1
                idx = 100

            pcts[pct_idx] = gran * idx + gran / 2

        return pcts
    
    def format_usec(self, lat):
        if lat > self._SEC:
            return '{:.1f}s'.format(lat / self._SEC)
        elif lat > 10 * self._MSEC:
            return '{:.0f}ms'.format(lat / self._MSEC)
        elif lat > self._MSEC:
            return '{:.1f}ms'.format(lat / self._MSEC)
        elif lat > 0:
            return '{:.0f}us'.format(lat)
        else:
            return '-'

    def find_pct(self, req, total, slots, idx, counted):
        while idx > 0:
            idx -= 1
            if slots[idx] > 0:
                counted += slots[idx]
                if self._verbose > 1:
                    print('idx={} counted={} pct={:.1f} req={}'
                        .format(idx, counted, counted / total, req))
                if (counted / total) * 100 >= 100 - req:
                    break
        return (idx, counted)
    