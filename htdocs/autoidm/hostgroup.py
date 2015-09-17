from tempfile import mkstemp
from shutil import move
from os import remove, close, chmod
from tools import current_path

curr_path = current_path()
path_to_hostgroups = curr_path+"conf.d/autoidm/autoidm_hostgroups.cfg"


def list_services():
    global path_to_hostgroups
    all_service = []
    all_service.append("None")
    with open(path_to_hostgroups) as f:    
        for line in f:
            if "alias" in line:
                if "#" not in line:
                    tmp_service = line.rsplit("alias")
                    service = tmp_service[1].strip()
                    if service != 'all':
                        all_service.append(service)

    return all_service


def add_del_to_hostgroups(hostname, service, action):
    global path_to_hostgroups
    switch = "off"
    
    if service == "None":
        return "OK"
    else:
        # Create temp file
        fh, abs_path = mkstemp()
        new_file = open(abs_path,'w')
        
        with open(path_to_hostgroups) as f:    
            for line in f:
                if "alias\t\t\t"+service in line:
                    switch = "on"
                    new_file.write(line)
                elif switch != "on":
                    new_file.write(line)
                    
                if "members\t\t\t" in line and switch == "on":
                    print line
                    if action == 'del':
                        if hostname in line:                    
                            p1 = line.find(hostname)-2
                            p2 = line.find(hostname)+len(hostname)
                            line_to_change = line
                            new_line = line[0:p1] + line[p2:]
                            new_file.write(new_line)
                        switch = "off"
                    elif action == 'add':
                        if hostname not in line:  
                            new_line = line[0:-1]+', '+hostname+'\n'
                            # print new_line
                            new_file.write(new_line)
                        switch = "off"
            
        # close temp file
        new_file.close()
        close(fh)

        # Remove original file
        remove(path_to_hostgroups)

        # Move new file
        move(abs_path, path_to_hostgroups)
        chmod(path_to_hostgroups,0644)  # CHMOD

        return "OK"
