# P4-INT-graduation-program
基于带内网络遥测的时延最优路由研究，系统方案不算完善仅供参考.
## 文件说明
|文件|用途|
|-|-|
|文件夹 data|存储数据|
|文件夹 p4runtime_lib|p4runtime的python库|
|文件夹 pod-topo|      静态路由的规则文件.json|
|genrate_fattree.py|    用于生成网络拓扑文件（json文件）|
|get_delays.py|         用于汇总data中的switch延迟数据|
|my_controller.py|      自定义控制器|
|networkflow.p4|       p4文件|
|random_send.py|       随机发送探测包|
|switch_monitor.py|     接收探测包并记录|
|send.py     |         发送探测包|
|receive.py |           接收探测包|
|set_rule.py|           控制器设置转发规则库文件|
|short_path.py|        控制器最短路由计算库文件|
|topology.json|       fattree网络拓扑，由genrate_ffattree.py文件自动生成|
## 如果自己装P4的环境装不上！
如果自己装环境装不上，可以直接用这个ova！（这个是原版，自己用要调试的）。里面的库是18年的很多已经更新，而且python是2.7的。可能会有许多的因为库过于老而造成的bug需要自己慢慢搞。建议和[P4官方教程](https://github.com/p4lang/tutorials)对比着看.
* ova文件[百度网盘](https://pan.baidu.com/s/1JqdUowYRNH-mUD88AqWRDA?pwd=u647)提取码：u647
