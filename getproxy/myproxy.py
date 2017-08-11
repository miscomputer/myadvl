# _*_ coding:utf-8 _*_
# author:@shenyi
import datetime
import re
import requests
import os
from selenium import webdriver
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class GetProxyIP:

    def __init__(self):
        self.ipsRank_href = []
        self.nowDays = datetime.datetime.today().strftime('%Y-%m-%d')
        self.driver = webdriver.PhantomJS(r'C:\Python27\phantomjs211\bin\phantomjs.exe')
        self.driver.implicitly_wait(30)

    def getProxyPage(self):
        self.driver.get('http://www.goubanjia.com/dayip_1.shtml')
        ipsRank = self.driver.find_elements_by_xpath('//div[@class="wrap fullwidth"]/div[@class="entry entry-content dayip"]')
        # print len(ipsRank)
        for ips in ipsRank:
            ipsTitle = ips.find_element_by_xpath('./h2/a').text.encode('utf-8')
            # print ipsTitle.encode('utf-8')
            if self.nowDays in ipsTitle:
                link = ips.find_element_by_xpath('./h2/a').get_attribute('href').encode('utf-8')
                self.ipsRank_href.append([ipsTitle, link])

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
    p.page2IPBysele()
    # p.page2IPByRequests()
