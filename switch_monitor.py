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

def showPacket(pkt, INTreport_id):
    stats = {}
    path = []
    hop_delays = []
    timestamps = []
    queue_lengths = []
    if SwitchTrace in pkt:
        #pkt.show()
        #print("  Switch    Queue Len    Delay(mS)")
        hop=0;
        sid = 10
        while sid != 0 :
            path.append(int(pkt[SwitchTrace][hop].swid))
            hop_delays.append(float(pkt[SwitchTrace][hop].hop_delay))
            timestamps.append(pkt[SwitchTrace][hop].ingress)
            #queue_lengths.append(int(pkt[SwitchTrace][hop].qdepth))
            #print(path[hop], queue_lengths[hop],hop_delays[hop])
            hop=hop+1
            sid = int(pkt[SwitchTrace][hop].swid)
            #print(sid) 
        nowtime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        #print(nowtime)
        stats = {"time":nowtime, "path": path, "hop_delays": hop_delays, "timestamps": timestamps}
        with open("data/INTreport_%s"%INTreport_id, 'w') as fp:
            json.dump(stats, fp,  ensure_ascii=False, sort_keys=False)
        print ("Finish host-switch{} INT data record at {}".format(INTreport_id,nowtime))


def main():
    INTreport_id = sys.argv[1]
    iface = get_if()
    #ifac = eth1
    print("Interface: %s" % iface)
    sniff(iface = iface, prn = lambda x: showPacket(x, INTreport_id))

if __name__ == '__main__':
     main()
