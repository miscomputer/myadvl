# _*_ coding:utf-8 _*_
# author:@shenyi
import requests
import datetime
import re
import time
from selenium import webdriver
from selenium.webdriver.common.proxy import ProxyType


class ProxyCheck:

    def __init__(self):
        self.nowdays = datetime.datetime.today().strftime('%Y-%m-%d')
        self.driver = webdriver.PhantomJS(r'C:\Python27\phantomjs211\bin\phantomjs.exe')
        self.driver.implicitly_wait(30)

    def effectiveIPbyRequests(self):
        effectivePorxy = []
        try:
            proxyServer = open('.\\datas\\{}.log'.format(self.nowdays))
        except Exception as e:
            print e
        for line in proxyServer.readlines():
            # print line,
            server = re.search(r'\d.*\d.*\d.*\d.*:\d{1,5}', line)
            if server:
                proxyip = server.group()
                # print proxyip
                # data = requests.get(url='http://httpbin.org/ip',  proxies={"https": "http://{}".format(proxyip)}, timeout=5)
                data = requests.get(url='http://httpbin.org/ip',  proxies={"http": "http://221.5.45.246:808"}, timeout=10)
                if data.status_code == 200:
                    # effectivePorxy.append(proxyip)
                    print data.text
                    yield proxyip
                    time.sleep(1)

    def effectiveIPbysele(self):
        effectivePorxy = []
        try:
            proxyServer = open('.\\datas\\{}.log'.format(self.nowdays))
        except Exception as e:
            print e
        for line in proxyServer.readlines():
            # print line,
            server = re.search(r'\d.*\d.*\d.*\d.*:\d{1,5}', line)
            if server:
                proxyip = server.group()
                proxy = webdriver.Proxy()
                proxy.proxy_type = ProxyType.MANUAL
                # proxy.http_proxy = "121.56.37.12:80"
                proxy.http_proxy = "221.5.45.246:808"
                proxy.add_to_capabilities(webdriver.DesiredCapabilities.PHANTOMJS)
                self.driver.start_session(webdriver.DesiredCapabilities.PHANTOMJS)
                self.driver.get('http://httpbin.org/ip')
                print self.driver.page_source
                time.sleep(1)


if __name__ == '__main__':
    ip = ProxyCheck()
    # ips = ip.effectiveIPbyRequests()
    # for ip in ips:
    #     print ip
    import threading
    pool = []
    for i in range(30):
        pool.append(threading.Thread(target=ip.effectiveIPbysele))
    for i in pool:
        i.start()
