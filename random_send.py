import argparse
import sys
import socket
import random
import struct

from scapy.all import sendp, send, hexdump, get_if_list, get_if_hwaddr
from scapy.all import Ether, IP, UDP, TCP
from scapy.all import IntField, FieldListField, FieldLenField, ShortField
from scapy.packet import Packet, bind_layers
from intHeader import SwitchTrace
from time import sleep

TYPE_INT = 0x1212
TYPE_IPV4 = 0X800

def get_if():
    ifs = get_if_list()
    iface = None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface = i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def main():
    iface = get_if()
    kk=random.randint(0,8)
    addr="10.0.{}.{}".format(kk,kk)
    print("sending on interface %s to %s" % (iface, str(addr)))
    pkt = Ether(src=get_if_hwaddr(iface), dst="ff:ff:ff:ff:ff:ff", type = TYPE_INT)
    pkt = pkt/SwitchTrace()/IP(dst=addr)/TCP()
    
    try:
      for i in range(0,random.randint(0,4)):
        sendp(pkt, iface=iface)
        #pkt.show2()
        sleep(random.randint(0,3))
    except KeyboardInterrupt:
        raise

if __name__ == '__main__':
    for i in range (0,1000):
        main()
        print "finsh send a packet "
        sleep(random.random())
