#!/usr/bin/env python

import argparse
import sys
import socket
import random
import struct
import json

from scapy.all import sendp, send, sniff, hexdump, get_if_list, get_if_hwaddr
from scapy.all import Ether, IP, UDP, TCP
from scapy.all import IntField, FieldListField, FieldLenField, ShortField, PacketListField, XBitField
from scapy.packet import Packet, bind_layers
from intHeader import SwitchTrace
from time import sleep
import datetime
import csv
TYPE_INT = 0x1212

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def showPacket(pkt,archivename):
    #stats = {}
    #path = []
    hop_delays = []
    #timestamps = []
    queue_lengths = []
    #num = 1
    if SwitchTrace in pkt:
        #nowtime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        #print(nowtime)
        #pkt.show()
        #nowtime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        #print(nowtime)
        #print("  Switch  Delay(mS)")
        
        hop=0;
        sid = 10
        while sid != 0 :
           hop_delays.append(float(pkt[SwitchTrace][hop].hop_delay))
           #queue_lengths.append(int(pkt[SwitchTrace][hop].qdepth))
           #print(queue_lengths) 
           hop=hop+1
           sid = int(pkt[SwitchTrace][hop].swid)
        delays = sum(hop_delays)
        f = open('{}.csv'.format(archivename), 'a')
        csv_write = csv.writer(f)
        csv_write.writerow([delays])
        f.close()
        
        


def main():
    archivename =sys.argv[1]
    iface = get_if()
    print("Interface: %s" % iface)
    sniff(iface = iface, prn = lambda x: showPacket(x,archivename))

if __name__ == '__main__':
     main()
     
