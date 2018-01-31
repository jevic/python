#!/usr/bin/python
# coding: utf-8
import os,sys
import ftplib
from ConfigParser import ConfigParser

config = ConfigParser()
config.read('config.ini')
FtpHost = config.get('FTP','HOST')
username = config.get('FTP','USER')
passwd = config.get('FTP','PASSWD')

class MyFtp():
	ftp = ftplib.FTP()
	def __init__(self):
		try:
			self.bufsize = 1024
			self.ftp.connect(FtpHost)
			self.ftp.login(username,passwd)
		except Exception,e:
			print e
	
	def List(self,path=''):
		self.ftp.dir(path)

	def dirs(self,remote):
		try:
			self.ftp.cwd(remote)
		except ftplib.error_perm:
			try:
				self.ftp.mkd(remote)
				self.ftp.cwd(remote)
			except ftplib.error_perm:
				print "U have no authority to make dir"

	def DownFile(self,remote,local):
		fp = open(local,'wb')
		self.ftp.retrbinary('RETR ' + remote,fp.write,self.bufsize)
		fp.close()

	def Upload(self,remote,local):
		fp = open(local,'rb')
		self.ftp.storbinary('STOR ' + remote,fp,self.bufsize)
		fp.close()
