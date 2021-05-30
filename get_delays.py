import json
import time

statstime =[0,0,0,0]
hop_stats={"sw1":[],"sw2":[],"sw3":[],"sw4":[],"sw5":[],"sw6":[],"sw7":[],"sw8":[],"sw9":[],"sw10":[]}
def get_delay():
    cnt=0
    #with open("data/delay_all") as fp:
     #    hop_stats = json.load(fp)
    for i in range (7,11):
         with open ("data/INTreport_sw%s"% i) as fp:
              stats=json.load(fp)     
         if stats["time"] != statstime[cnt]:
              hop=stats["path"]
              hop_delay=stats["hop_delays"]
              cnt=cnt+1
              for j in range(len(hop)):
                 for i in range (0,10):
                      if hop[j] == i+1 :
                         hop_stats["sw{}".format(i+1)]=hop_delay[j]
         #return  hop_stats
         

if __name__=="__main__":
    while True:
        try:
            for i in range (0,5000):
                get_delay()
                with open("data/delay_all", 'w') as fp:
                     json.dump(hop_stats, fp,  ensure_ascii=False, sort_keys=False)
                print("finish update all delay %s" % i)
                time.sleep(1)            
        except Exception as e:
            print(e)
            break

