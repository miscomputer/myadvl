# _*_ coding:utf-8 _*_
# author:@shenyi
import ConfigParser
import datetime
import os
import re
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.proxy import ProxyType

from Adaptors.log import Logger
from sqldb.mysqlController import getMySql

conf = ConfigParser.ConfigParser()
conf_path = re.search('\S*myadvl', os.path.dirname(__file__)).group() +'\\conf\\myadvl.ini'
conf.read(conf_path)
PHANTOMJS = conf.get('path', 'PhantomJS')
log = Logger()


class ProxyCheck:

    def __init__(self):
        self.nowdays = datetime.datetime.today().strftime('%Y-%m-%d')
        self.driver = webdriver.PhantomJS(PHANTOMJS)
        self.driver.implicitly_wait(30)
        self.ips = []

    def getProxyIp(self):
        conn = getMySql()
        cur = conn.cursor()
        select_ip_sql = 'select ip,proxy_type,proxy_level from ip'
        cur.execute(select_ip_sql)
        self.ips = cur.fetchall()

    def effectiveIPbyRequests(self):
        print self.ips
        for line in self.ips:
            # print line,
            server = re.search(r'\d.*\d.*\d.*\d.*:\d{1,5}', line)
            if server:
                proxyip = server.group()
                # print proxyip
                # data = requests.get(url='http://httpbin.org/ip',  proxies={"https": "http://{}".format(proxyip)}, timeout=5)
                data = requests.get(url='http://httpbin.org/ip',  proxies={"http": "http://221.5.45.246:808"}, timeout=10,hearder=None)
                if data.status_code == 200:
                    # effectivePorxy.append(proxyip)
                    print data.text
                    yield proxyip
                    time.sleep(1)

    def effectiveIPbysele(self):
        effectivePorxy = []
        proxy = webdriver.Proxy()
        proxy.proxy_type = ProxyType.MANUAL
        # proxy.http_proxy = "121.56.37.12:80"
        proxy.http_proxy = "https://91.199.99.14:3128"
        proxy.add_to_capabilities(webdriver.DesiredCapabilities.PHANTOMJS)
        self.driver.start_session(webdriver.DesiredCapabilities.PHANTOMJS)
        self.driver.get('http://httpbin.org/ip')
        print self.driver.page_source
        time.sleep(1)


def verityByReq(*proxy):
    """
    验证代理IP是否有效
    验证前需要确定已创建内存表
    :param proxy: ('111.13.7.42:843', 'http', '匿名')
    :return:
    """
    conn = getMySql()
    cur = conn.cursor()
    ip = proxy[0]
    proxy_type = proxy[1]
    proxy_level = proxy[2]
    baseHeaders = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'GBK,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7'
    }
    try:
        data = requests.get(url='http://httpbin.org/ip', proxies={'{}'.format(proxy_type): '{0}://{1}'.format(proxy_type,ip)}, headers=baseHeaders, timeout=10)
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 如果状态返回200，更新ip内存表
        if data.status_code == 200:
            response_time = float(data.elapsed.microseconds) / 10**6
            real_ip = re.search('[^"]+[\d.]+', data.text).group()
            update_sql = """update tmp_memory_verifyIp 
            set response_time = '{0}',
            verify_time = '{1}',
            others = 'real_ip:{2}|',
            verify_count = verify_count + 1
            where ip='{3}'
            """.format(response_time, nowTime, real_ip, ip)
            try:
                cur.execute(update_sql)
            except Exception as e:
                log.error('验证返回200，更新ip内存表失败：{}'.format(e))
        else:
            log.warn('代理ip {0} 响应状态为：{1}'.format(ip, data.status_code))
        data.close()
    except Exception as e:
        if 'Timeout' in e:
            log.info('代理验证超时:{}'.format(ip))
            update_sql = """update tmp_memory_verifyIp
                    set timout_count = timout_count + 1,
                    verify_count = verify_count + 1
                    where ip = '{}'
                    """.format(ip)
            try:
                cur.execute(update_sql)
            except Exception as e:
                log.error('验证超时，写入timeout_count字段失败：{}'.format(e))
        else:
            log.warn('验证代理错误：{}'.format(e))
    finally:
        log.info('代理ip验证完成')
        conn.close()


if __name__ == '__main__':
    ip = ProxyCheck()
    # proxy = ('210.38.1.143:80', 'http', '匿名')

    conn = getMySql()
    cur = conn.cursor()
    select_sql = 'select ip, proxy_type, proxy_level from tmp_memory_verifyip'
    cur.execute(select_sql)
    ret = cur.fetchall()
    for i in ret:
        verityByReq(*i)
        print '--'

    # ips = ip.effectiveIPbyRequests()
    # for ip in ips:
    #     print ip
    # ip.getProxyIp()
    # for i in ip.ips:
    #     for j in i:
    #         print j,
    #     print ''