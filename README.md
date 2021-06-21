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
