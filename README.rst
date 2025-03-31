.. These are the Travis-CI and Coveralls badges for your repository. Replace
   your *github_repository* and uncomment these lines by removing the leading
   two dots.

.. .. image:: https://travis-ci.org/*github_repository*.svg?branch=master
    :target: https://travis-ci.org/*github_repository*

.. .. image:: https://coveralls.io/repos/github/*github_repository*/badge.svg?branch=master
    :target: https://coveralls.io/github/*github_repository*?branch=master

Project Goals
=============
This project is part of a larger effort to automatically test disk performance. The goal is to create traffic
on the disk system and see where it has bottlenecks as viewed by the kernel. 

Things that run
===============
When main.py in run it will automatically find any disks that are nvme based and run FIO on them. 
Right before it starts FIO two eBPF processes are spawned: 
Biolatency: Which tracks latency of the disk I/O is measured from the issue to the device to its
completion.
biolatpcts traces block device I/O, and prints the latency percentiles per I/O type.

Source
=======
The eBPF binaries were complied from github source on March 28th, 2025. The binaries included in standard linux package
distribution are out of date and are missing functionality.  

FIO is controlled by /src/models/fio.yaml. It currently runs a short but wide array of tests to see how different profiles are handled.
Each test is run three times (controlled by iterations) and averages the result returning a float. A two second pause in injected
between runs to ensure the disk can complete any IO in between runs.  

Outputs
=======
Output json files are dumped into /tmp/ and are listed by job-blocksize-numjobs-iodepth-process. They are in json format for portability
into graphing utilities. 

Requirements
============
FIO needs to be installed prior to first run.

Future
======
task to be completed are listed in the notes.
