import json



def parse_output(output: list) -> dict:
    #specifcy the values that we want
    read_iops : int
    read_iops_min : int
    read_iops_max : int
    #Completion latency (clat) Submission to the kernel and when the IO is complete.
    read_clat_ns_min : int
    read_clat_ns_max : int
    read_clat_ns_mean : float
    #Submission latency (slat) how long did it take to submit this IO to the kernel for processing
    read_slat_ns_min : int
    read_slat_ns_max : int
    read_slat_ns_mean : float
    read_lat_ns_min : int
    read_lat_ns_max : int
    read_lat_ns_mean : float
    write_iops : int
    write_iops_min : int
    write_iops_max : int
    write_clat_ns_min : int
    write_clat_ns_max : int
    write_clat_ns_mean : int
    write_slat_ns_min : int
    write_slat_ns_max : int
    write_slat_ns_mean : float
    write_lat_ns_min : int
    write_lat_ns_max : int
    write_lat_ns_mean : float

    #fill the values that we want
    for interation in output:
        interation = interation[0].decode('utf-8')
        interation = json.loads(interation)
        read_iops += interation["jobs"][0]['read']['iops']
        read_iops_min += interation['jobs'][0]['read']['iops_min']
        read_iops_max += interation['jobs'][0]['read']['iops_max']
        read_clat_ns_min += interation['jobs'][0]['read']['clat_ns']['min']
        read_clat_ns_max += interation['jobs'][0]['read']['clat_ns']['max']
        read_clat_ns_mean += interation['jobs'][0]['read']['clat_ns']['mean']
        read_slat_ns_min += interation['jobs'][0]['read']['slat_ns']['min']
        read_slat_ns_max += interation['jobs'][0]['read']['slat_ns']['max']
        read_slat_ns_mean += interation['jobs'][0]['read']['slat_ns']['mean']
        read_lat_ns_min += interation['jobs'][0]['read']['lat_ns']['min'] 
        read_lat_ns_max += interation['jobs'][0]['read']['lat_ns']['max']
        read_lat_ns_mean += interation['jobs'][0]['read']['lat_ns']['mean']
        write_iops += interation["jobs"][0]['write']['iops']
        write_iops_min += interation['jobs'][0]['write']['iops_min']
        write_iops_max += interation['jobs'][0]['write']['iops_max']
        write_clat_ns_min += interation['jobs'][0]['write']['clat_ns']['min']
        write_clat_ns_max += interation['jobs'][0]['write']['clat_ns']['max']
        write_clat_ns_mean += interation['jobs'][0]['write']['clat_ns']['mean']
        write_slat_ns_min += interation['jobs'][0]['write']['slat_ns']['min']
        write_slat_ns_max += interation['jobs'][0]['write']['slat_ns']['max']
        write_slat_ns_mean += interation['jobs'][0]['write']['slat_ns']['mean']
        write_lat_ns_min += interation['jobs'][0]['write']['lat_ns']['min'] 
        write_lat_ns_max += interation['jobs'][0]['write']['lat_ns']['max']
        write_lat_ns_mean += interation['jobs'][0]['write']['lat_ns']['mean']
    #create a return dict from the values
    return_object = {"read_iops": read_iops, "read_iops_min": read_iops_min, "read_iops_max": read_iops_max, "read_clat_ns_min": read_clat_ns_min,  
                     "read_clat_ns_max": read_clat_ns_max, "read_clat_ns_mean": read_clat_ns_mean, "read_slat_ns_min": read_slat_ns_min, "read_slat_ns_max": read_slat_ns_max,
                     "read_slat_ns_mean": read_slat_ns_mean, "read_lat_ns_min": read_lat_ns_min, "read_lat_ns_max": read_lat_ns_max, "read_lat_ns_mean": read_lat_ns_mean,
                     "write_iops": write_iops, "write_iops_min": write_iops_min, "write_iops_max": write_iops_max, "write_clat_ns_min": write_clat_ns_min, 
                     "write_clat_ns_max": write_clat_ns_max, "write_clat_ns_mean": write_clat_ns_mean, "write_slat_ns_min": write_slat_ns_min, "write_clat_ns_max": write_clat_ns_max,
                     "write_slat_ns_mean": write_slat_ns_mean, "write_lat_ns_min": write_lat_ns_min, "write_lat_ns_max": write_lat_ns_max, "write_lat_ns_mean": write_lat_ns_mean}
    #get the average of the values 
    for key in return_object.keys():
        return_object[key] = return_object[key]/len(output)
    
    return return_object
    
        
    
