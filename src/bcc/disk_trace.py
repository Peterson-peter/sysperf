from bcc import BPF
from bcc.utils import printb

# Load the eBPF program from an external file
bpf = BPF(src_file="disk_trace.c")
bpf.attach_tracepoint(tp="block:block_rq_issue", fn_name="trace_disk_io")

# Define the output format
def print_event(cpu, data, size):
    event = bpf["events"].event(data)
    printb(b"%-6d %-16s %-8s %-10d %-10d %-2s" % (
        event.pid, event.comm, event.disk_name, event.sector, event.bytes, bytes(event.rwflag)))

# Print header
print("%-6s %-16s %-8s %-10s %-10s %-2s" % ("PID", "COMM", "DISK", "SECTOR", "BYTES", "RW"))

# Loop to print events
bpf["events"].open_perf_buffer(print_event)
while True:
    try:
        bpf.perf_buffer_poll()
    except KeyboardInterrupt:
        exit()