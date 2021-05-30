import json

K=3
host={"h1":[],"h2":[],"h3":[],"h4":[],"h5":[],"h6":[],"h7":[],"h8":[]}

link=[]
host_cnt=8
for i in range (0, host_cnt):
#      host[i]={"h{}".format(i+1):{"ip":"10.0.{}.{}/24".format(i+1,i+1),
#                                "mac":"08:00:00:00:0{}:{}{}".format(i+1,i+1,i+1),
#                                 "commands":["route add default gw 10.0.{}.{}0 dev eth0".format(i+1,i+1)
#                                             "arp -i eth0 -s 10.0.{}.{}0 08:00:00:00:0{}:00".format(i+1,i+1,i+1)]
#                                }
#               }
       host["h{}".format(i+1)]={"ip":[],"mac":[],"commands":[]}      
       host["h{}".format(i+1)]["ip"]="10.0.{}.{}/24".format(i+1,i+1)
       host["h{}".format(i+1)]["mac"]="08:00:00:00:0{}:{}{}".format(i+1,i+1,i+1)
       host["h{}".format(i+1)]["commands"]=["route add default gw 10.0.{}.{}0 dev eth0".format(i+1,i+1),
                                            "arp -i eth0 -s 10.0.{}.{}0 08:00:00:00:0{}:00".format(i+1,i+1,i+1)]
switch={"s1":{},"s2":{},"s3":{},"s4":{},"s5":{},"s6":{},"s7":{},"s8":{},"s9":{},"s10":{}}
L1 = 2
L2 = L1 * 2 
L3 = L2
c = []
a = []
e = []
          
# add core ovs  
for i in range( L1 ):
     sw = 's{}'.format(i + 1)
     c.append( sw )
    
# add aggregation ovs
for i in range( L2 ):
     sw = 's{}'.format(L1 + i + 1)
     a.append( sw )
    
# add edge ovs
for i in range( L3 ):
     sw = 's{}'.format(L1 + L2 + i + 1) 
     e.append( sw )
for i in range( L1 ):
     sw1 = c[i]
     for j in range(L2):
         sw2 = a[j]
         #print(sw2)
         #print("{}-p{}".format(sw1,j+1),"{}-p{}".format(sw2,i+1))
         link.append(["{}-p{}".format(sw1,j+1),"{}-p{}".format(sw2,i+1),"0",200])
for i in range( 0, L2, 2 ):
      #print(i)
      cnt=3
      for sw1 in a[i:i+2]:
          num = 0
          for sw2 in e[i:i+2]:
             #print(sw1,sw2)
             #print(cnt,num)
             #print("{}-p{}".format(sw1, num+3),"{}-p{}".format(sw2,cnt))
	     link.append(["{}-p{}".format(sw1, num+3),"{}-p{}".format(sw2,cnt),"0",200])
             num = num+1
          cnt= cnt + 1
count = 1
for sw1 in e:
      for i in range(2):
           #print("{}-p{}".format(sw1,i+1), "h{}".format( count ))
           link.append(["{}-p{}".format(sw1,i+1), "h{}".format( count ),"0",200])
           count += 1

topo={"hosts":host,"switches":switch,"links":link}
with open("topology.json",'w') as fp:
     json.dump(topo, fp,  ensure_ascii=False, sort_keys=False)


