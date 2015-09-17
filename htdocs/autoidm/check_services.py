from tools import call_and_peek_output, current_path, timeout_command
import os

config_file = 'config'
hard_timeout = 1


def get_check_plugins_path():
    global config_file
    curr_path = current_path()
    path = 'path config for Check_plugins is empty'
    with open(curr_path+config_file) as f:
        for line in f:
            if 'check_plugins_path' in line:
                path = line.split("=")[1].strip()
                break
    return path
    

def read_services_config():
    global config_file
    curr_path = current_path()
    hostgroups = {}
    all_services = {}
    serv_switch = 'off'
    service_checks = {}
    with open(curr_path+config_file) as f:
        for line in f:
            if 'tcp-service' in line or 'udp-service' in line:
                if 'tcp-service' in line:
                    proto = 'tcp'
                else:
                    proto = 'udp'
                service = line.split(":")[1][:-5].lstrip().rstrip()
                port = line.split(":")[2][:-11].lstrip().rstrip()
                all_services[service]=port
                used_for_temp1 = line.split(":")[3][:-2].lstrip().rstrip().split(",")
                used_for_temp2 = []
                for i in used_for_temp1:
                    used_for_temp2.append(i.lstrip("\""))
                used_for = []
                for i in used_for_temp2:
                    hostgroup = i.strip().lstrip("\"").rstrip("\"")
                    used_for.append(hostgroup)
                
                    if hostgroup in hostgroups:
                        hostgroups[hostgroup]["services"].append({"service": service, "port": port, "proto": proto})
                        hostgroups[hostgroup]["port_list"].append(port)
                    else:
                        hostgroups[hostgroup] = {
                            "port_list": [port],
                            "services": [{"service": service, "port": port, "proto": proto}]}
            if '-Service List Start-' in line:
                serv_switch = "on"
            if '-Service List End-' in line:
                serv_switch = "off"
            if serv_switch == 'on':
                if ":" in line:
                    serv = line.split(":",1)
                    service_checks[serv[0]]= serv[1]
                
        return hostgroups, all_services, service_checks


def match_hostgroup(ip, hostgroups, all_services, service_checks):
    global hard_timeout
    check_plugin_path = get_check_plugins_path()
    tcp_check0 = check_plugin_path+'check_tcp -H $HOSTADDRESS$ -p $PORT$ -t '+str(hard_timeout)
    ports_up = []
    common_ports = []
    host_services = {}
    for item in service_checks:
        cmd = ''
        tcp_check = tcp_check0
        if service_checks[item].isspace():
            tcp_check = tcp_check.replace('$HOSTADDRESS$', ip)
            tcp_check = tcp_check.replace('$PORT$', all_services[item])
            cmd = tcp_check
        elif '$HOSTADDRESS$' in service_checks[item]:
            new_check = check_plugin_path+service_checks[item].strip()
            new_check = new_check.replace('$HOSTADDRESS$', ip)
            new_check = new_check.replace('$PORT$', all_services[item])
            cmd = new_check
        if cmd:
            
            check_output = timeout_command(cmd, hard_timeout)
            if "OK" in check_output or "WARNING" in check_output:
                result = "OK"
                ports_up.append(all_services[item])
            else:
                result = "DOWN"
        else:
            print "BAD CHECK INPUT"

    for item in hostgroups:
        common = list(set(ports_up) & set(hostgroups[item]["port_list"]))
        common_ports.append(len(common))
        host_services[item] = {
            'ports_up': ports_up,
            'ports_required': hostgroups[item]["port_list"],
            'ports_common': common}
    matches = []
    possible_matches = {}
    final_match = []
    if max(common_ports) == 0:
        final_match.append("None")
        matches.append("None")
    else:
        for item in hostgroups:
            if len(host_services[item]['ports_required']) <= max(common_ports) and \
                            len(host_services[item]['ports_common']) == len(host_services[item]['ports_required']):
                matches.append({'service': item, 'common': len(host_services[item]['ports_common'])})
        if not matches:
            final_match.append("None")
        else:
            max_count = 0
            for i in range(0, len(matches)):
                if matches[i]['common'] > max_count:
                    max_count = matches[i]['common']
            for i in range(0, len(matches)):
                if matches[i]['common'] == max_count:
                    final_match.append(matches[i]['service'])
            if not final_match:
                final_match.append("None")
    return final_match


def check_host_up(host):
    ping = ''
    ssh = ''
    telnet = ''
    check_plugin_path = get_check_plugins_path()
    for l in call_and_peek_output([check_plugin_path+'check_ping -H ' + host + ' -w 200.0,40% -c 400.0,80% -t 2'],
                                  shell=True):
        if 'OK' in l or 'WARNING' in l:
            ping = 'PING OK'
        else:
            ping = "PING CRITICAL"
 
    for l in call_and_peek_output(['/usr/lib/nagios/plugins/check_ssh -H ' + host+' -t 2'], shell=True):
        if 'OK' in l or 'WARNING' in l:
            ssh = 'SSH OK'
        else:
            ssh = "SSH CRITICAL"

    for l in call_and_peek_output(['/usr/lib/nagios/plugins/check_tcp -H ' + host+' -p 23 -t 2'], shell=True):
        if 'OK' in l or 'WARNING' in l:
            telnet = 'TELNET OK'
        else:
            telnet = "TELNET DOWN"
    output = "**HOST: "+host+" PING: "+ping+", SSH: "+ssh+", TELNET: "+telnet
    
    status = "DOWN"
    if "OK" in output:
        status = host+"UP"
            
    return status
