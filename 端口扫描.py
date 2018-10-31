#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import re
import monitor_weixin
file = '/opt/caspar/white_list.txt'


def Port_WhiteList(ip,port):
	static_key=None
	file_object = open(file)
	try:
		for line in file_object:
			aline= line.strip()
			scan_recorde= ip+':'+port
			if aline == scan_recorde:
				static_key=port
				break
	finally:
		file_object.close( )
	return static_key



def Port_scanner(ip):
	c_reg = re.compile(r'^(\d+).*?\s+(\w+)\s+(.*?)$')
	sp = subprocess.Popen(['nmap', '-open', '-p 1-10000', ip], stdout=subprocess.PIPE)
	sp_lines = sp.stdout.readlines()
	for line in sp_lines:
		n=re.search('Nmap scan report for ', line)
		if n:
			ipaddress=line.replace('Nmap scan report for ','')

		m = c_reg.match(line.strip())
		if m:
			port = m.group(1)
			stat = m.group(2)
			ipadd=ipaddress.replace('Nmap scan report for ','').strip()
			if stat == 'open' and Port_WhiteList(ipadd,port) == None:
				monitor_weixin.monitor(ipadd+"存在非白名单端口："+port)
				print (ipadd+"存在非白名单端口："+port)


Port_scanner('114.114.114.114/32')









