import tkinter
from tkinter import messagebox, ttk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import time
import datetime
from fundinfo import FundInfo


# 曲线绘制颜色列表
color_list = ['k', 'r', 'orange', 'g', 'b', 'silver', 'purple', 'yellow', 'lime', 'cyan']
# 曲线绘制X轴和Y轴数据
X = []
Y = []

# 创建tkinter的主窗口
mainwindow = tkinter.Tk()
mainwindow.title("基金查询工具V0.1")
mainwindow.geometry("800x600+50+50")
mainwindow.resizable(0, 0)

# 曲线图
f = plt.figure(figsize=(8, 4), dpi=100)
subplot = f.add_subplot(111)

# 将绘制的图形显示到tkinter:创建属于mainwindow的canvas画布,并将图f置于画布上
canvas = FigureCanvasTkAgg(f, master=mainwindow)
canvas.draw()  # 注意show方法已经过时了,这里改用draw
canvas.get_tk_widget().place(x=0, y=0)


# 键盘事件处理
def on_key_event(event):
	print("你按了%s" % event.key)
	key_press_handler(event, canvas, toolbar)

# 点击退出按钮时调用这个函数
def on_quit():
	if messagebox.askokcancel("退出程序", "您想要退出本程序吗?"):
		mainwindow.quit()  # 结束主循环
		mainwindow.destroy()  # 销毁窗口
	return

# 绘制单位净值
def button_draw_net():
	pass
	return

# 绘制累计净值
def button_draw_ac():
	plt.cla()
	fund_info = FundInfo()
	fund_list = fund_info.get_list()
	myfund_object = fund_info.get_fundinfo('005918')
	net_worthtrend = myfund_object.eval('Data_netWorthTrend')
	x = [datetime.datetime.fromtimestamp(int(o['x'])//1000) for o in net_worthtrend]
	y1 = [o['y'] for o in net_worthtrend]
	ac_worthtrend = myfund_object.eval('Data_ACWorthTrend')
	y2 = [e[1]-0.1 for e in ac_worthtrend]
	plt.plot(x, y1, color='b', label='net')
	plt.plot(x, y2, color='r', label='ac')
	plt.gcf().autofmt_xdate()
	plt.legend()
	canvas.draw()
	return


# 绑定键盘事件处理函数
canvas.mpl_connect('key_press_event', on_key_event)
# 绑定退出窗口事件
mainwindow.protocol("WM_DELETE_WINDOW", on_quit)

# 基金列表
fund_draw_list = tkinter.Listbox(mainwindow, width=22, height=10)
fund_draw_list.place(x=10, y=410)
# 绘制图片
btn_draw_net = tkinter.Button(mainwindow, text ="绘制单位净值", width=15, height=2, command=button_draw_net)
btn_draw_net.place(x=300, y=450)
btn_draw_ac = tkinter.Button(mainwindow, text ="绘制累计净值", width=15, height=2, command=button_draw_ac)
btn_draw_ac.place(x=300, y=500)
# 主循环
mainwindow.mainloop()