import matplotlib.pyplot as plt
import csv
from datetime import datetime

outtime1 = []
fd = open('b5.csv', 'r')
reader1 = csv.reader(fd)
for row in reader1:
    outtime1.append(row)
outtime2 = []
fc = open('tb5.csv', 'r')
reader2 = csv.reader(fc)
for row in reader2:
    outtime2.append(row)
outtime3 = []
fc = open('tb10.csv', 'r')
reader3 = csv.reader(fc)
for row in reader3:
    outtime3.append(row)

delays3=[]
delays1=[]
delays2=[]
for i in range(len(outtime3)):
    delays1.append(float(outtime1[i][0]))
    delays2.append(float(outtime2[i][0]))
    delays3.append(float(outtime3[i][0]))

c = list(range(1,len(outtime3)+1))
#print(delays)

plt.figure(1)
plt.plot( c ,delays1, 'ro-', color='r', alpha=0.8, linewidth=1)
plt.plot( c ,delays2, '--', color='b', alpha=0.8, linewidth=1)
plt.plot( c ,delays3, '--', color='g', alpha=0.8, linewidth=1)
#plt.plot( c ,delays)
#plt.ylim(0, 200)
plt.title("Simple Plot")
plt.show()

