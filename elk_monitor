#!/usr/bin/python
#-*- coding:utf-8 -*-
# ScriptName: attack_monitor.py
# Create Date: 2017-05-10 16:53
# Modify Date: 2017-05-10 16:53
#***************************************************************#

import sys
reload(sys) # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')


from elasticsearch import Elasticsearch
import elasticsearch.helpers as helpers
import re
import urllib2
import urllib
import requests
import time
import os



es = Elasticsearch(
        ['192.168.1.1','192.168.1.2','192.168.1.3'],
        sniff_on_start=True,
        sniff_on_connection_fail=True,
        sniffer_timeout=60
                )


scanResp = helpers.scan(
        client=es,
        scroll="2m",
        query={
            "query": {
                "bool": {
                    "filter": {
                        "range": {
                            "@timestamp": {"gt": "now-2h"}
                        }
                    }
                }
            }
        },
        index="ssh*",
        timeout="5m",
        size=100)

i=0
for resp in scanResp:
    i=i+1
    client_host=resp['_source']['ClientIP']
    service_host = resp['_source']['ServiceIP']
    status=resp['_source']['status']
    message = str(resp['_source']['message'])


print("totle:"+str(i))



