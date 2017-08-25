# _*_ coding:utf-8 _*_
# author:@shenyi
import datetime
import re
import ConfigParser
import requests
import os
import time
from selenium import webdriver
from log import Logger
from sqldb.sqlitecontroller import *
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


conf = ConfigParser.ConfigParser()
conf_path = re.search('\S*myadvl', os.path.dirname(__file__)).group() +'\\conf\\myadvl.ini'
conf.read(conf_path)
phantomjs = conf.get('path', 'PhantomJS')
# print phantomjs


class GetProxyIP:

    def __init__(self):
        self.ipsRank_href = []
        self.nowDays = datetime.datetime.today().strftime('%Y-%m-%d')
        self.driver = webdriver.PhantomJS(phantomjs)
        self.driver.implicitly_wait(30)

    def getProxy_goubanjia(self):
        """
        http://www.goubanjia.com/
        :return:
        """
        for i in range(1, 10):
            nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.driver.get('http://www.goubanjia.com/index%s.shtml' % i)
            url = 'http://www.goubanjia.com/index%s.shtml' % i
            site_name = self.driver.find_element_by_xpath('//div[@class="entry entry-content"]/h4').text.encode('utf-8')
            if self.nowDays in site_name:
                proxy_ranks_trs = self.driver.find_elements_by_xpath('//div[@class="entry entry-content"]//tbody/tr')
                for ip_info in proxy_ranks_trs:
                    ip_port = ip_info.find_element_by_xpath('.//td[@class="ip"]').text.encode('utf-8')  # 非得把ip分开显示
                    proxy_level = ip_info.find_element_by_xpath('.//td[2]').text.encode('utf-8')
                    proxy_type = ip_info.find_element_by_xpath('.//td[3]').text.encode('utf-8')
                    location = ip_info.find_element_by_xpath('.//td[4]').text.encode('utf-8')
                    remarks = ip_info.find_element_by_xpath('.//td[5]').text.encode('utf-8')
                    column = {
                        'proxyip': ip_port,
                        'create_time': nowTime,
                        'proxy_type': proxy_type,
                        'proxy_level': proxy_level,
                        'location': location,
                        'site_name': site_name,
                        'url': url,
                        'remarks': remarks
                    }
                    insertData('proxy', **column)
                    time.sleep(0.2)

            # print len(ipsRank)

    def closeDriver(self):
        self.driver.quit()

    def page2IPBysele(self):
        iplog = '.\\datas\\{}.log'.format(self.nowDays)
        try:
            if not os.path.isfile(iplog):
                open(iplog, 'w').close()
            iplog = open(iplog, 'w')
            if not self.ipsRank_href:
                self.getProxyPage()
            for i in self.ipsRank_href:
                self.driver.get(i[1])
                ipText = self.driver.find_element_by_xpath('//div[@class="content"]/p[2]').text.encode('utf-8')
                print ipText
                iplog.write(ipText)
                iplog.write('\r\n')
                iplog.flush()
            iplog.close()
        except Exception as e:
            # TODO 之后再配置日志系统
            print e
        finally:
            iplog.close()
            self.closeDriver()

    def page2IPByRequests(self):
        if not self.ipsRank_href:
            self.getProxyPage()
        """
        页面请求貌似要验证Referer和cookies，暂时不用这个方法
        """

if __name__ == '__main__':
    p = GetProxyIP()
    p.getProxy_goubanjia()
    # p.page2IPByRequests()
