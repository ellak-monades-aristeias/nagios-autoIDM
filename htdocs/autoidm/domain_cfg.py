from tempfile import mkstemp
from shutil import move
from os import remove, close, chmod
from tools import current_path

path_to_conf_read = '/etc/nagios3/conf.d'

curr_path = current_path()
path_to_conf_write = curr_path+'conf.d'


def domain_cfg(host, domain, hostname, service):    
    global path_to_conf_read 
    global path_to_conf_write    
    
    # Create path vars
    path_to_skeleton = path_to_conf_read+'/autoidm_skeleton'
    domain_cfg = path_to_conf_read+'/'+domain+'.cfg'

    # Read skeleton File and replace appropriately
    f = open(path_to_skeleton)
    lines = f.readlines()
    f.close()
    define_host = []
    define_hostgroup = []
    hstgrp = False
    
    for item in range(0, len(lines)):
        entry = lines[item]
    
        if "define hostgroup" in entry:
            define_host.append("}")
            define_hostgroup.append(entry)                
            hstgrp = True
        elif "define host" in entry:
            define_host.append(entry)
        elif "}" not in entry:
            my_var = entry.lstrip()
            next_space = my_var.find(' ')
            my_var = my_var[0:next_space]
                   
            value_start = entry.find("<")
            value_end = entry.rfind(">")  
            placeholder = entry[value_start:value_end+1]  
    
            if my_var == "use":
                if service == 'None':
                    new_service = 'generic-host'
                else:
                    new_service = service
                new_entry = entry.replace(placeholder, new_service)
            elif my_var == "host_name":
                new_entry = entry.replace(placeholder, (hostname+'.'+domain))
            elif my_var == "alias" and not hstgrp:
                new_entry = entry.replace(placeholder, (hostname+'.'+domain))
            elif my_var == "address":
                new_entry = entry.replace(placeholder, host)
            elif my_var == "hostgroups":
                if service == 'None':
                    new_service = ''
                else:
                    new_service = ', '+service
                new_entry = entry.replace(placeholder, (domain + new_service))
            elif my_var == "hostgroup_name":
                new_entry = entry.replace(placeholder, domain)
            elif my_var == "alias" and hstgrp:
                new_entry = entry.replace(placeholder, domain)
            elif ";" in entry:
                new_entry = entry
        
            if entry != '\n':
                if not hstgrp:
                    define_host.append(new_entry)
                else:
                    define_hostgroup.append(new_entry)
    
        elif "}" in entry:
            pass
                        
        if item == len(lines)-1:
            define_hostgroup.append("}\n")
    
    # Check if file exists

    domain_cfg = path_to_conf_write+'/'+domain+'.cfg'

    try:                                        
        with open(domain_cfg) as check_file:    
            pass                                
        write_action = "a"                      
    except IOError as e:                        
        write_action = "w"                      
    
    # Write or append to file #####
    nf = open(domain_cfg, write_action)    # nf = new file
    if write_action == "a":
        for item in range(0, len(define_host)):
            nf.write(define_host[item])
        nf.write("\n")
    elif write_action == "w":
        for item in range(0, len(define_hostgroup)):
            nf.write(define_hostgroup[item])
        for item in range(0, len(define_host)):
            nf.write(define_host[item])
        nf.write("\n")
    nf.close()
    

def del_domain(ip, domain, service, hname):
    global path_to_conf_write
    
    path_to_domain_cfg = path_to_conf_write+'/'+domain+'.cfg'
    
    switch = "off"
    
    # Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    
    with open(path_to_domain_cfg) as f:
        line_counter = 0
        define_line = 0    
        define_found = False
        define_start = 0
        define_end = 0
        temp_found_addr = False # used to check for both ip and service
        # temp_found_serv = False #used to check for both ip and service
        temp_found_name = False
        founder = 'no'
                
        for line in f:
            
            if 'define host{' in line:
                define_line = line_counter
                
            if 'address' in line and ip in line:
                temp_found_addr = True  # used to check for both ip and service

            if 'host_name' in line and hname in line:
                temp_found_name = True  # used to check for hostname
                                
            if temp_found_addr and temp_found_name:
                define_found = True
                define_start = define_line
                founder = 'yes'
                   
            if '}' in line and define_found:
                define_end = line_counter
                define_found = False
                temp_found_addr = False
                temp_found_name = False
                
            line_counter += 1

    with open(path_to_domain_cfg) as f:    
        line_counter = 0   
        for line in f:
            
            line_to_del = False
            if define_start == 0 and define_end == 0:
                new_file.write(line)
            else:
                if line_counter < define_start or line_counter > define_end:
                    new_file.write(line)
            
            line_counter += 1
    # close temp file
    new_file.close()
    close(fh)
    # Remove original file
    remove(path_to_domain_cfg)
    # Move new file
    move(abs_path, path_to_domain_cfg)
    chmod(path_to_domain_cfg, 0644)  # CHMOD
           
    return founder