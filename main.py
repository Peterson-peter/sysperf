from src.fio import fio
from src.disks_util import disk_util
import logging

logger = logging.getLogger(__name__)

"""
This program will automaticly run a full range of test using fio. Fio settings file can be found
at /src/models/fio.yam. It will also send the output off disk. 
"""



def main():

    disks = disk_util.get_disks()
    disk_fio = fio()
    logger.info("discovered disks: " + ''.join(disks))
    for disk in disks:
        if "nvme" in disk:
            disk_fio.run(disk)


if __name__ == "__main__":
    main()
