from check_services import check_host_up, match_hostgroup, read_services_config
from tools import cidr_to_iprange, timeout_command, verify_config
from domain_cfg import domain_cfg, del_domain
from hostgroup import list_services, add_del_to_hostgroups

import re
import cgi


def index(req):
    req.content_type = "Content-Type: application/xml"
    type = req.form.getfirst("type")
    if type == 'subnet':
        subnet_pattern = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/(\d|[1-2]\d|3[0-2]))$")
        (hostgroups, all_services, service_checks) = read_services_config()
        subnet = req.form.getfirst("subnet_id")
        name = req.form.getfirst("subnet_name")
        name = cgi.escape(name)
        if subnet_pattern.match(subnet):
            
            service_name = {
                'None': 'None',
                'debian-servers': 'debian',
                'http-servers': 'http',
                'Asterisk-servers': 'asterisk',
                'SIP-CISCO-devices': 'ciscophone',
                'SIP-GRANDSTREAM-devices': 'grandstreamphone',
                'Windows-Hosts': 'windowshost',
                'Windows-Servers': 'windowsserver',
                'NAS': 'nas',
                'VMware-Hypervisors': 'esx',
                'Routers': 'mikrotik',
                'Switches': 'switch',
                'UNIX-Linux-boxes': 'unix'}
            
            all_ip = cidr_to_iprange(subnet)['range']
            
            result = ''
            hosts_to_add = {}
            for x in range(0,len(all_ip)):
                host_status = check_host_up(all_ip[x])
                result += host_status+"|||| \n"
                if "UP" in host_status: 
                    hostgroup_match = match_hostgroup(all_ip[x], hostgroups, all_services, service_checks)           
                    for i in range(0,len(hostgroup_match)):
                        service = hostgroup_match[i]
                        if service in hosts_to_add: 
                            list_key = str(len(hosts_to_add[service])+1)
                            hosts_to_add[hostgroup_match[i]].append({
                                'ip': str(all_ip[x]),
                                'domain': name,
                                'hostname': service_name[service]+list_key})
                        else:
                            hosts_to_add[hostgroup_match[i]] = []
                            list_key = '1'
                            hosts_to_add[hostgroup_match[i]].append({
                                'ip': str(all_ip[x]),
                                'domain': name,
                                'hostname': service_name[service]+list_key})
            my_str = ' HOSTS ADDED: '
            for item in hosts_to_add:
                for x in range(0, len(hosts_to_add[item])):
                    ip = domain = hostname = service = 'BAD ENTRY'+str(hosts_to_add[item][x])
                    
                    ip = hosts_to_add[item][x]['ip']
                    domain = hosts_to_add[item][x]['domain']
                    hostname = hosts_to_add[item][x]['hostname']
                    service = item
                    
                    domain_cfg(ip, domain, hostname, service)
                    add_del_to_hostgroups(hostname+'.'+domain, service, 'add')            
                    my_str += "IP: "+str(ip)+", HOSTNAME: "+str(hostname)+", DOMAIN NAME: "+str(domain) + \
                              ", SERVICE/GROUP: "+str(service)+" || \n"
            
            verification = verify_config()
            if "OK" in verification:
                timeout_command("sudo service nagios3 restart", 1500)
                return "<?xml version=\"1.0\"?> <message>"+my_str+" </message>"
            else:
                return "<?xml version=\"1.0\"?> <message>"+verification+" </message>"
        else:
            return "<?xml version=\"1.0\"?> <message> Bad input. The subnet should follow the CIDR format</message>"
    
    elif type == 'single':
        new_hosts = []
        counter = req.form.getfirst("counter")
        for i in range(0, int(counter)+1):
            ip = req.form.getfirst("ip-single"+str(i))
            name = req.form.getfirst("hostname"+str(i))
            group = req.form.getfirst("host-group"+str(i))
            
            temp_dict = {'ip': ip, 'name': name, 'group': group}
            new_hosts.append(temp_dict)

            
        hosts = ''
        my_str = " "
        hosts_to_add = []
        
        ip_pattern = re.compile("((^|\.)((25[0-5])|(2[0-4]\d)|(1\d\d)|([1-9]?\d))){4}$")
        for i in range(0, len(new_hosts)):
            ip_to_check = str(new_hosts[i]['ip'])
            if '.' in str(new_hosts[i]['name']):
                domain_ok = True
            else:
                domain_ok = False
            
            if ip_pattern.match(ip_to_check) and domain_ok:
                my_str += "IP: "+ip_to_check+", HOSTNAME: "+new_hosts[i]['name'].split(".", 1)[0] + \
                          ", DOMAIN NAME: " + new_hosts[i]['name'].split(".", 1)[1]+", SERVICE/GROUP:" + \
                          new_hosts[i]['group']+" || \n"
                hosts_to_add.append(ip_to_check)
                
                domain_cfg(ip_to_check,
                           str(new_hosts[i]['name'].split(".", 1)[1]),
                           str(new_hosts[i]['name'].split(".", 1)[0]),
                           str(new_hosts[i]['group']))
                add_del_to_hostgroups(str(new_hosts[i]['name']), str(new_hosts[i]['group']), 'add')
                
                verification = verify_config()
                if "OK" in verification:
                    timeout_command("sudo service nagios3 restart", 1500)
                    s = "<?xml version=\"1.0\"?> <message> HOSTS ADDED: "+my_str+" </message>"  
                    return s
                else:
                    return "<?xml version=\"1.0\"?> <message>"+verification+" </message>"
            else:
                return "<?xml version=\"1.0\"?> <message> A row has a non-valid IP address OR Bad Hostname" \
                       " (the hostname must follow the format <hostname>.<domain>) </message>"
 
        s = "<?xml version=\"1.0\"?> <message> HOSTS ADDED: "+my_str+" </message>"  
        return s

    elif type == 'service-list':
        service_list = list_services()
        for item in range(0, len(service_list)):
            service_list[item] += "</option>"
        s = "<?xml version=\"1.0\"?> <message> <option>%s </message>" % ' <option>'.join(map(str, service_list))
        return s
    
    elif type == 'del':
        new_hosts = []
        counter = req.form.getfirst("counter")
        for i in range(0,int(counter)+1):
            ip = req.form.getfirst("ip-single"+str(i))
            name = req.form.getfirst("hostname"+str(i))
            group = req.form.getfirst("host-group"+str(i))
            
            temp_dict = {'ip': ip, 'name': name, 'group': group}
            new_hosts.append(temp_dict)

            
        hosts = ''
        my_str = " "
        hosts_to_add = []
        
        ip_pattern = re.compile("((^|\.)((25[0-5])|(2[0-4]\d)|(1\d\d)|([1-9]?\d))){4}$")
        for i in range(0, len(new_hosts)):
            domain_ok = False
            ip_to_del = str(new_hosts[i]['ip'])
            if '.' in str(new_hosts[i]['name']):
                domain = str(new_hosts[i]['name'].split(".", 1)[1])
                host = str(new_hosts[i]['name'].split(".", 1)[0])
                domain_ok = True
            service = str(new_hosts[i]['group'])
            
            if ip_pattern.match(ip_to_del) and domain_ok:
                
                founder = del_domain(ip_to_del, domain, service, host)
                if founder == "yes":
                    my_str = my_str + " // "+ip_to_del+' , '+domain+' , '+service
                    add_del_to_hostgroups(str(new_hosts[i]['name']), service, 'del')

                else:
                    verification = verify_config()
                    if "OK" in verification:
                        timeout_command("sudo service nagios3 restart", 1500)
                        s = "<?xml version=\"1.0\"?> <message> Wrong combination of Host and Hostgroup " \
                            "OR Host not found for IP: "+str(ip_to_del)+" </message>"
                        return s
                    else:
                        return "<?xml version=\"1.0\"?> <message>"+verification+" </message>"
            else:
                return "<?xml version=\"1.0\"?> <message> A row has a non-valid IP address OR Bad Hostname " \
                       "(the hostname must follow the format <hostname>.<domain>) </message>"
        s = "<?xml version=\"1.0\"?> <message> HOSTS DELETED: " + my_str + ' </message>'
        verification = verify_config()
        if "OK" in verification:
            timeout_command("sudo service nagios3 restart", 15)
            return s    
        else:
            return "<?xml version=\"1.0\"?> <message>"+verification+" </message>"