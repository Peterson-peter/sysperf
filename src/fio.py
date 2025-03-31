from .parse_fio_output import parse_output
import os
import time
import subprocess
import yaml
import logging
import json

logger = logging.getLogger(__name__)


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
            logger.info("opening " + abs_file_path)
            settings  = yaml.safe_load(f)
        self._settings = settings
    
    def run(self, device: str):
        """
        This function runs predescribed jobs in the fio.yaml file. Edit the file under models/fio.yaml.
        by default it will run 240 jobs.

        """
        report = []
        for job in self._settings["job"]:
            #call the logger here for kernel traces kick off into the background
            for blocksize in self._settings["blocksize"]:
                for numjobs in self._settings["numjobs"]:
                    for iodepth in self._settings["iodepth"]:

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
                        --group_reporting"+" \
                        --output-format=" + self._settings["output-format"]

                        logger.info("Running command: " + command)
                        for iterations in range (0, self._settings["iterations"]):
                            time.sleep(2) #allow any previous runs to cleanup 
                            #kill traces 
                            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
                            output = output.decode('utf-8')
                            output = json.loads(output)
                            report.append(output)
                        average_ouput = parse_output(report)
                        #Create the output file name
                        file_name = "/tmp/" + \
                            self._settings["job"] + "_" + \
                            self._settings["blocksize"] + "_" + \
                            self._settings["numjobs"] + "_" + \
                            self._settings["iodepth"] + "_" + \
                            "fio_ouput.json"
                        with open(file_name, "w" ) as f:
                            f.write(json.dumps(average_ouput, indent=4))
                            
                            
