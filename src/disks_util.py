import subprocess


class disk_util:

    def __init__(self):
        pass
    
def get_disks() -> list:
    """
    finds all disks on Linux and return a list of strings
    """
    disks = []
    output = subprocess.check_output(["lsblk", "-d", "-n", "-oKNAME,TYPE,RO"])
    for line in output.splitlines():
        kname, blk_type, readonly = line.split()
        if blk_type == b"disk" and readonly == b"0":
            disks.append(kname.decode('utf-8'))
    return disks


