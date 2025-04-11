#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>

struct data_t {
    u32 pid;
    char comm[TASK_COMM_LEN];
    char disk_name[DISK_NAME_LEN];
    u64 sector;
    u64 bytes;
    char rwflag;
};

BPF_PERF_OUTPUT(events);

int trace_disk_io(struct pt_regs *ctx, struct request *req) {
    struct data_t data = {};
    struct gendisk *disk = req->rq_disk;

    data.pid = bpf_get_current_pid_tgid() >> 32;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    if (disk) {
        bpf_probe_read_kernel(&data.disk_name, sizeof(data.disk_name), disk->disk_name);
    }

    data.sector = req->__sector;
    data.bytes = req->__data_len;
    data.rwflag = (req->cmd_flags & REQ_OP_WRITE) ? 'W' : 'R';

    events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}