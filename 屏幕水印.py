#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import win32api, win32con, pywintypes
import tkinter
import os
from win32com.client import GetObject
import sys
import subprocess

Process_list=['excel.exe','word.exe','POWERPNT.exe']
mark=0

def get_replicate_text(text):
    i, space, str1, str2 = 0, 70, "", ""
    while (i <= 5):
        str1 = str1 + text + " " * space
        i = i + 1
    str2 = " " * space + str1 + "\n\n\n\n"
    str1 = str1 + "\n\n\n\n"
    str1 = (str1 + str2) * 5
    return str1

def app_usage(appname):
    wmi = GetObject('winmgmts:/root/cimv2')
    appbase = wmi.ExecQuery(
        'select * from Win32_Process where CommandLine like "%{}%" and Caption != "python.exe"'.format(appname))
    for item in appbase:
        apppid = item.ProcessId

    appstatus = []

    try:
        appinfo = wmi.ExecQuery(
            'select * from Win32_PerfFormattedData_PerfProc_Process where IDProcess = "{}"'.format(apppid))
    except UnboundLocalError as nopid:
        return "0"
        sys.exit(2)

    for item in appinfo:
        appstatus.append(item.PercentProcessorTime)
        appstatus.append(round(float(item.WorkingSetPrivate) / 1024 / 1024, 2))
    appstatus.append(subprocess.getstatusoutput('netstat -ano | findstr {} | wc -l'.format(apppid))[1])

    return (appname, apppid, appstatus)


mytext = get_replicate_text(os.environ['USERNAME'])
root = tkinter.Tk()
width = win32api.GetSystemMetrics(0)
height = win32api.GetSystemMetrics(1)
root.overrideredirect(True)  # 隐藏显示框
root.geometry("+0+0")  # 设置窗口位置或大小
root.attributes("-alpha", 0.2)
root.lift()  # 置顶层
root.wm_attributes("-topmost", True)  # 始终置顶层
root.wm_attributes("-disabled", True)
root.wm_attributes("-transparentcolor", "white")  # 白色背景透明

hWindow = pywintypes.HANDLE(int(root.frame(), 16))
exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)
label = tkinter.Label(text=mytext, compound='left', font=('Times New Roman', '30'), fg='#FF0000', bg='#ffffff')
label.pack()  # 显示
root.mainloop()  # 循环

