#!/usr/bin/env python2
import argparse
import grpc
import os
import sys
import json
from time import sleep

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))
import p4runtime_lib.bmv2
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.helper

host_num=8
def get_host():
    host=[]
    for i in range (host_num):
        h={"ip":"10.0.{}.{}".format(i+1,i+1),
           "mac":"08:00:00:00:0{}:{}{}".format(i+1,i+1,i+1),
           "dstAddr":"08:00:00:00:0{}:00".format(i+1)
           }
        host.append(h)
    return host

def write_ipv4_lpm_Rules(p4info_helper,ingress_sw, dst_eth_addr, dst_ip_addr,dst_addport,dstport):
    
    # 1)Ingress Rule
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, dst_addport)
        },
        action_name="MyIngress.ipv4_forward",
        action_params={
            "dstAddr":dst_eth_addr,
            "port": dstport
        })
    ingress_sw.WriteTableEntry(table_entry)
    #print ("update %s table ipv4 rule"% ingress_sw.name)

def wirte_drop_Rules(p4info_helper,ingress_sw):
    # 2)drop rule
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm",
        default_action=True,
        action_name="MyIngress.drop",
        action_params={
        })
    ingress_sw.WriteTableEntry(table_entry)
    #print ("update %s table drop rule" % ingress_sw.name)

def write_swtrace_Rules(p4info_helper,ingress_sw, switch_id):
    
    # 3)Egress Rule
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyEgress.swtrace",
        default_action=True,
        action_name="MyEgress.add_swtrace",
        action_params={
            "swid":switch_id
        })
    ingress_sw.WriteTableEntry(table_entry)
    #print ("update %s table swtrace rule"% ingress_sw.name)    

def set_host_table(p4info_helper, switch, host):
    for i in range (len(switch)):
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=switch[i], dst_eth_addr=host[2*i]["mac"], dst_ip_addr=host[2*i]["ip"],dst_addport=32,dstport=1)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=switch[i], dst_eth_addr=host[2*i+1]["mac"], dst_ip_addr=host[2*i+1]["ip"],dst_addport=32,dstport=2)

def set_allswitch_swtrace_table(p4info_helper, switch, switch_idd , host):
    for i in range (len(switch)):
        write_swtrace_Rules(p4info_helper,ingress_sw=switch[i], switch_id =switch_idd[i] )
        wirte_drop_Rules(p4info_helper,ingress_sw=switch[i])

def set_switch_ipv4_table(p4info_helper, switch, host):
    c=[switch[0],switch[1]]
    a=[switch[2],switch[3],switch[4],switch[5]]
    e=[switch[6],switch[7],switch[8],switch[9]]
    L1=2
    L2=4
    L3=4
    #print(c)
    #print(a)
    #print(e)
    for i in range(L3):
        h =[]
        for j in range(len(host)):
            if j == 2*i or j == 2*i+1:
                k=1;
            else:
                h.append(host[j]) 
        #print(h)
        for j in range (0,3):
            write_ipv4_lpm_Rules(p4info_helper,ingress_sw=e[i], dst_eth_addr=h[2*j]["mac"], dst_ip_addr=h[2*j]["ip"],dst_addport=32,dstport=3)
            write_ipv4_lpm_Rules(p4info_helper,ingress_sw=e[i], dst_eth_addr=h[2*j+1]["mac"], dst_ip_addr=h[2*j+1]["ip"],dst_addport=32,dstport=4)
    #print(1)

        
    for i in range( 0, L2, 2 ):
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[i], dst_eth_addr=host[2*i]["dstAddr"], dst_ip_addr=host[2*i]["ip"],dst_addport=32,dstport=3)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[i], dst_eth_addr=host[2*i+1]["dstAddr"], dst_ip_addr=host[2*i+1]["ip"],dst_addport=32,dstport=3)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[i], dst_eth_addr=host[2*i+2]["dstAddr"], dst_ip_addr=host[2*i+2]["ip"],dst_addport=32,dstport=4)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[i], dst_eth_addr=host[2*i+3]["dstAddr"], dst_ip_addr=host[2*i+3]["ip"],dst_addport=32,dstport=4)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[i+1], dst_eth_addr=host[2*i]["dstAddr"], dst_ip_addr=host[2*i]["ip"],dst_addport=32,dstport=3)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[i+1], dst_eth_addr=host[2*i+1]["dstAddr"], dst_ip_addr=host[2*i+1]["ip"],dst_addport=32,dstport=3)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[i+1], dst_eth_addr=host[2*i+2]["dstAddr"], dst_ip_addr=host[2*i+2]["ip"],dst_addport=32,dstport=4)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[i+1], dst_eth_addr=host[2*i+3]["dstAddr"], dst_ip_addr=host[2*i+3]["ip"],dst_addport=32,dstport=4)
    #print(2)

    
    write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[0], dst_eth_addr=host[4]["dstAddr"], dst_ip_addr=host[4]["ip"],dst_addport=32,dstport=1)
    write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[0], dst_eth_addr=host[6]["dstAddr"], dst_ip_addr=host[6]["ip"],dst_addport=32,dstport=1)
    write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[1], dst_eth_addr=host[4]["dstAddr"], dst_ip_addr=host[4]["ip"],dst_addport=32,dstport=1)
    write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[1], dst_eth_addr=host[6]["dstAddr"], dst_ip_addr=host[6]["ip"],dst_addport=32,dstport=1)
    write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[2], dst_eth_addr=host[0]["dstAddr"], dst_ip_addr=host[0]["ip"],dst_addport=32,dstport=1)
    write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[2], dst_eth_addr=host[2]["dstAddr"], dst_ip_addr=host[2]["ip"],dst_addport=32,dstport=1)
    write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[3], dst_eth_addr=host[0]["dstAddr"], dst_ip_addr=host[0]["ip"],dst_addport=32,dstport=1)
    write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[3], dst_eth_addr=host[2]["dstAddr"], dst_ip_addr=host[2]["ip"],dst_addport=32,dstport=1)
    write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[0], dst_eth_addr=host[5]["dstAddr"], dst_ip_addr=host[5]["ip"],dst_addport=32,dstport=2)
    write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[0], dst_eth_addr=host[7]["dstAddr"], dst_ip_addr=host[7]["ip"],dst_addport=32,dstport=2)
    write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[1], dst_eth_addr=host[5]["dstAddr"], dst_ip_addr=host[5]["ip"],dst_addport=32,dstport=2)
    write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[1], dst_eth_addr=host[7]["dstAddr"], dst_ip_addr=host[7]["ip"],dst_addport=32,dstport=2)
    write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[2], dst_eth_addr=host[1]["dstAddr"], dst_ip_addr=host[1]["ip"],dst_addport=32,dstport=2)
    write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[2], dst_eth_addr=host[3]["dstAddr"], dst_ip_addr=host[3]["ip"],dst_addport=32,dstport=2)
    write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[3], dst_eth_addr=host[1]["dstAddr"], dst_ip_addr=host[1]["ip"],dst_addport=32,dstport=2)
    write_ipv4_lpm_Rules(p4info_helper,ingress_sw=a[3], dst_eth_addr=host[3]["dstAddr"], dst_ip_addr=host[3]["ip"],dst_addport=32,dstport=2)     
    #print(3)

    for i in range(L1):
        for j in range (0,4):
            write_ipv4_lpm_Rules(p4info_helper,ingress_sw=c[i], dst_eth_addr=host[2*j]["mac"], dst_ip_addr=host[2*j]["ip"],dst_addport=32,dstport=j+1)
            write_ipv4_lpm_Rules(p4info_helper,ingress_sw=c[i], dst_eth_addr=host[2*j+1]["mac"], dst_ip_addr=host[2*j+1]["ip"],dst_addport=32,dstport=j+1) 
    #print(4)    
    
def set_short_rule(p4info_helper,p,switch,host_source ,host_target):
    path_switch_id=[]
    switch_port=[]
    for i in range (1, len(p)-1):
        #path_switch_id.append(str(p[i])[0])
        #switch_port.append(str(p[i])[0])
        if p[i] == "sw10-1" or p[i] == "sw10-2" or  p[i] == "sw10-3" or  p[i] == "sw10-4":
            path_switch_id.append(10)
            switch_port.append(int(str(p[i])[5]))
        else :
            path_switch_id.append(int(str(p[i])[2]))
            switch_port.append(int(str(p[i])[4]))
    #print(path_switch_id)
    #print(switch_port)
    
    for i in range (0,len(path_switch_id),2):
        if i == 0 :
            write_ipv4_lpm_Rules(p4info_helper,ingress_sw=switch[path_switch_id[i]-1], dst_eth_addr=host_target["mac"], dst_ip_addr=host_target["ip"],dst_addport=32,dstport=switch_port[i+1])
        elif i == len(path_switch_id) - 2:
            write_ipv4_lpm_Rules(p4info_helper,ingress_sw=switch[path_switch_id[i]-1], dst_eth_addr=host_source["mac"], dst_ip_addr=host_source["ip"],dst_addport=32,dstport=switch_port[i])
        else :
            write_ipv4_lpm_Rules(p4info_helper,ingress_sw=switch[path_switch_id[i]-1], dst_eth_addr=host_source["mac"], dst_ip_addr=host_source["ip"],dst_addport=32,dstport=switch_port[i])
            write_ipv4_lpm_Rules(p4info_helper,ingress_sw=switch[path_switch_id[i]-1], dst_eth_addr=host_target["mac"], dst_ip_addr=host_target["ip"],dst_addport=32,dstport=switch_port[i+1]) 
             
         
        
        

    
                
          
        
             
          
     
#if __name__ == '__main__':
#     h=get_host()
#     print(h)         
