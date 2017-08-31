# -*- coding:utf-8 -*-
import ConfigParser
import os
import re,time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.events import EVENT_JOB_EXECUTED,EVENT_JOB_ERROR
# from apscheduler.triggers.cron.expressions import
from apscheduler.events import JobEvent
from apscheduler.jobstores.memory import MemoryJobStore

timez = pytz.timezone('Asia/Shanghai')


def my_job():
    print 'hello world'


def my_listener(event):
    if event.exception:
        print('The job crashed :(') # or logger.fatal('The job crashed :(')
    else:
        print('The job worked :)')
        print event.job_id
        print event.scheduled_run_time.strftime("%Y-%m-%d %H:%M:%S")


executors = {
    'default': ThreadPoolExecutor(10),
    'processpool': ProcessPoolExecutor(3)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
scheduler = BackgroundScheduler(timezone=timez)
scheduler.add_listener(my_listener)
scheduler.add_job(func=my_job, trigger='interval', seconds=2, id='my_job')
# scheduler.add_job(func=my_job, trigger='cron', minute="11,12,13", id='my_job')

scheduler.start()

try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
