#!/usr/bin/env python2
import argparse
import grpc
import os
import sys
import json
import networkx as nx
import matplotlib.pyplot as plt
from time import sleep

import set_rule
# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))
import p4runtime_lib.bmv2
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.helper

def load():
    with open("data/delay_all") as fp:
        return(json.load(fp))

def get_Graph( switch ):
    G = nx.Graph()
    for i in range (0,10):
        s_node1 = 'sw{}-{}'.format(i+1,1)
        s_node2 = 'sw{}-{}'.format(i+1,2)
        s_node3 = 'sw{}-{}'.format(i+1,3)
        s_node4 = 'sw{}-{}'.format(i+1,4)
        G.add_node(s_node1)
        G.add_node(s_node2)
        G.add_node(s_node3)
        G.add_node(s_node4)
        weight =switch["sw{}".format(i+1)]
        #print(weight)
        G.add_weighted_edges_from([(s_node1,s_node2,weight),(s_node1,s_node3,weight),(s_node1,s_node4,weight),(s_node2,s_node3,weight),(s_node2,s_node4,weight),(s_node3,s_node4,weight)])
    
    L1 = 2
    L2 = L1 * 2 
    L3 = L2
    c = []
    a = []
    e = []
    
    # add core ovs  
    for i in range( L1 ):
        sw = 'sw{}'.format(i + 1)
        c.append( sw )
    
    # add aggregation ovs
    for i in range( L2 ):
        sw = 'sw{}'.format(L1 + i + 1)
        a.append( sw )
    
    # add edge ovs
    for i in range( L3 ):
        sw = 'sw{}'.format(L1 + L2 + i + 1) 
        e.append( sw )
    # c
    for i in range (L1):
        sw1 = c[i]
        for j in range(L2):
           sw2 = a[j]
           #print(sw2)
           #print("{}-p{}".format(sw1,j+1),"{}-p{}".format(sw2,i+1))
           #link.append(["{}-p{}".format(sw1,j+1),"{}-p{}".format(sw2,i+1)])
           G.add_edge("{}-{}".format(sw1,j+1),"{}-{}".format(sw2,i+1))
    for i in range( 0, L2, 2 ):
         #print(i)
         cnt=3
         for sw1 in a[i:i+2]:
            num = 0
            for sw2 in e[i:i+2]:
               #print(sw1,sw2)
               #print(cnt,num)
               #print("{}-p{}".format(sw1, num+3),"{}-p{}".format(sw2,cnt))
	       #link.append(["{}-p{}".format(sw1, num+3),"{}-p{}".format(sw2,cnt)])
               G.add_edge("{}-{}".format(sw1, num+3),"{}-{}".format(sw2,cnt))
               num = num+1
            cnt = cnt + 1
    count = 1
    for sw1 in e:
          for i in range(2):
              #print("{}-p{}".format(sw1,i+1), "h{}".format( count ))
              #link.append(["{}-p{}".format(sw1,i+1), "h{}".format( count )])
              G.add_node('h{}'.format( count ))
              G.add_edge("{}-{}".format(sw1,i+1),"h{}".format(count))
              count += 1

    return (G)

def shortest_routing_path(host_source ,host_target):
    switch = load()
    G = get_Graph( switch )
    p = nx.shortest_path(G, source='%s' %host_source , target='%s'%host_target,weight='weight')
    #print(p)
    
    #nx.draw(G)
    #plt.savefig("topo.png")
    #plt.show()
    return p
def shortest_routing_path_length(host_source ,host_target):
    switch = load()
    G = get_Graph( switch )
    pa = nx.shortest_path(G, source='%s' %host_source , target='%s'%host_target,weight='weight')
    p = nx.shortest_path_length(G, source='%s' %host_source , target='%s'%host_target,weight='weight')
    p = p - ( len(pa)-2)/2 
    #print(p)
    
    #nx.draw(G)
    #plt.savefig("topo.png")
    #plt.show()
    return p


def get_delay(p):
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
    switch = load()
    delay = 0
    for sw in path_switch_id :
        delay += switch["sw{}".format(sw)]
    return delay
     


#if __name__ == "__main__":
 #   switch = load()
  #  #print(switch["sw10"])
   # pa=shortest_routing_path("h1","h8")
    #print(pa)
    #print(len(pa)-2)
    #p=shortest_routing_path_length("h1","h8")
    #print(p)
    #set_short_rule(p)    
            
    

    
