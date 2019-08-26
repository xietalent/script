#!/usr/bin/python
# -*- coding: UTF-8 -*-

#########################
#读取各大厂商的补丁信息
###########################
import feedparser
import datetime
import MySQLdb.cursors
import subprocess
import json
import time
import urllib2,urllib,requests
import datetime



odate=datetime.date.today()-datetime.timedelta(days = 7)

maillist='xxx@xxx.com'
ciscourl='https://tools.cisco.com/security/center/psirtrss20/CiscoSecurityAdvisory.xml'
windowsurl='https://api.msrc.microsoft.com/cvrf/'
conn = MySQLdb.connect(host='xxx.xxx.xxx.xxx', user='xxx', passwd='xxxxx', db='xxx', port=3306, charset='utf8')


year= datetime.datetime.strftime(odate,'%Y')
month= datetime.datetime.strftime(odate,'%b')

def save_to_db(sql):
    print sql
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

#####################################################################################################################################################
#微软 通过api来进行访问
#访问的地址是https://portal.msrc.microsoft.com/zh-cn/developer
#取的地址格式是
# curl -X GET --header 'Accept: application/json' --header 'api-key: 123123123123123' 'https://api.msrc.microsoft.com/cvrf/2018-june?api-version=2018'
#####################################################################################################################################################

def msrc_patch():

    sp = subprocess.Popen(['curl','-X','GET','--header', 'Accept: application/json','--header','api-key: xxxxxxxx','https://api.msrc.microsoft.com/cvrf/'+year+'-'+month+'?api-version='+year ], stdout=subprocess.PIPE)
    out, err = sp.communicate()
    print out
    msrc_json=json.loads(out)
    print(len(msrc_json['Vulnerability']))
    for i in range(len(msrc_json['Vulnerability'])):
        msrc_title = msrc_json['Vulnerability'][i]['Title']['Value']
        msrc_cve = msrc_json['Vulnerability'][i]['CVE']
        msrc_date = str(msrc_json['Vulnerability'][i]['RevisionHistory'][0]['Date']).replace('T',' ')
        #msrc_description = msrc_json['Vulnerability'][i]['Remediations'][j]['Description']['Value']
        for j in range(len(msrc_json['Vulnerability'][i]['Remediations'])):
            if 'URL' in msrc_json['Vulnerability'][i]['Remediations'][j]:
                msrc_update_url= msrc_json['Vulnerability'][i]['Remediations'][j]['URL']
            else:
                msrc_update_url=''
                #msrc_json['Vulnerability'][i]['Remediations'][j]['URL']==''
            if 'SubType' in msrc_json['Vulnerability'][i]['Remediations'][j]:
                msrc_subtype = msrc_json['Vulnerability'][i]['Remediations'][j]['SubType']
            else:
                msrc_subtype = ''
            sql = "replace into patch_update(title,cve,publish_date,url,update_type,product) values('%s','%s','%s','%s','%s','%s')" % (
                msrc_title, msrc_cve, msrc_date, msrc_update_url,msrc_subtype, 'Microsoft')
            save_to_db(sql)

#####################################################################################################################################################
#思科 通过rrs来进行访问
#访问的地址是https://tools.cisco.com/security/center/psirtrss20/CiscoSecurityAdvisory.xml
#####################################################################################################################################################

def cisco_path():
    d = feedparser.parse(ciscourl)
    for e in d.entries:
        title=e.title
        url=e.link
        DatetimeValue=time.strptime(str(e.published).replace(' CDT',''), "%a, %d %b %Y %H:%M:%S")
        datetime=time.strftime('%Y-%m-%d %H:%M:%S', DatetimeValue)
        sql = "replace into patch_update(title,cve,publish_date,url,update_type,product) values('%s','%s','%s','%s','%s','%s')" % (
            title, '', datetime, url, 'Security Update', 'Cisco')
        save_to_db(sql)




#####################################################################################################################################################
#redhat 通过api接口来进行访问
#访问的地址是https://access.redhat.com/labs/securitydataapi/cve.xml?after=2018-09-01
#####################################################################################################################################################
def redhat_path():
    url = 'https://access.redhat.com/labs/securitydataapi/cve.json?after='+str(odate)
    r=requests.get(url).json()
    for i in range(len(r)):
        title = str(r[i]['bugzilla_description']).replace("\n", "").replace("'s","").rstrip()
        cve=r[i]['CVE']
        cdate=time.strftime('%Y-%m-%d',time.strptime(str(r[i]['public_date']).split('T')[0], "%Y-%m-%d"))
        update_type=r[i]['severity']
        url=r[i]['resource_url']
        sql = "replace into patch_update(title,cve,publish_date,url,update_type,product) values('%s','%s','%s','%s','%s','%s')" % (
        title, cve, cdate, url, update_type, 'redhat')
        #print sql
        save_to_db(sql)




def emailNotice(recv):
    sql='SELECT * FROM `patch_update` WHERE publish_date >='+"'"+str(odate)+"'"
    cur = conn.cursor()
    cur.execute(sql)
    data = list(cur.fetchall())
    d = ''  # 表格内容
    for i in range(len(list(data))):
        #print list(data)[i]
        #print len(list(data)[i])
        d = d + """
                <tr>
                  <td >""" + str(list(data)[i][0]) + """</td>
                  <td >""" + str(list(data)[i][1]) + """</td>
                  <td width="10%" align="center">""" + str(list(data)[i][2]) + """</td>
                  <td width="40%">""" + str(list(data)[i][3]) + """</td>
                  <td width="10%">""" + str(list(data)[i][4]) + """</td>
                  <td width="10%">""" + str(list(data)[i][5]) + """</td>
                </tr>"""


    html = """\
        <html>
        <title>test</title>
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    
    
        <body>
        <div id="container">
        <p><strong>本周补丁推送情况:</strong></p>
        <div id="content">
         <table width="30%" border="2" bordercolor="black" cellspacing="0" cellpadding="0">
        <tr>
          <td ><strong>更新标题</strong></td>
          <td ><strong>cve编号</strong></td>
          <td width="10%" align="center"><strong>补丁发布时间</strong></td>
          <td width="40%"><strong>更新地址</strong></td>
          <td width="10%"><strong>更新级别</strong></td>
          <td width="10%"><strong>产品线</strong></td>
        </tr>""" + d + """
        </table>
        </div>
        </div>
        </div>
        </body>
        </html>
    """
#    print html


    url = 'http://security.xxx.xxx/oss/api/mail_api'
    values = {'recv': recv,
              'subject': '补丁更新提醒',
              'body': html}

    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    the_page = response.read()
    print the_page


cisco_path()
msrc_patch()
redhat_path()

emailNotice(maillist)
