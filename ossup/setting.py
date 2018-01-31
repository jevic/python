#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import hashlib
from ConfigParser import ConfigParser

'''
配置信息
帮助信息
md5sum
MySQL 加载
'''

config = ConfigParser()
config.read('config.ini')

HdfsHost = config.get('HDFS','HOST')
HdfsPath = config.get('HDFS','Path')

Mins = int(config.get('HDFS','JobTime'))
Tmins = int(config.get('HDFS','Timeout'))
Timeout = 60 * Tmins

access_key_id = config.get('OSS','ACCESS_KEY_ID')
access_key_secret = config.get('OSS','ACCESS_KEY_SECRET')
bucket = config.get('OSS','BUCKET_NAME')
endpoint = config.get('OSS','ENDPOINT')
osspath = config.get('OSS','OSS_PATH')

muser = config.get('DB','USER')
mpass = config.get('DB','PASSWD')
mhost = config.get('DB','HOST')
mdb = config.get('DB','DBASE')
table = config.get('DB','TABLE')

domains = config.get('DOMAIN','DOMAINS').split(' ')

Rhost = config.get('REDIS','HOST')
RPASSWD = config.get('REDIS','PASSWD')
Rport = config.get('REDIS','PORT')
RDB = config.get('REDIS','DB')
RKey = config.get('REDIS','HKEY')

Version = '20180117v1'
Usage = """
[提示:] 直接运行则处理当前时间前30分钟时间点的日志!!!
------------------------------------------------------
[获取HDFS五分钟日志 上传OSS]

YYYMMDD/HHMM    -- 20180117/1205 -- 上传1月17号12点05分的日志
-v|-V           -- 版本信息
-h|--help       -- 帮助信息
Ctrl+c          -- 退出程序
"""

def get_md5_value(src):
    myMd5 = hashlib.md5()
    myMd5.update(src)
    myMd5_Digest = myMd5.hexdigest()
    return str(myMd5_Digest[-6:])
