import tkinter
from tkinter import messagebox, ttk
from datetime import datetime, date
from datetime import timedelta
import time
import decimal
import collections
import sqlite3


mainwindow = tkinter.Tk()
mainwindow.title("基金投资管理软件 v0.1")
mainwindow.geometry("800x600+50+50")
mainwindow.resizable(0, 0)

# 从数据库读取当前持有基金
connect = sqlite3.connect('myfund.db3')
print("database connected")
cursor = connect.cursor()

fund_set_current = set()
res = cursor.execute("SELECT DISTINCT fund FROM current")
for row in res:
    fund_set_current.add(row[0])
# print(fund_set_current)

fund_set_profit = set()
res = cursor.execute("SELECT DISTINCT fund FROM profit")
for row in res:
    fund_set_profit.add(row[0])

# 关闭窗口事件


def on_closing():
    if messagebox.askokcancel("退出程序", "您想要退出本程序吗?"):
        connect.close()
        print("database connection closed")
        mainwindow.destroy()
    return

# 查看当前基金


def show_current_fund(event):
    items = table_current_fund.get_children()
    [table_current_fund.delete(item) for item in items]
    items = table_cal_profit.get_children()
    [table_cal_profit.delete(item) for item in items]
    sel = list_fund_current.curselection()
    if not sel:
        return
    index = list_fund_current.curselection()[0]
    fund_name = list_fund_current.get(index)
    # print(index, fund_name)
    cursor.execute(
        "SELECT date, amount FROM current WHERE fund='{}'".format(fund_name))
    res = cursor.fetchall()
    # print(res)
    total = 0
    for row in res:
        date, amount = row
        table_current_fund.insert('', 'end', values=(date, amount / 100))
        total += amount
    table_current_fund.insert('', 'end', values=("总金额", total / 100))
    profit_base = cal_profit_by_rate(res, 1)
    for rate in range(1, 31):
        profit = profit_base * rate
        table_cal_profit.insert(
            '', rate - 1, values=(str(rate) + '%', round(profit, 2)))
    return

# 以目标年化利率计算目标持有收益


def cal_profit_by_rate(table, rate):
    dr = decimal.Decimal(rate) / 100 + 1
    day_rate = [(dr**i - 1) / 365 for i in range(1, 6)]  # 计算日利率
    # day_rate = decimal.Decimal(rate) / decimal.Decimal(365) / 100
    profit = decimal.Decimal(0)
    today = date.today()
    for dt, amount in table:
        datetime_date = datetime.strptime(dt, "%Y-%m-%d")
        date_time = datetime.date(datetime_date)
        delta = today - date_time
        days = decimal.Decimal(delta.days)
        year = int(days // 365)
        profit += decimal.Decimal(amount) / 100 * day_rate[year] * days
    return profit

# 查看基金历史收入


def fund_profit(event):
    items = table_profit.get_children()
    [table_profit.delete(item) for item in items]
    fund_name = cmb_fund_profit.get()
    cursor.execute(
        "SELECT date, buy_amount, sold_amount, profit_amount FROM profit WHERE fund='{}'".format(fund_name))
    res = cursor.fetchall()
    total_buy, total_sold, total_profit = 0, 0, 0
    for row in res:
        date, buy, sold, profit = row
        table_profit.insert('', 'end', values=(
            date, buy / 100, sold / 100, profit / 100))
        total_buy += buy
        total_sold += sold
        total_profit += profit
    table_profit.insert('', 'end', values=(
        "总金额", total_buy / 100, total_sold / 100, total_profit / 100))
    return

# 买入


def button_buy():
    dt = entry_date.get()
    if not dt:
        dt = time.strftime('%Y-%m-%d', time.localtime())
    amount = entry_amount.get()
    if not amount:
        messagebox.showinfo('提示', '操作金额不能为空')
        return
    fund = cmb_fund.get()
    if not fund:
        messagebox.showinfo('提示', '操作基金不能为空')
        return
    amount = int(amount)
    print("buy", dt, amount, fund)
    cursor.execute("INSERT INTO current(date, amount, fund) VALUES('{}', {}, '{}')".format(
        dt, amount, fund))
    cursor.execute("INSERT INTO history(date, amount, fund, sold) VALUES('{}', {}, '{}', 0)".format(
        dt, amount, fund))
    connect.commit()
    # 更新持有基金列表
    fund_set_current.add(fund)
    list_fund_current.delete(0, 'end')
    for item in sorted(fund_set_current):
        list_fund_current.insert("end", item)
    return

# 卖出


def button_sell():
    dt = entry_date.get()
    if not dt:
        dt = time.strftime('%Y-%m-%d', time.localtime())
    sold_amount = entry_amount.get()
    if not sold_amount:
        messagebox.showinfo('提示', '操作金额不能为空')
        return
    fund = cmb_fund.get()
    if not fund:
        messagebox.showinfo('提示', '操作基金不能为空')
        return
    sold_amount = int(sold_amount)
    cursor.execute(
        "SELECT sum(amount) FROM current WHERE fund='{}'".format(fund))
    res = cursor.fetchall()
    buy_amount = res[0][0]
    profit_amount = sold_amount - buy_amount
    print("sold", dt, buy_amount, sold_amount, profit_amount, fund)
    cursor.execute("INSERT INTO profit(date, buy_amount, sold_amount, profit_amount, fund) VALUES('{}', {}, {}, {}, '{}')".format(
        dt, buy_amount, sold_amount, profit_amount, fund))
    cursor.execute("DELETE FROM current WHERE fund='{}'".format(fund))
    cursor.execute("INSERT INTO history(date, amount, fund, sold) VALUES('{}', {}, '{}', 1)".format(
        dt, sold_amount, fund))
    connect.commit()
    # 更新基金列表
    fund_set_current = set()
    res = cursor.execute("SELECT DISTINCT fund FROM current")
    for row in res:
        fund_set_current.add(row[0])
    list_fund_current.delete(0, 'end')
    for item in sorted(fund_set_current):
        list_fund_current.insert("end", item)
    fund_set_profit = set()
    res = cursor.execute("SELECT DISTINCT fund FROM profit")
    for row in res:
        fund_set_profit.add(row[0])
    cmb_fund_profit['value'] = tuple(sorted(fund_set_profit))
    return

# 绑定退出窗口事件
mainwindow.protocol("WM_DELETE_WINDOW", on_closing)


# 窗口布局
# 持有基金
label_fund_current = tkinter.Label(mainwindow, text="持有基金列表")
label_fund_current.place(x=10, y=10)
list_fund_current = tkinter.Listbox(mainwindow, width=22)
for item in sorted(fund_set_current):
    list_fund_current.insert("end", item)
list_fund_current.place(x=10, y=32)
list_fund_current.bind("<<ListboxSelect>>", show_current_fund)

label_fund_current_record = tkinter.Label(mainwindow, text="当前基金持有记录")
label_fund_current_record.place(x=180, y=10)
frame = tkinter.Frame(mainwindow)
frame.place(x=180, y=32, width=220, height=446)
scrollBar = tkinter.Scrollbar(frame)
scrollBar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
table_current_fund = ttk.Treeview(
    frame, show="headings", yscrollcommand=scrollBar.set)
table_current_fund["columns"] = ("买入日期", "买入金额")
table_current_fund.column("买入日期", width=100, anchor="center")
table_current_fund.column("买入金额", width=100, anchor="center")
table_current_fund.heading("买入日期", text="买入日期")
table_current_fund.heading("买入金额", text="买入金额（元）")
table_current_fund.pack(side=tkinter.LEFT, fill=tkinter.Y)
scrollBar.config(command=table_current_fund.yview)

label_cal_profit = tkinter.Label(mainwindow, text="计算目标收益")
label_cal_profit.place(x=10, y=228)
table_cal_profit = ttk.Treeview(mainwindow, show="headings")
table_cal_profit.place(x=10, y=252)
table_cal_profit["columns"] = ("收益率", "收益金额")
table_cal_profit.column("收益率", width=52, anchor="center")
table_cal_profit.column("收益金额", width=102, anchor="center")
table_cal_profit.heading("收益率", text="收益率")
table_cal_profit.heading("收益金额", text="收益金额（元）")

# 历史收益部分
label_profit = tkinter.Label(mainwindow, text="查看历史收益")
label_profit.place(x=420, y=10)
cmb_fund_profit = ttk.Combobox(mainwindow, width=40)
cmb_fund_profit['value'] = tuple(sorted(fund_set_profit))
cmb_fund_profit.place(x=420, y=32)
cmb_fund_profit.bind("<<ComboboxSelected>>", fund_profit)
table_profit = ttk.Treeview(mainwindow, show="headings", height=19)
table_profit.place(x=420, y=66)
table_profit["columns"] = ("卖出日期", "买入金额", "卖出金额", "收益金额")
table_profit.column("卖出日期", width=100, anchor="center")
table_profit.column("买入金额", width=80, anchor="center")
table_profit.column("卖出金额", width=80, anchor="center")
table_profit.column("收益金额", width=80, anchor="center")
table_profit.heading("卖出日期", text="卖出日期")
table_profit.heading("买入金额", text="买入金额")
table_profit.heading("卖出金额", text="卖出金额")
table_profit.heading("收益金额", text="收益金额")

# 记录功能部分
label_date = tkinter.Label(mainwindow, text="操作日期")
label_date.place(x=10, y=500)
entry_date = tkinter.Entry(mainwindow, width=22)
entry_date.place(x=10, y=525)
label_amount = tkinter.Label(mainwindow, text="操作金额（分）")
label_amount.place(x=180, y=500)
entry_amount = tkinter.Entry(mainwindow, width=22)
entry_amount.place(x=180, y=525)
label_fund = tkinter.Label(mainwindow, text="操作基金")
label_fund.place(x=360, y=500)
cmb_fund = ttk.Combobox(mainwindow, width=22)
cmb_fund['value'] = tuple(sorted(fund_set_current | fund_set_profit))
cmb_fund.place(x=360, y=523)

btn_buy = tkinter.Button(mainwindow, text="买入", width=10,
                         height=2, command=button_buy)
btn_buy.place(x=580, y=500)
btn_sell = tkinter.Button(mainwindow, text="卖出",
                          width=10, height=2, command=button_sell)
btn_sell.place(x=680, y=500)

# 进入消息循环
mainwindow.mainloop()
