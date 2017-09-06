# _*_ coding:utf-8 _*_
# author:@shenyi
import time
import datetime
import pytz
from sqldb.mysqlController import getMySql
from Adaptors.getconf import getRecipient
from apscheduler import events
from apscheduler.schedulers.background import BackgroundScheduler
from Adaptors.log import Logger
from Adaptors.log import logging_base
from sendmail import send_mail
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from Adaptors.getEXPip import getExpIp
from getproxy.myproxy import GetProxyIP
from Queue import Queue


# timez = pytz.timezone('Asia/Shanghai')
taskLog = logging_base()
log = Logger()
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(3)
}

job_defaults = {
    'apscheduler.executors.processpool': {
        'type': 'processpool',
        'max_workers': '15'
    },
    'apscheduler.job_defaults.coalesce': 'false',
    'apscheduler.job_defaults.max_instances': '5',
    'apscheduler.timezone': 'Asia/Shanghai',
}

scheduler = BackgroundScheduler(executors=executors,job_defaults=job_defaults)
q = Queue()
exp_ip = '1.1.1.1'


def sendMail():
    mailto_list = getRecipient()
    send_mail(mailto_list, u"每日邮件日志", u"每日邮件日志")

tfunc_threads_count = 0
all_threads_count = 0


def tFunc():
    # if not q.empty():
    #     print 'tfunc:%s' % q.get()
    # print 'inner start time:%s' % datetime.datetime.now().strftime('%H:%M:%S')
    a = 3
    b = 1
    # print 'inner executed time:%s' % datetime.datetime.now().strftime('%H:%M:%S')
    time.sleep(10)
    return a/b


def job_max_instance_listener(ev):
    conn = getMySql()
    cur = conn.cursor()
    nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if ev.code == 2 ** 16:
        insert_maxinstance_sql = """insert into task
                                (task_type,task_description,run_status,start_time) VALUES 
                                ('{0}','已到最大线程数','maxInstance:{0}','{1}')
        """.format(ev.job_id, nowTime)
        try:
            cur.execute(insert_maxinstance_sql)
            conn.commit()
            log.warn('执行的任务已到最大线程数，{}未加载到任务'.format(ev.job_id))
        except Exception as e:
            log.error('EVENT_JOB_MAX_INSTANCES写入task表失败')
            log.error(str(e))
    cur.close()
    conn.close()


def job_listener(ev):
    conn = getMySql()
    cur = conn.cursor()
    if ev.exception:
        if ev.code == 2 ** 13:  # EVENT_JOB_ERROR
            insert_jobErr_sql = """insert into task 
                                (task_type,task_description,run_status,start_time) VALUES 
                                ('{1}','任务执行错误','EVENT_JOB_ERROR: {0}','{2}')
            """.format(ev.exception, ev.job_id, ev.scheduled_run_time.strftime('%Y-%m-%d %H:%M:%S'))
            try:
                cur.execute(insert_jobErr_sql)
                conn.commit()
                log.error('{} 执行失败，已写入数据表'.format(ev.job_id))
            except Exception as e:
                log.error('EVENT_JOB_ERROR写入task表失败')
                log.error(str(e))
    else:
        if ev.code == 2 ** 14:  # EVENT_JOB_MISSED
            insert_jobMiss_sql = """insert into task                                
                                (task_type,task_description,run_status,start_time) VALUES 
                                ('{0}','任务执行错过','EVENT_JOB_MISSED','{1}')
            """.format(ev.job_id, ev.scheduled_run_time.strftime('%Y-%m-%d %H:%M:%S'))
            try:
                cur.execute(insert_jobMiss_sql)
                conn.commit()
                log.warn('{} 错过本次执行，已写入数据表'.format(ev.job_id))
            except Exception as e:
                log.error('EVENT_JOB_MISSED写入task表失败')
                log.error(str(e))

        elif ev.code == 2 ** 12:  # EVENT_JOB_EXECUTED
            global exp_ip
            nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if ev.job_id == 'proxy_check':
                insert_jobEXEC_sql = """insert into task
                                    (task_type,task_description,exp_ip,run_status,start_time,end_time) VALUES 
                                    ('{0}','代理ip检测','{1}','EVENT_JOB_EXECUTED','{2}','{3}')
                """.format(ev.job_id, exp_ip, ev.scheduled_run_time.strftime('%Y-%m-%d %H:%M:%S'), nowTime)
                try:
                    # print insert_jobEXEC_sql
                    cur.execute(insert_jobEXEC_sql)
                    conn.commit()
                    log.info('任务 {} 已执行'.format(ev.job_id))
                except Exception as e:
                    log.error('EVENT_JOB_EXECUTED写入task表失败')
                    log.error(str(e))
            elif ev.job_id == 'get_EXPip':
                exp_ip = ev.retval
    cur.close()
    conn.close()

getproxy = GetProxyIP()
scheduler.add_job(func=tFunc, trigger='cron', hour=0, minute=30, id='my_mail')  # 每天0点30分发邮件
scheduler.add_job(func=getExpIp, trigger='cron', hour=1, id='get_EXPip')  # 每天1点获取一次外网IP
scheduler.add_job(func=getproxy.getProxy_goubanjia, trigger='cron', hour='3,9,15,21', id='get_goubanjia')  # 每天1点获取一次外网IP


# scheduler.add_job(func=tFunc,trigger='cron', hour=16, minute=45, id='tfunc')
# scheduler.add_job(func=tFunc, trigger='interval', seconds=2, id='proxy_check')
# scheduler.add_job(func=getExpIp, args=(q,), trigger='cron', hour=1, id='exp_ip')  # 获取外网IP


scheduler.add_listener(job_listener, events.EVENT_JOB_ERROR
                       | events.EVENT_JOB_EXECUTED
                       | events.EVENT_JOB_MISSED
                       )

scheduler.add_listener(job_max_instance_listener, events.EVENT_JOB_MAX_INSTANCES
                       | events.EVENT_JOBSTORE_ADDED)


scheduler.start()

try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()

# EVENTS EXCEPTION CODE TABLE
"""
EVENT_SCHEDULER_STARTED = EVENT_SCHEDULER_START = 2 ** 0 = 1    调度程序启动了
EVENT_SCHEDULER_SHUTDOWN = 2 ** 1 = 2   调度程序已关闭
EVENT_SCHEDULER_PAUSED = 2 ** 2 = 4    调度程序中的作业处理已暂停
EVENT_SCHEDULER_RESUMED = 2 ** 3 = 8    调度程序中的作业处理已恢复
EVENT_EXECUTOR_ADDED = 2 ** 4 = 16  执行程序已添加到调度程序
EVENT_EXECUTOR_REMOVED = 2 ** 5 = 32    作业存储从调度程序中删除
EVENT_JOBSTORE_ADDED = 2 ** 6 = 64    	作业存储已添加到调度程序 
EVENT_JOBSTORE_REMOVED = 2 ** 7 = 128   作业存储从调度程序中删除
EVENT_ALL_JOBS_REMOVED = 2 ** 8 = 256   所有作业都从所有作业仓库或一个特定作业存储库中删除
EVENT_JOB_ADDED = 2 ** 9 = 512    作业已添加到作业存储
EVENT_JOB_REMOVED = 2 ** 10 = 1024    作业已从作业存储库中删除
EVENT_JOB_MODIFIED = 2 ** 11 = 2048    作业从调度程序外部修改
EVENT_JOB_EXECUTED = 2 ** 12 = 4096    作业成功执行
EVENT_JOB_ERROR = 2 ** 13 = 8192    作业在执行期间引发异常 
EVENT_JOB_MISSED = 2 ** 14 = 16384    作业的执行错过了
EVENT_JOB_SUBMITTED = 2 ** 15 = 32768    作业被提交给其执行者运行 | 
EVENT_JOB_MAX_INSTANCES = 2 ** 16 = 65536    被提交给其执行者的作业不被执行者接受，因为该作业已经达到最大并发
"""
