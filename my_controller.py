#!/usr/bin/env python2
import argparse
import grpc
import os
import sys
import json
import networkx as nx
import matplotlib.pyplot as plt
from time import sleep
import datetime

import set_rule
import short_path
# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))
import p4runtime_lib.bmv2
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.helper



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

def host_input():
    print("source host for shortest forwarding: ")
    source=input()
    print("source host for shortest forwarding: ")
    target=input()
    host = [source,target]
    return (host)
    
def main(p4info_file_path, bmv2_file_path):
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
        s5 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s5',
            address='127.0.0.1:50055',
            device_id=4,
            proto_dump_file='logs/s5-p4runtime-requests.txt')
        s6 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s6',
            address='127.0.0.1:50056',
            device_id=5,
            proto_dump_file='logs/s6-p4runtime-requests.txt')
        s7 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s7',
            address='127.0.0.1:50057',
            device_id=6,
            proto_dump_file='logs/s7-p4runtime-requests.txt')
        s8 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s8',
            address='127.0.0.1:50058',
            device_id=7,
            proto_dump_file='logs/s8-p4runtime-requests.txt')
        s9 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s9',
            address='127.0.0.1:50059',
            device_id=8,
            proto_dump_file='logs/s9-p4runtime-requests.txt')
        s10 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s10',
            address='127.0.0.1:50060',
            device_id=9,
            proto_dump_file='logs/s10-p4runtime-requests.txt')
        
        s1.MasterArbitrationUpdate()
        s2.MasterArbitrationUpdate()
        s3.MasterArbitrationUpdate()
        s4.MasterArbitrationUpdate()
        s5.MasterArbitrationUpdate()
        s6.MasterArbitrationUpdate()
        s7.MasterArbitrationUpdate()
        s8.MasterArbitrationUpdate()
        s9.MasterArbitrationUpdate()
        s10.MasterArbitrationUpdate()
        

        # Install the P4 program on the switches
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s1")
        s2.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s2")
        s3.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s3") 
        s4.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                     bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s4")
        s5.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s5")
        s6.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s6")
        s7.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s7") 
        s8.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                     bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s8")
        s9.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s9")
        s10.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s10")
        switch=[s1,s2,s3,s4,s5,s6,s7,s8,s9,s10]
        host=set_rule.get_host()
        switch_e=[s7,s8,s9,s10]

        set_rule.set_host_table(p4info_helper, switch_e, host)
        
        switch_idd=[1,2,3,4,5,6,7,8,9,10]

        set_rule.set_allswitch_swtrace_table(p4info_helper, switch, switch_idd , host)

        set_rule.set_switch_ipv4_table(p4info_helper, switch, host)
        print("++++++++++++++++++++++++++++++++++")
        print("                                  ")
        print("-----------------OK---------------")
        print("                                  ")
        print("++++++++++++++++++++++++++++++++++")
        

    except KeyboardInterrupt:
        print (" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

def short_update(p4info_file_path, bmv2_file_path,path,host_source,host_target):
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
        s5 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s5',
            address='127.0.0.1:50055',
            device_id=4,
            proto_dump_file='logs/s5-p4runtime-requests.txt')
        s6 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s6',
            address='127.0.0.1:50056',
            device_id=5,
            proto_dump_file='logs/s6-p4runtime-requests.txt')
        s7 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s7',
            address='127.0.0.1:50057',
            device_id=6,
            proto_dump_file='logs/s7-p4runtime-requests.txt')
        s8 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s8',
            address='127.0.0.1:50058',
            device_id=7,
            proto_dump_file='logs/s8-p4runtime-requests.txt')
        s9 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s9',
            address='127.0.0.1:50059',
            device_id=8,
            proto_dump_file='logs/s9-p4runtime-requests.txt')
        s10 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s10',
            address='127.0.0.1:50060',
            device_id=9,
            proto_dump_file='logs/s10-p4runtime-requests.txt')
        
        s1.MasterArbitrationUpdate()
        s2.MasterArbitrationUpdate()
        s3.MasterArbitrationUpdate()
        s4.MasterArbitrationUpdate()
        s5.MasterArbitrationUpdate()
        s6.MasterArbitrationUpdate()
        s7.MasterArbitrationUpdate()
        s8.MasterArbitrationUpdate()
        s9.MasterArbitrationUpdate()
        s10.MasterArbitrationUpdate()
        

        # Install the P4 program on the switches
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s1")
        s2.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s2")
        s3.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s3") 
        s4.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                     bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s4")
        s5.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s5")
        s6.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s6")
        s7.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s7") 
        s8.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                     bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s8")
        s9.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s9")
        s10.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        #print ("Installed P4 Program using SetForwardingPipelineConfig on s10")
        
        switch=[s1,s2,s3,s4,s5,s6,s7,s8,s9,s10]
        host=set_rule.get_host()
        switch_e=[s7,s8,s9,s10]
        set_rule.set_host_table(p4info_helper, switch_e, host)
        switch_idd=[1,2,3,4,5,6,7,8,9,10]
        set_rule.set_allswitch_swtrace_table(p4info_helper, switch, switch_idd , host)

        
        #[host_source,host_target]=host_input()
        #p = short_path.shortest_routing_path(host_source ,host_target)
        #print("++++++++++++++++++++++++++++++++++")
        #print("                                  ")
        #print(p)
        #print("                                  ")
        #print("++++++++++++++++++++++++++++++++++")
       
        h_source=host[int(str(host_source)[1])-1]
        h_target=host[int(str(host_target)[1])-1]
        set_rule.set_short_rule(p4info_helper,path,switch,h_source ,h_target)
        print(" Finsh changing")
        print("++++++++++++++++++++++++++++++++++")
        print(path)
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
    main(args.p4info, args.bmv2_json)
    print(1)
    a = input()
    #sleep(80)

    T = 10
    host_source="h1"
    host_target="h8"
    p = short_path.shortest_routing_path(host_source ,host_target)
    path_1 = p
    short_update(args.p4info, args.bmv2_json,p,host_source,host_target)
    old_delay = short_path.get_delay(p)
    print(" Now delay is {}".format(old_delay))
    #b=input()
    now_delay = 0
    new_delay = 0
    sleep(1)
    print(" start to update min-delay routing ")
    next = 1
    while next != 1000:
        '''
        nowtime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        print("Nowtime is |{}|".format(nowtime))
        now_delay = short_path.get_delay(path_1)
        print ("Now delay is {}".format(old_delay))
        if old_delay - now_delay > T :
            path_2 = short_path.shortest_routing_path(host_source ,host_target)
            new_delay = short_path.get_delay(path_2)
            print ("New delay is {}".format(new_delay))
            old_delay = now_delay
            if now_delay - new_delay > T:
               print ("Need to change")
               short_update(args.p4info, args.bmv2_json,path_2,host_source,host_target)
               old_delay = new_delay
               path_1 = path_2
        else :
            print ("Don't need to change")
        '''
        path_2 = short_path.shortest_routing_path(host_source ,host_target)
        short_update(args.p4info, args.bmv2_json,path_2,host_source,host_target)
        print("------------------------------")
        print("------------------------------")
        sleep(5)
        print("restore")
        main(args.p4info, args.bmv2_json)
        sleep(5)
        next = next+1
        
    
    
    
