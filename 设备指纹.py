#!/usr/bin/python
#-*- coding:utf-8 -*-
# ScriptName: .py
#2018-11-11
#***************************************************************#
import sys
import subprocess
import re
import MySQLdb.cursors
import threading


conn = MySQLdb.connect(host='localhost', user='caspar', passwd='caspar', db='caspar', port=3306, charset='utf8')

class IP_Scan():
    c_reg = re.compile(r'^(\d+).*?\s+(\w+)\s+(.*?)$')
    h_reg = re.compile(r'^Nmap scan report for .*?(\d+\.\d+\.\d+\.\d+).*')
    thread_count = 4
    hosts = []
    lock = threading.Lock()

    def scan_ip(self,hosts):
        host_list=[]
        sp = subprocess.Popen(['nmap', '-PI', '-sn', hosts], stdout=subprocess.PIPE)
        sp_lines = sp.stdout.readlines()
        for line in sp_lines:
            n = self.h_reg.match(line.strip())
            if n:
                ip= n.group(1)
                sql = "insert ignore INTO ip_scan_new(ip,in_portscan_whitelist,isnew) values('%s','%s','%s')" % (ip, 'n', 'y')
                self.insert_db(sql)
        sql2='select ip from ip_scan_new where in_portscan_whitelist="n"'
        host_list=self.select_db(sql2)
        return host_list

    def scan_port(self,host):
        sp = subprocess.Popen(['nmap', '-sV', host], stdout=subprocess.PIPE)
        sp_lines = sp.stdout.readlines()
        for line in sp_lines:
            m = self.c_reg.match(line.strip())
            if m:
                port = m.group(1)
                stat = m.group(2)
                service = m.group(3)
                if stat=='open':
                    #print str(host) +':'+str(port)+":"+str(service)
                    sql = "insert ignore INTO port_fingerprint(host,port,service,is_white) values('%s','%s','%s','%s')" % (host, port, service,'n')
                    self.insert_db(sql)

    def insert_db(self,sql):
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

    def select_db(self,sql):
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        return data



    def pop_queue(self):
        ip = None
        self.lock.acquire()
        if self.hosts:
            ip = self.hosts.pop()
        self.lock.release()
        return ip

    def dequeue(self):
        while True:
            ip = self.pop_queue()
            if not ip:
                return None
            self.scan_port(ip)



    def start(self):
        threads = []

        for i in range(self.thread_count):
            t = threading.Thread(target=self.dequeue)
            t.start()
            threads.append(t)

        [t.join() for t in threads]


#data=IP_Scan().scan_ip('10.254.16.1/30')

if __name__ == '__main__':
    banner='''usage:
    使用方法:
    python xx.py 192.168.1.1/30
    会先进行ip的探测，判断ip的存活状态，如果确定不需要端口扫描可以把ip_scan表中的in_portscan_white设置为y，下次扫描端口不会启动扫描
    端口扫描会把结果存储port_fingerprint表中，扫描结束之后需要确认，确认端口把is_white设置为Y，新增端口默认为N,如记录不需要请删除。
    程序运行锅中中的mysql警告说明数据原来存在表中，不会重复插入。
    有空会把有变化的增加出来
    '''
    if (len(sys.argv)<>2):
        print banner
    else:
        print("start")
        data= IP_Scan().scan_ip(sys.argv[1])
        scanner = IP_Scan()
        scanner.hosts = []
        for d in data:
            scanner.hosts.append(d[0])
        scanner.start()
