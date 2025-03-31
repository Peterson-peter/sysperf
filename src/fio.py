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
            logger.debug("loading yaml file")
            settings  = yaml.safe_load(f)
        self._settings = settings
    
    def run(self, device: str):
        """
        This function runs prescribed jobs in the fio.yaml file. Edit the file under models/fio.yaml.
        by default it will run 240 jobs.

        """
        report = []
        logger.info("Starting the loops based on fio.yaml")
        for job in self._settings["job"]:
            for blocksize in self._settings["blocksize"]:
                for numjobs in self._settings["numjobs"]:
                    for iodepth in self._settings["iodepth"]:
                        #create the file saving template
                        file_names = "/tmp/" + \
                            str(job) + "_" + \
                            str(blocksize) + "_" + \
                            str(numjobs) + "_" + \
                            str(iodepth) + "_"

                        biolatency_file = file_names + "biolatency.json"
                        command = "./bin/biolatency-bpfcc 1 -j > " + biolatency_file
                        logger.info("starting Biolatency in a different processes") 
                        biolatency = subprocess.Popen(command)
                        biolatpcts_file = file_names + "biolatpcts.json"
                        command = "./bin/biolatpcts-bpfcc /dev/" + device + " -j > " + biolatpcts_file
                        logger.info("starting Biolatpcts in a different processes")
                        biolatpcts = subprocess.Popen(command)
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
                            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
                            output = output.decode('utf-8')
                            output = json.loads(output)
                            logger.info("Adding iteration")
                            report.append(output)
                        logger.info("Terminating the eBPF processes")
                        biolatency.terminate()
                        biolatpcts.terminate()
                        average_output = parse_output(report)
                        #Create the output file name
                        fio_file_name = file_names + "fio_output.json"
                        with open(fio_file_name, "w" ) as f:
                            logger.info("writing output")
                            f.write(json.dumps(average_output, indent=4))
                            
                            
