from fio import fio
from disks_util import disk_util

"""
This program will automaticly run a full range of test using fio. Fio settings file can be found
at /src/models/fio.yam. It will also send the output off disk. 
"""



def main():

    disks = disk_util.get_disks()
    for disk in disks:
        if "nvme" in disk:
            fio.run(disk)


