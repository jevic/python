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

```

