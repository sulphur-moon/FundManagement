from fundinfo import FundInfo
import matplotlib.pyplot as plt
import time
import datetime


fund_info = FundInfo()
fund_list = fund_info.get_list()
myfund_object = fund_info.get_fundinfo('005918')
net_worthtrend = myfund_object.eval('Data_netWorthTrend')
x = [datetime.datetime.fromtimestamp(int(o['x'])//1000) for o in net_worthtrend]
y1 = [o['y'] for o in net_worthtrend]
ac_worthtrend = myfund_object.eval('Data_ACWorthTrend')
y2 = [e[1]-0.1 for e in ac_worthtrend]
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
plt.plot(x, y1, color='b', label='net')
plt.plot(x, y2, color='r', label='ac')
plt.gcf().autofmt_xdate()
plt.legend()
plt.show()
