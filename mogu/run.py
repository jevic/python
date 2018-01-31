#!/usr/bin/python
# coding: utf-8
import os,sys,re
import time
import datetime
import logbook
import redis
from ftp import MyFtp
from pyhdfs import HdfsClient
from ConfigParser import ConfigParser
from logbook.more import ColorizedStderrHandler
from multiprocessing import Pool

Sdir = os.path.split(os.path.realpath(sys.argv[0]))[0]
os.chdir(Sdir)

config = ConfigParser()
config.read('config.ini')

HdfsAddr = config.get('HDFS','HOST')
HdfsPath = config.get('HDFS','Path')
Rhost = config.get('REDIS','HOST')
RPASSWD = config.get('REDIS','PASSWD')
Rport = config.get('REDIS','PORT')
RDB = config.get('REDIS','DB')
RKey = config.get('REDIS','HKEY')
domains = config.get('DOMAIN','DOMAINS').split(' ')
Mins = int(config.get('HDFS','JobTime'))
Tmins = int(config.get('HDFS','Timeout'))
Timeout = 60 * Tmins
Usge = """Version: 20180118-v4.1
YYYMMDD/HHMM    -- 指定上传日志时间
 --help | -h"""

if len(sys.argv) == 2:
        Argv = sys.argv[1]
        if re.match('\d{8}/\d{4}$',Argv):
                jobTime = Argv
		Dday = Argv.split('/')[0]
        elif Argv == '--help' or Argv == '-h':
		print Usge
		sys.exit()
        else:
		print Usge
		sys.exit()
elif len(sys.argv) > 2:
     	print Usge
	sys.exit()
else:
	Times = (datetime.datetime.now() - datetime.timedelta(minutes = Mins))  
	jobTime = Times.strftime("%Y%m%d/%H%M")
	Dday = Times.strftime("%Y%m%d")

LOG_DIR = os.path.join('log')
DOWN_DIR = os.path.join('cdn/'+ Dday)
if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        
if not os.path.exists(DOWN_DIR):
		os.makedirs(DOWN_DIR)

APP_NAME = ':'
LOG_PATH = os.path.join(LOG_DIR,'migu.log')

class Logs():
	def __init__(self,jobTime):
		self.jobTime = jobTime
		self.domain = 'test'
		self.jobTimeObj = time.strptime(self.jobTime, '%Y%m%d/%H%M')
		self.PathDay = time.strftime('%Y%m%d',self.jobTimeObj)
		self.Path_Day = time.strftime('%Y_%m_%d',self.jobTimeObj)
		self.ObjTime = time.strftime('%H%M',self.jobTimeObj)
		self.success = "_SUCCESS"

	@property
	def HPath(self):
		return "%s/%s/%s/" % (HdfsPath,self.PathDay,self.ObjTime)
	
	@property
	def LogName(self):
		return "_%s_%s.gz" % (self.Path_Day,self.ObjTime)
	
	@property
	def Migu(self):		
		return "MG_CDN_4006_%s%s_" % (self.PathDay,self.ObjTime)


def get_logger(name=APP_NAME, file_log=False):
    logbook.set_datetime_format('local')
    ColorizedStderrHandler(bubble=False).push_application()
    if file_log:
        logbook.TimedRotatingFileHandler(LOG_PATH, date_format='%Y%m%d', bubble=True).push_application()
    return logbook.Logger(name)

def Add_Jobs(key):
    RedisClient.hset(RKey,key,0)
    RedisClient.shutdown

def upload(remote,local):
	try:
		myftp = MyFtp()
		myftp.dirs(Dday)
		myftp.Upload(remote,local)
	except Exception,error:
		logger.error(error)
	myftp.ftp.quit()

def GetJobs():
    try:
        handlejobs = RedisClient.hgetall(RKey)
	jobs = []
	for handlejob in handlejobs:
                if Timeout_log(handlejob):
			logger.warn(handlejob + "   Timeout Delete Key")
    			RedisClient.hdel(RKey,handlejob)
			continue
		if handlejobs[handlejob] == "1":
			continue
		jobs.append(handlejob)
	RedisClient.shutdown
        return jobs
    except Exception,e:
		logger.warn(e)

def Timeout_log(jobTime):
    nowTime = datetime.datetime.now()
    newTs = int(time.mktime(nowTime.timetuple()))
    jobTimeTs = int(time.mktime(time.strptime(jobTime,"%Y%m%d/%H%M")))
    return (Timeout < (newTs - jobTimeTs))


def RunLog(jobTime):
	ups = Logs(jobTime)
	if Client.exists(ups.HPath + ups.success):
		RedisClient.hset(RKey,jobTime,1)
		for domain in domains:
			Files = ups.HPath + domain + ups.LogName
			ids = "%.3d" % int(domains.index(domain)+1)
			if Client.exists(Files):
				Dfile = DOWN_DIR + '/' + ups.Migu + ids + '.log.gz'
				logger.info("下载文件: " + Files + " " + Dfile)
				Client.copy_to_local(Files, Dfile)
				logger.info("上传文件: /"+Dday+"/"+ ups.Migu + ids + '.log.gz')
				upload(ups.Migu + ids + '.log.gz',Dfile)
				RedisClient.hdel(RKey,jobTime)
	else:
		logger.warn(ups.HPath + " 文件未生成")


if __name__ == '__main__':
	logger = get_logger(file_log=True)
	try:
		Client = HdfsClient(hosts = HdfsAddr)
		pool = redis.ConnectionPool(host=Rhost, password=RPASSWD, port=Rport, db=RDB)
		RedisClient = redis.Redis(connection_pool=pool)
	except Exception,error:
		logger.error(error)
		sys.exit()
	Add_Jobs(jobTime)
	jobs = GetJobs()
        pool = Pool()
        pool.map(RunLog,jobs)
        pool.close()
        pool.join()
