#!/usr/bin/python
# coding: utf-8
# auth: jieyang
# 
import os,sys,re
import time
import datetime
import logbook
import redis
import oss2
from setting import *
from pyhdfs import HdfsClient
import mysql.connector
from ConfigParser import ConfigParser
from logbook.more import ColorizedStderrHandler
from multiprocessing import Pool

Sdir = os.path.split(os.path.realpath(sys.argv[0]))[0]
os.chdir(Sdir)

Aname = sys.argv[0]
if len(sys.argv) == 2:
    Argv = sys.argv[1]
    if re.match('\d{8}/\d{4}$',Argv):
    	jobTime = Argv
    	Dday = Argv.split('/')[0]
    elif Argv == '--help' or Argv == '-h':
	print Usage
	sys.exit()
    elif Argv == '-V' or Argv == '-v':
	print Version
	sys.exit()
    else:
	print Usage
	sys.exit()
elif len(sys.argv) > 2:
	print Usage
	sys.exit()
else:
	nowTime = datetime.datetime.now()
	Times = nowTime - datetime.timedelta(minutes = Mins)
	jobTime = Times.strftime("%Y%m%d/%H%M")
	Dday = Times.strftime("%Y%m%d")

LOG_DIR = os.path.join('log')
DOWN_DIR = os.path.join('cdn/'+ Dday)
if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        
if not os.path.exists(DOWN_DIR):
		os.makedirs(DOWN_DIR)

APP_NAME = ':'
LOG_PATH = os.path.join(LOG_DIR,'%s.log' % Aname)

def create_logs():
	log_mins = Mins - 5
	Times = nowTime - datetime.timedelta(minutes = log_mins) 
	jobTime = Times.strftime("%Y%m%d/%H%M")
	Add_Jobs(jobTime)
	
class Logs():
	def __init__(self,jobTime):
		self.jobTime = jobTime
		self.jobTimeObj = time.strptime(self.jobTime, '%Y%m%d/%H%M')
		self.PathDay = time.strftime('%Y%m%d',self.jobTimeObj)
		self.Path_Day = time.strftime('%Y_%m_%d',self.jobTimeObj)
		self.OSS_Day = time.strftime('%Y-%m-%d',self.jobTimeObj)
		self.ObjTime = time.strftime('%H%M',self.jobTimeObj)
		self.timestamp = int(time.mktime(self.jobTimeObj))
		self.success = "_SUCCESS"

	@property
	def HPath(self):
		return "%s/%s/%s/" % (HdfsPath,self.PathDay,self.ObjTime)

	@property
	def OssPath(self):
		return "%s/%s/%s/" % (osspath,self.OSS_Day,self.ObjTime)

	def LogName(self,domain):
		return "%s_%s_%s.gz" % (domain,self.Path_Day,self.ObjTime)

def get_logger(name=APP_NAME, file_log=False):
    logbook.set_datetime_format('local')
    ColorizedStderrHandler(bubble=False).push_application()
    if file_log:
        logbook.TimedRotatingFileHandler(LOG_PATH, date_format='%Y%m%d', bubble=True).push_application()
    return logbook.Logger(name)

def ossUpload(domain):
        try:
            Bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket)
            Localfile = DOWN_DIR + "/" + ups.LogName(domain)
            Bucket.put_object_from_file("%s%s" % (ups.OssPath,ups.LogName(domain)),Localfile)
            logger.info("oss://" + bucket + "/" + ups.OssPath + ups.LogName(domain))
        except Exception,osse:
            logger.error('上传 OSS文件失败 %s' % osse)
            sys.exit()

def DB():
    try:
        db = mysql.connector.connect(user=muser,host=mhost,password=mpass,database=mdb)
        return db
    except Exception,emysql:
        print emysql
        sys.exit()

def Indb(domain):
        Prefix = ups.OssPath + ups.LogName(domain)
        clength = os.path.getsize(DOWN_DIR + "/" + ups.LogName(domain))
        mtype = 0
        length = 5
        timestamp = ups.timestamp
        create_time = int(time.mktime(datetime.datetime.now().timetuple()))
        sql = "insert %s(bucket,prefix,host,timestamp,create_time,length,mtype,content_length) values('%s','%s','%s','%s','%s','%s','%s','%s')" % (table,bucket, Prefix, domain, timestamp, create_time,length, mtype, clength)
        try:
            sdb = DB()
            cursor = sdb.cursor()
            cursor.execute(sql)
            sdb.commit()
            logger.info(sql)
        except Exception,e3:
            sdb.rollback()
            logger.error(e3)
            sys.exit()
        sdb.close()

def Add_Jobs(key):
    RedisClient.hset(RKey,key,0)
    RedisClient.shutdown

def Getjobs():
	try:
		handlejobs = RedisClient.hgetall(RKey)
		jobs = []
		for handlejob in handlejobs:
			if Timeout_log(handlejob):
				logger.warn(handlejob + " Timeout Delete Key")
				RedisClient.hdel(RKey,handlejob)
				continue
			if handlejobs[handlejob] == '1':
				continue
			jobs.append(handlejob)
		RedisClient.shutdown
		return jobs
	except Exception,e:
		logger.warn(e)


def Timeout_log(jobTime):
    newTs = int(time.mktime(nowTime.timetuple()))
    jobTimeTs = int(time.mktime(time.strptime(jobTime,"%Y%m%d/%H%M")))
    return (Timeout < (newTs - jobTimeTs))


def RunLog(jobTime):
	global ups
	ups = Logs(jobTime)
	if Client.exists(ups.HPath + ups.success):
		RedisClient.hset(RKey,jobTime,1)
		for domain in domains:
			Files = ups.HPath + ups.LogName(domain)
			if Client.exists(Files):
				Localfile = DOWN_DIR + "/" + ups.LogName(domain) 
				logger.info(' ')
				logger.info("下载文件: " + Files + " " + Localfile)
				Client.copy_to_local(Files, Localfile)

				logger.info("上传文件: %s" % Localfile)		
				ossUpload(domain)

				Indb(domain)
				RedisClient.hdel(RKey,jobTime)
	else:
		logger.warn(ups.HPath + " 文件未生成")


if __name__ == '__main__':
	logger = get_logger(file_log=True)
	try:
		Client = HdfsClient(hosts = HdfsHost)
		pool = redis.ConnectionPool(host=Rhost, password=RPASSWD, port=Rport, db=RDB)
		RedisClient = redis.Redis(connection_pool=pool)
	except Exception,error:
		logger.error(error)
		sys.exit()
	Add_Jobs(jobTime)
	jobs = Getjobs()
	pool = Pool()
	pool.map(RunLog,jobs)
	pool.close()
	pool.join()
	create_logs()
