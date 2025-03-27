import os
import time
import subprocess
import yaml



class fio:

    """
    This is a class the runs linux fio with settings on a drive
    https://fio.readthedocs.io/en/latest/
    """

    def __init__(self):
        """
        init loads the fio settings from a file
        """
        location = os.path.dirname(__file__)
        rel_path = "models/fio.yaml"
        abs_file_path = os.path.join(location, rel_path)
        with open(abs_file_path) as f:
            print("opening " + abs_file_path)
            settings  = yaml.safe_load(f)
        self._settings = settings
        print(settings["iogengine"])
    
    def run(self, device: str):
        """
        This function runs predescribed jobs in the fio.yaml file. Edit the file under models/fio.yaml.
        by default it will run 240 jobs.

        """
        for job in self._settings["job"]:
            for blocksize in self._settings["blocksize"]:
                for numjobs in self._settings["numjobs"]:
                    for iodepth in self._settings["iodepth"]:

                        result = "" + \
                        str(job) + ";" + \
                        str(blocksize) + ";" + \
                        str(numjobs) + ";" + \
                        str(iodepth) + ";" 

                        command = "sudo fio --minimal -name=temp-fio \
                        --bs="+str(blocksize)+" \
                        --ioengine=libaio \
                        --iodepth="+str(iodepth)+" \
                        --size="+self._settings["file_size"]+" \
                        --direct=1 \
                        --rw="+str(job)+" \
                        --filename=/dev/"+str(device)+" \
                        --numjobs="+str(numjobs)+" \
                        --time_based \
                        --runtime="+self._settings["runtime"]+" \
                        --group_reporting"

                        for iterations in range (0, self._settings["iterations"]):
                            time.sleep(10) #allow any previous runs to cleanup
                            output = subprocess.check_output(command, shell=True)

                            iops = iops + float(output)
