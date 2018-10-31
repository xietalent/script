#!/usr/bin/python
#-*- coding:utf-8 -*-
# ScriptName: .py
#2018-10-30
#***************************************************************#
import os
import re
import sqlite3
import hashlib
import sys

webshell_keywords="eval\(|file_put_contents|base64_decode|python_eval|exec\(|passthru|popen|proc_open|pcntl|assert\(|system\(|shell"
remove_postfix_list=['jpg','bmp','js']


'''
PATH包含路径和文件名
MD5是文件的MD5值
Exclude 0表示没有问题，1表示可能是webshell需要手工确认,2表示文件有变化了，需要手工进行确认
'''
class webshell():
    def create_db(self):
        conn = sqlite3.connect('files.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE file 
              (
               PATH           TEXT   NOT NULL,
               MD5            TEXT   NOT NULL,
               Exclude        INT    NOT NULL,
               PRIMARY KEY ("MD5")
               );
        ''')
        conn.commit()
        conn.close()

    def inster_db(self,filepath,filemd5,exclude_key):
        conn = sqlite3.connect('files.db')
        c = conn.cursor()
        sql="replace INTO file (PATH,MD5,Exclude) VALUES ('%s','%s','%s')" % (filepath,filemd5,exclude_key)
        c.execute(sql)
        conn.commit()
        conn.close()

    def select_db_MD5(self,filepath):
        print filepath
        conn = sqlite3.connect('files.db')
        c = conn.cursor()
        sql='SELECT md5 from file where PATH="'+str(filepath)+'" limit 1'
        md5=c.execute(sql).fetchall()[0][0]
        conn.commit()
        conn.close()
        return md5

    def md5file(self,filepath):
        m=hashlib.md5()
        f = open(filepath, 'rb')
        while True:
            b = f.read(8192)
            if not b:
                break
            m.update(b)
        f.close()
        return m.hexdigest()

    def scan_webshell_new(self,path):
        for fpath, dirs, fs in os.walk(rootdir):
            for f in fs:
                filepath = str(os.path.join(fpath, f))
                if str(f).split('.')[1] not in remove_postfix_list:
                    with open(filepath) as f:
                        filevalue = f.read()
                        valid_regex = re.compile(webshell_keywords,re.I)
                        matches = re.findall(valid_regex, filevalue)
                    MD5_Now_Recode = webshell().md5file(filepath)
                    if len(matches) > 0:
                        print filepath+' maybe webshell'
                        webshell().inster_db(filepath,MD5_Now_Recode,'1')
                    else:
                        print filepath + ' no webshell'
                        webshell().inster_db(filepath, MD5_Now_Recode,'0')

    def scan_webshell(self,path):
        for fpath, dirs, fs in os.walk(rootdir):
            for f in fs:
                filepath = str(os.path.join(fpath, f))
                if str(f).split('.')[1] not in remove_postfix_list:
                    with open(filepath) as f:
                        filevalue = f.read()
                        valid_regex = re.compile(webshell_keywords,re.I)
                        matches = re.findall(valid_regex, filevalue)
                    MD5_Now_Recode=webshell().md5file(filepath)
                    MD5_Source_Recode=webshell().select_db_MD5(filepath)
                    if len(matches) > 0:
                        print filepath+' maybe webshell'
                        webshell().inster_db(filepath,MD5_Now_Recode,'1')
                    elif MD5_Now_Recode<>MD5_Source_Recode:
                        print filepath+' has change'
                        webshell().inster_db(filepath, MD5_Now_Recode, '2')
                    else:
                        print filepath + ' no change'
                        webshell().inster_db(filepath, MD5_Now_Recode, '0')

if __name__ == '__main__':
    banner='''usage:
    第一次或者有较多文件更新需要先删除老的数据库，重新扫描一下，执行一下命令
    python scan_webshell.py -new /var/www
    日常使用 
    python find.py -check /var/www
    默认排除文件类型：.jpg,.bmp,.js
    '''
    if (len(sys.argv)<2):
        print banner
    elif (len(sys.argv)==3 and sys.argv[1]=='-new'):
        print 'create DB'
        webshell().create_db()
        print 'begin scan'
        webshell().scan_webshell_new(sys.argv[2])
    elif (len(sys.argv)==3 and sys.argv[1]=='-check'):
        if os.path.isdir(sys.argv[2])==False:
            print 'path no found'
        else:
            print 'checking'+sys.argv[2]
            webshell().scan_webshell(sys.argv[2])
    else:
        print banner


