# 微信企业号报警接口
## 目录

```
alarm
├── alarm.py   接口程序
└── weixin.py  接口调用脚本

```

## 使用说明

```
jay➜~» git clone https://github.com/jevic/python.git
jay➜~» yum install -y python-devel gcc
jay➜~» pip install flask werkzeug setproctitle daemon

jay➜~» cd python/alarm
jay➜~» vim alarm.py
.....
procname = 'xxxx'  ## 进程名称
setproctitle(procname)
print getproctitle ()

## 修改以下三处
Corpid = "xxxxx"
Corpsecret = "xxxxx"
agentid = xxxxx
.....

jay➜~» python alarm.py

jay➜~» curl 127.0.0.1:51001/send_message?content=test

```
## Shell 脚本

```
#!/bin/bash
wechat()
{
                DT_ADDR='127.0.0.1:51001'
                #处理下编码，用于合并告警内容的标题和内容
                #中文需要utf8编码并进行urlencode
                message=$(echo -e "$title\n$content"|od -t x1 -A n -v -w1000000000 | tr " " %)
                DT_URL="http://$DT_ADDR/send_message?content=$message"
                /usr/bin/curl $DT_URL
}

#title=test
#content=test
#wechat

```

## Python调用

```
#!/usr/bin/python
# coding: utf-8
#
from urllib import quote
import urllib2
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

def wechat(title,content):
        Title = quote(title.encode('utf8'))
        Content = quote(content.encode('utf8'))
        API_URL="http://127.0.0.1:51001/send_message?content=%s%s" % (Title,Content)
        try:
            req = urllib2.Request(API_URL)
            result = urllib2.urlopen(req)
            res = result.read()
        except:
            print "error"


```
