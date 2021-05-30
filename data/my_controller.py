#!/usr/bin/env python2
import argparse
import grpc
import os
import sys
import json
import networkx as nx
import matplotlib.pyplot as plt
from time import sleep

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))
import p4runtime_lib.bmv2
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.helper

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
    print ("update %s table ipv4 rule"% ingress_sw.name)
def wirte_drop_Rules(p4info_helper,ingress_sw):
    # 2)drop rule
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm",
        default_action=True,
        action_name="MyIngress.drop",
        action_params={
        })
    ingress_sw.WriteTableEntry(table_entry)
    print ("update %s table drop rule" % ingress_sw.name)
def write_set_swid_Rules(p4info_helper,ingress_sw, switch_id):
    
    # 3)Egress Rule
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyEgress.swid",
        default_action=True,
        action_name="MyEgress.set_swid",
        action_params={
            "swid":switch_id
        })
    ingress_sw.WriteTableEntry(table_entry)
    print ("update %s table set_swid rule"% ingress_sw.name)

def write_swtrace_Rules(p4info_helper,ingress_sw, switch_id):
    
    # 3)Egress Rule
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyEgress.swtrace",
        default_action=True,
        action_name="MyEgress.add_swtrace",
        action_params={
            "swidid":switch_id
        })
    ingress_sw.WriteTableEntry(table_entry)
    print ("update %s table swtrace rule"% ingress_sw.name)    

def readTableRules(p4info_helper, sw):
    """
    Reads the table entries from all tables on the switch.

    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    """
    print ('\n----- Reading tables rules for %s -----' % sw.name)
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry
            # TODO For extra credit, you can use the p4info_helper to translate
            #      the IDs in the entry to names
            table_name = p4info_helper.get_tables_name(entry.table_id)
            print ('%s: ' % table_name),
            for m in entry.match:
                print (p4info_helper.get_match_field_name(table_name, m.field_id)),
                print ('%r' % (p4info_helper.get_match_field_value(m),)),
            action = entry.action.action
            action_name = p4info_helper.get_actions_name(action.action_id)
            print ('->', action_name),
            for p in action.params:
                print (p4info_helper.get_action_param_name(action_name, p.param_id)),
                print ('%r' % p.value),
            print

def printGrpcError(e):
    print ("gRPC Error:", e.details()),
    status_code = e.code()
    print ("(%s)" % status_code.name),
    traceback = sys.exc_info()[2]
    print ("[%s:%d]" % (traceback.tb_frame.f_code.co_filename, traceback.tb_lineno))

def short_path(switch_source,switch_target):
    hop_delay=[]
    nodes=[]
    a=[]
    b=[]
    with open("data/getINTreport") as fp:
         stats=json.load(fp)
    a.append(stats["path"])
    nodes=a[0]
    b.append(stats["hop_delays"])
    hop_delay=b[0]
    nodes_id=list(set(nodes))
    switch={}
    G = nx.Graph()
    for i in range (0,len(nodes_id)):
         for j in range (0,len(nodes)):
             if nodes_id[i] == nodes[j]:
                switch[i+1]=[nodes_id[i],hop_delay[j]]
         s_node1='%s-1' % switch[i+1][0]
         s_node2='%s-2' % switch[i+1][0]
         s_node3='%s-3' % switch[i+1][0]
         G.add_node(s_node1)
         G.add_node(s_node2)
         G.add_node(s_node3)
         G.add_weighted_edges_from([(s_node1,s_node2,switch[i+1][1]),(s_node2,s_node3,switch[i+1][1]),(s_node3,s_node1,switch[i+1][1])])
    start_node=nodes[0]
    cnt=1
    cnt2=0
    while cnt != 0:
         if nodes[cnt] != start_node:
             s_3 = '%s-3' % nodes[cnt-1]
             
             s_next_2 = '%s-2' % nodes[cnt]
             
             G.add_weighted_edges_from([(s_3,s_next_2,1)])
             cnt = cnt+1
             cnt2 = cnt
         else:
             cnt = 0
    G.add_weighted_edges_from([('%s-3' % nodes[cnt2-1],'%s-2' % nodes[cnt2],1)])
    
    p=nx.shortest_path(G, source='%s-1' %switch_source , target='%s-1'%switch_target,weight='weight')
    #print(p)
    #print(str(p[0])[0])
    path_switch_id=[]
    for i in range (0, len(p)):
        path_switch_id.append(int(str(p[i])[0]))
    for n in path_switch_id:
            if path_switch_id.count(n) > 1:
                path_switch_id.remove(n)
    return path_switch_id


def setoldtable(p4info_file_path, bmv2_file_path):
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    try:
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
            proto_dump_file='logs/s1-p4runtime-requests.txt')
        s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s2',
            address='127.0.0.1:50052',
            device_id=1,
            proto_dump_file='logs/s2-p4runtime-requests.txt')
        s3 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s3',
            address='127.0.0.1:50053',
            device_id=2,
            proto_dump_file='logs/s3-p4runtime-requests.txt')
        s4 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s4',
            address='127.0.0.1:50054',
            device_id=3,
            proto_dump_file='logs/s4-p4runtime-requests.txt')
        

        s1.MasterArbitrationUpdate()
        s2.MasterArbitrationUpdate()
        s3.MasterArbitrationUpdate()
        s4.MasterArbitrationUpdate()
        

        # Install the P4 program on the switches
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print ("Installed P4 Program using SetForwardingPipelineConfig on s1")
        s2.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print ("Installed P4 Program using SetForwardingPipelineConfig on s2")
        s3.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print ("Installed P4 Program using SetForwardingPipelineConfig on s3") 
        s4.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                     bmv2_json_file_path=bmv2_file_path)
        print ("Installed P4 Program using SetForwardingPipelineConfig on s4")
        
        #s1 table
        write_set_swid_Rules(p4info_helper,ingress_sw=s1, switch_id=1)
        write_swtrace_Rules(p4info_helper,ingress_sw=s1, switch_id=1)
        wirte_drop_Rules(p4info_helper,ingress_sw=s1)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s1, dst_eth_addr="08:00:00:00:01:11", dst_ip_addr="10.0.1.1",dst_addport=32,dstport=1)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s1, dst_eth_addr="08:00:00:00:02:22", dst_ip_addr="10.0.2.2",dst_addport=32,dstport=2)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s1, dst_eth_addr="08:00:00:00:03:00", dst_ip_addr="10.0.3.3",dst_addport=32,dstport=3)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s1, dst_eth_addr="08:00:00:00:04:00", dst_ip_addr="10.0.4.4",dst_addport=32,dstport=4)
        #s2 table
        write_set_swid_Rules(p4info_helper,ingress_sw=s2, switch_id=2)
        write_swtrace_Rules(p4info_helper,ingress_sw=s2, switch_id=2)
        wirte_drop_Rules(p4info_helper,ingress_sw=s2)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s2, dst_eth_addr="08:00:00:00:03:00", dst_ip_addr="10.0.1.1",dst_addport=32,dstport=4)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s2, dst_eth_addr="08:00:00:00:04:00", dst_ip_addr="10.0.2.2",dst_addport=32,dstport=3)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s2, dst_eth_addr="08:00:00:00:03:33", dst_ip_addr="10.0.3.3",dst_addport=32,dstport=1)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s2, dst_eth_addr="08:00:00:00:04:44", dst_ip_addr="10.0.4.4",dst_addport=32,dstport=2)
        #s3 table
        write_set_swid_Rules(p4info_helper,ingress_sw=s3, switch_id=3)
        write_swtrace_Rules(p4info_helper,ingress_sw=s3, switch_id=3)
        wirte_drop_Rules(p4info_helper,ingress_sw=s3)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s3, dst_eth_addr="08:00:00:00:01:00", dst_ip_addr="10.0.1.1",dst_addport=32,dstport=1)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s3, dst_eth_addr="08:00:00:00:01:00", dst_ip_addr="10.0.2.2",dst_addport=32,dstport=1)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s3, dst_eth_addr="08:00:00:00:02:00", dst_ip_addr="10.0.3.3",dst_addport=32,dstport=2)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s3, dst_eth_addr="08:00:00:00:02:00", dst_ip_addr="10.0.4.4",dst_addport=32,dstport=2)
        #s4 table
        write_set_swid_Rules(p4info_helper,ingress_sw=s4, switch_id=4)
        write_swtrace_Rules(p4info_helper,ingress_sw=s4, switch_id=4)
        wirte_drop_Rules(p4info_helper,ingress_sw=s4)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s4, dst_eth_addr="08:00:00:00:01:00", dst_ip_addr="10.0.1.1",dst_addport=32,dstport=2)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s4, dst_eth_addr="08:00:00:00:01:00", dst_ip_addr="10.0.2.2",dst_addport=32,dstport=2)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s4, dst_eth_addr="08:00:00:00:02:00", dst_ip_addr="10.0.3.3",dst_addport=32,dstport=1)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s4, dst_eth_addr="08:00:00:00:02:00", dst_ip_addr="10.0.4.4",dst_addport=32,dstport=1)
        
        
        readTableRules(p4info_helper, s1)
        readTableRules(p4info_helper, s2)
        readTableRules(p4info_helper, s3)
        readTableRules(p4info_helper, s4) 


    except KeyboardInterrupt:
        print (" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

def host_input():
    switch_source=0
    switch_target=0
    print("source host for shortest forwarding: ")
    source=input() #add ""
    if source == "h1":
       switch_source = 1
    elif source == "h2":
       switch_source = 1
    elif source == "h3":
       switch_source = 2
    elif source == "h4":
       switch_source = 2     
    print("source host for shortest forwarding: ")
    target=input() #add ""
    if target == "h1":
       switch_target = 1
    elif target == "h2":
       switch_target = 1
    elif target == "h3":
       switch_target = 2
    elif target == "h4":
       switch_target = 2
    switch=[switch_source,switch_target ]
    return switch

def set_shortest_path(p4info_file_path, bmv2_file_path, switch_id):
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)
    
    try:
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
            proto_dump_file='logs/s1-p4runtime-requests.txt')
        s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s2',
            address='127.0.0.1:50052',
            device_id=1,
            proto_dump_file='logs/s2-p4runtime-requests.txt')
        s3 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s3',
            address='127.0.0.1:50053',
            device_id=2,
            proto_dump_file='logs/s3-p4runtime-requests.txt')
        s4 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s4',
            address='127.0.0.1:50054',
            device_id=3,
            proto_dump_file='logs/s4-p4runtime-requests.txt')
        

        s1.MasterArbitrationUpdate()
        s2.MasterArbitrationUpdate()
        s3.MasterArbitrationUpdate()
        s4.MasterArbitrationUpdate()
        

        # Install the P4 program on the switches
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print ("Installed P4 Program using SetForwardingPipelineConfig on s1")
        s2.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print ("Installed P4 Program using SetForwardingPipelineConfig on s2")
        s3.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print ("Installed P4 Program using SetForwardingPipelineConfig on s3") 
        s4.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                     bmv2_json_file_path=bmv2_file_path)
        print ("Installed P4 Program using SetForwardingPipelineConfig on s4")
        
        # s1 s2 s3 s4 basic rules
        write_set_swid_Rules(p4info_helper,ingress_sw=s1, switch_id=1)
        wirte_drop_Rules(p4info_helper,ingress_sw=s1)
        write_set_swid_Rules(p4info_helper,ingress_sw=s2, switch_id=2)
        wirte_drop_Rules(p4info_helper,ingress_sw=s2)
        write_set_swid_Rules(p4info_helper,ingress_sw=s3, switch_id=3)
        wirte_drop_Rules(p4info_helper,ingress_sw=s3)
        write_set_swid_Rules(p4info_helper,ingress_sw=s4, switch_id=4)
        wirte_drop_Rules(p4info_helper,ingress_sw=s4)
        
        write_swtrace_Rules(p4info_helper,ingress_sw=s1, switch_id=1)
        write_swtrace_Rules(p4info_helper,ingress_sw=s2, switch_id=2)
        write_swtrace_Rules(p4info_helper,ingress_sw=s3, switch_id=3)
        write_swtrace_Rules(p4info_helper,ingress_sw=s4, switch_id=4)


        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s1, dst_eth_addr="08:00:00:00:01:11", dst_ip_addr="10.0.1.1",dst_addport=32,dstport=1)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s1, dst_eth_addr="08:00:00:00:02:22", dst_ip_addr="10.0.2.2",dst_addport=32,dstport=2)
        
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s2, dst_eth_addr="08:00:00:00:03:33", dst_ip_addr="10.0.3.3",dst_addport=32,dstport=1)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s2, dst_eth_addr="08:00:00:00:04:44", dst_ip_addr="10.0.4.4",dst_addport=32,dstport=2)
        
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s3, dst_eth_addr="08:00:00:00:01:00", dst_ip_addr="10.0.1.1",dst_addport=32,dstport=1)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s3, dst_eth_addr="08:00:00:00:01:00", dst_ip_addr="10.0.2.2",dst_addport=32,dstport=1)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s3, dst_eth_addr="08:00:00:00:02:00", dst_ip_addr="10.0.3.3",dst_addport=32,dstport=2)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s3, dst_eth_addr="08:00:00:00:02:00", dst_ip_addr="10.0.4.4",dst_addport=32,dstport=2)
        
        write_set_swid_Rules(p4info_helper,ingress_sw=s4, switch_id=4)
        wirte_drop_Rules(p4info_helper,ingress_sw=s4)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s4, dst_eth_addr="08:00:00:00:01:00", dst_ip_addr="10.0.1.1",dst_addport=32,dstport=2)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s4, dst_eth_addr="08:00:00:00:01:00", dst_ip_addr="10.0.2.2",dst_addport=32,dstport=2)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s4, dst_eth_addr="08:00:00:00:02:00", dst_ip_addr="10.0.3.3",dst_addport=32,dstport=1)
        write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s4, dst_eth_addr="08:00:00:00:02:00", dst_ip_addr="10.0.4.4",dst_addport=32,dstport=1)
        # set_short_path
        if switch_id[1] == 3:
               write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s1, dst_eth_addr="08:00:00:00:03:00", dst_ip_addr="10.0.3.3",dst_addport=32,dstport=3)
               write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s1, dst_eth_addr="08:00:00:00:03:00", dst_ip_addr="10.0.4.4",dst_addport=32,dstport=3)
               write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s2, dst_eth_addr="08:00:00:00:04:00", dst_ip_addr="10.0.1.1",dst_addport=32,dstport=4)
               write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s2, dst_eth_addr="08:00:00:00:04:00", dst_ip_addr="10.0.2.2",dst_addport=32,dstport=4)
        elif switch_id[1] == 4:
               write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s1, dst_eth_addr="08:00:00:00:04:00", dst_ip_addr="10.0.3.3",dst_addport=32,dstport=4)
               write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s1, dst_eth_addr="08:00:00:00:04:00", dst_ip_addr="10.0.4.4",dst_addport=32,dstport=4)
               write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s2, dst_eth_addr="08:00:00:00:03:00", dst_ip_addr="10.0.1.1",dst_addport=32,dstport=3)
               write_ipv4_lpm_Rules(p4info_helper,ingress_sw=s2, dst_eth_addr="08:00:00:00:03:00", dst_ip_addr="10.0.2.2",dst_addport=32,dstport=3)

        readTableRules(p4info_helper, s1)
        readTableRules(p4info_helper, s2)
        readTableRules(p4info_helper, s3)
        readTableRules(p4info_helper, s4) 

        print("++++++++++++++++++++++++++++++++++")
        print("                                  ")
        print(" set router for s%s--s%s--s%s     "% (switch_id[0],switch_id[1],switch_id[2]))
        print("                                  ")
        print("++++++++++++++++++++++++++++++++++")

    except KeyboardInterrupt:
        print (" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()
       

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/networkflow.p4info')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/networkflow.json')
    args = parser.parse_args()
   
    if not os.path.exists(args.p4info):
        parser.print_help()
        print ("\np4info file not found: %s\nHave you run 'make'?" % args.p4info)
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print ("\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json)
        parser.exit(1)

    setoldtable(args.p4info, args.bmv2_json)
    
    [switch_source,switch_target]=host_input()
    switch_id = short_path(switch_source,switch_target)
    set_shortest_path(args.p4info, args.bmv2_json,switch_id)
    
    
