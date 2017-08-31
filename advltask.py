# _*_ coding:utf-8 _*_
# author:@shenyi
from datetime import datetime
import time
import os
from sendmail import send_mail
import pytz

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED,EVENT_JOB_ERROR,EVENT_ALL


timez = pytz.timezone('Asia/Shanghai')


def sendMail():
    mailto_list = ['ppag0440f2b3f783@sohu.com', '8697767@qq.com']
    send_mail(mailto_list, u"我是主题", u"我是正文")


def testFunc():
    a = 3
    b = 1
    try:
        c = a/b
    except:
        pass
    return c


def my_listener(event):
    import logging
    log = logging.getLogger('apscheduler.executors.default')
    if event.exception:
        print 'beng le:'
    else:
        print 'success:'
        # print event.job_id
        print event.scheduled_run_time.strftime("%Y-%m-%d %H:%M:%S")

scheduler = BackgroundScheduler(timezone=timez)
scheduler.add_job(func=testFunc, trigger='interval', seconds=2, id='my_mail')
scheduler.add_listener(my_listener, EVENT_JOB_ERROR)
scheduler.start()

try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()