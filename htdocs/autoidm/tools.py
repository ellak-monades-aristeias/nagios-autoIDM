#!/usr/bin/env python
 
import os,sys,subprocess,threading
import struct, socket
import datetime, time, signal




autoidm_path = "/usr/share/nagios3/htdocs/autoidm/"
nagios_cfg_path = "/etc/nagios3/nagios.cfg"


def current_path():
    global autoidm_path
    return autoidm_path
    

def ip2int(addr):                                                               
    return struct.unpack("!I", socket.inet_aton(addr))[0]                       


def int2ip(addr):                                                               
    return socket.inet_ntoa(struct.pack("!I", addr))   


def cidr_to_iprange(input): 
    # Split ip and prefix
    (addrString, cidrString) = input.split('/')
     
    # CIDR to int
    addr = addrString.split('.')
    cidr = int(cidrString)
     
    # calc mask
    mask = [0, 0, 0, 0]
    for i in range(cidr):
        mask[i/8] = mask[i/8] + (1 << (7 - i % 8))
     
    # calc network
    net = []
    for i in range(4):
        net.append(int(addr[i]) & mask[i])
     
    # calc broad
    broad = list(net)
    brange = 32 - cidr
    for i in range(brange):
        broad[3 - i/8] = broad[3 - i/8] + (1 << (i % 8))

    ip_range = [int2ip(x) for x in range(ip2int(".".join(map(str, net)))+1, ip2int(".".join(map(str, broad))))]

    dict = {"cidr": input, "netmask": ".".join(map(str, mask)),
            "network": ".".join(map(str, net)),
            "broadcast": ".".join(map(str, broad)),
            "range": ip_range}
    
    return dict
    
    
def call_and_peek_output(cmd, shell=False):
    import pty, subprocess
    master, slave = pty.openpty()
    p = subprocess.Popen(cmd, shell=shell, stdin=None, stdout=slave, close_fds=True)
    os.close(slave)
    line = ""
    clock_running = True
    t1 = int(time.time())+1  # timer
    while True:   
        try:
            ch = os.read(master, 1)
        except OSError:
            break
        line += ch
        if ch == '\n':
            yield line
            line = ""
    if line:
        yield line

    ret = p.wait()
    if ret and (ret > 2 or ret < 0):
        print "CMD: "+cmd
        raise subprocess.CalledProcessError(ret, cmd)
    
    
def timeout_command(command, timeout):
    """call shell-command and either return its output or kill it
    if it doesn't normally exit within timeout seconds and return None"""
    import subprocess, datetime, os, time, signal

    cmd = command.split(" ")
    start = datetime.datetime.now()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while process.poll() is None:
        time.sleep(0.1)
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            return "Hard-Timeout"
    return process.stdout.read() 


def timeout_command_code(command, timeout):
    """call shell-command and either return its output or kill it
    if it doesn't normally exit within timeout seconds and return None"""
    import subprocess, datetime, os, time, signal
    cmd = command.split(" ")
    start = datetime.datetime.now()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while process.poll() is None:
        time.sleep(0.1)
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            return "Hard-Timeout"
    return process.stdout.read(), process.returncode


def verify_config():
    global nagios_cfg_path
    cmd = 'sudo /usr/sbin/nagios3 -v '+nagios_cfg_path
    errors = 0
    
    lines, code = timeout_command_code(cmd,150)
    if code != 0:
        return lines
    else:
        return "OK"