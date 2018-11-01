 #!/usr/bin/python
#-*- coding:utf-8 -*-
# ScriptName: .py
# Create Date: 2016-02-02 17:41
# Modify Date: 2018-04-28 17:41
#***************************************************************#


import time
import datetime
import os
import MySQLdb.cursors
from github import Github


cdate=str(datetime.date.today())
#cdate='2016-07-15'
odate=str(datetime.date.today()-datetime.timedelta(days = 1))
#print odate
#odate='2016-07-14'
#date=str(datetime.date.today()-datetime.timedelta(days=1))

token = 'zzzzzzzz' #自己申请一下
sqlproject = ("select git_scan_key,confirm from git_scan_key")
conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='caspar',port=3306,charset='utf8')


class Scanner(object):


    #从数据库中取git关键字
    def get_scan_keyword(self,sql):
        cur = conn.cursor()
        cur.execute(sql)
        data=cur.fetchall()
        cur.close
        return data


    #根据关键字搜索项目存茹数据库
    def git_repositories_find(self,key):
        print(key)
        cur=conn.cursor()
        for repo in g.search_code(key):
            git_repositories_name=str(repo.name)
            git_repositories_owner = str(repo.owner.login)
            git_repositories_language = str(repo.language)
            git_repositories_cloneurl = str(repo.clone_url)
            git_repositories_updatetime = str(repo.updated_at).split(' ')[0]
            key_change_time=Scanner().get_scan_keyword('select change_time from git_scan where git_project="'+git_repositories_name+'" limit 1')
            sql = "insert into git_scan(cdate,change_time,git_project,git_url,user,language,git_scan_key) values('%s','%s','%s','%s','%s','%s','%s')" % (cdate, git_repositories_updatetime, git_repositories_name, git_repositories_cloneurl,git_repositories_owner, git_repositories_language, key)
            # 没有这个项目，查询事件为空
            if len(key_change_time)>0:
                if time.strptime(key_change_time[0][0],'%Y-%m-%d')>time.strptime(git_repositories_updatetime,'%Y-%m-%d'):
                    cur.execute(sql)
                    conn.commit()
                    time.sleep(10)
            else:
                print sql
                cur.execute(sql)
                conn.commit()
                time.sleep(10)
        cur.close()


    #复制项目，搜索项目中的文件是不是包含特定关键字
    def git_code_find(self,key):
        print(key)
        cur=conn.cursor()
        for repo in g.search_code(key):
            git_code_file_name=repo.name
            git_code_file_sha=repo.sha
            git_code_file_size=repo.size
            git_code_file_type=repo.type
            git_code_file_download_url=repo.download_url

            key_change=Scanner().get_scan_keyword('select file_sha,file_size from git_scan_code where file_name="'+git_code_file_name+'" limit 1')
            sql = "insert into git_scan_code(cdate,file_name,file_sha,file_size,file_type,download_url,git_scan_key) values('%s','%s','%s','%s','%s','%s','%s')" % (cdate, git_code_file_name, git_code_file_sha, git_code_file_size,git_code_file_type, git_code_file_download_url, key)

            if len(key_change) > 0:
                if key_change[0][0]<>git_code_file_sha or key_change[0][1]<>git_code_file_size:
                    cur.execute(sql)
                    conn.commit()
                    time.sleep(10)
            else:
                print sql
                cur.execute(sql)
                conn.commit()
                time.sleep(10)

if __name__ == "__main__":

    g=Github(token)
    #Scanner().git_code_find("pingan.com")
    datas=Scanner().get_scan_keyword(sqlproject)
    for i in range(len(datas)):
        git_scan_key, confirm = datas[i]
        if confirm == 1:
            Scanner().git_code_find(git_scan_key)
        elif confirm == 0:
            Scanner().git_repositories_find(git_scan_key)
