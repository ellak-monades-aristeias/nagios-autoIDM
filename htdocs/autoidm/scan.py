#!/usr/bin/env python

from optparse import OptionParser
from socket import *
from tools import cidr_to_iprange
import sys


def is_valid(port):
    try:
        return 1 <= int(port) <= 65535
    except ValueError:
        return False


def port_test(ip, port):

    # New socket
    s = socket(AF_INET, SOCK_STREAM)
    # s.setdefaulttimeout(30)
    result = s.connect_ex((ip, port))
    s.close()

    if result == 0:
        return 0
    return 1


def check(ip, port):
    status = 0
    status_string = ['OK', 'WARNING', 'CRITICAL']
    totals = {0: [], 1: []}

    st = port_test(ip, int(port))
    totals[st].append(port)
    if st == 1 and not status > 0:
        status = 2
    if totals[0]:
        return "OK"
    else:
        return "CRITICAL"


def scan_subnet(range):
    for ip in range:
        check(ip, ['22'])
    return "scan finished"


def host_group_id():
    ssh = {22}
    sip = {5060}
    pbx = {22, 5060}