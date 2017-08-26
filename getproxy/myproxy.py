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
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


conf = ConfigParser.ConfigParser()
conf_path = re.search('\S*myadvl', os.path.dirname(__file__)).group() +'\\conf\\myadvl.ini'
conf.read(conf_path)
PHANTOMJS = conf.get('path', 'PhantomJS')
DB_HOST = conf.get('mysql', 'ip')
DB_USER = conf.get('mysql', 'user')
DB_PWD = conf.get('mysql', 'password')
DB_PORT = conf.get('mysql', 'port')
DB_NAME = conf.get('mysql', 'dbName')


class GetProxyIP:

    def __init__(self):
        self.ipsRank_href = []
        self.nowDays = datetime.datetime.today().strftime('%Y-%m-%d')
        self.driver = webdriver.PhantomJS(PHANTOMJS)
        self.driver.implicitly_wait(30)

    def getProxy_goubanjia(self):
        """
        http://www.goubanjia.com/
        :return:
        """
        conn = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PWD, port=int(DB_PORT), db=DB_NAME, charset='utf8')
        cur = conn.cursor()
        for i in range(1, 10):
            nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                self.driver.get('http://www.goubanjia.com/index%s.shtml' % i)
                url = 'http://www.goubanjia.com/index%s.shtml' % i
                site_name = self.driver.find_element_by_xpath('//div[@class="entry entry-content"]/h4').text.encode('utf-8')
            except Exception as e:
                log.error('页面打开失败：{}'.format(url))
                log.error(str(e))
            if self.nowDays in site_name:
                '''目前数据处理逻辑是在页面每获取一行代理ip数据，往数据库写入一次
                    后期如果遇到mysql性能瓶颈，修改成获取所有代理IP数据后，一次写入
                '''
                try:
                    proxy_ranks_trs = self.driver.find_elements_by_xpath('//div[@class="entry entry-content"]//tbody/tr')
                    for ip_info in proxy_ranks_trs:
                        ip_port = ip_info.find_element_by_xpath('.//td[@class="ip"]').text.encode('utf-8')  # 非得把ip分开显示
                        proxy_level = ip_info.find_element_by_xpath('.//td[2]').text.encode('utf-8')
                        proxy_type = ip_info.find_element_by_xpath('.//td[3]').text.encode('utf-8')
                        location = ip_info.find_element_by_xpath('.//td[4]').text.encode('utf-8')
                        remarks = ip_info.find_element_by_xpath('.//td[5]').text.encode('utf-8')
                        insert_sql = """insert into PROXY (proxyip,create_time,proxy_type,proxy_level,location,site_name,url,remarks
                                                        ) values(
                                                        '%s','%s','%s','%s','%s','%s','%s','运营商：%s'
                                                        )""" % (
                        ip_port, nowTime, proxy_type, proxy_level, location, site_name, url, remarks)
                        try:
                            cur.execute(insert_sql)
                            conn.commit()
                        except Exception as e:
                            log.error('插入代理IP数据失败：{0} {1}'.format(e, ip_port))
                except Exception as e:
                    log.error('页面元素获取失败：{}'.format(url))
                    log.debug(str(e))
        log.info('"goubanjia"网站代理ip获取完成')
        conn.close()
        self.closeDriver()

    def closeDriver(self):
        self.driver.quit()

    def page2IPByRequests(self):
        pass
        """
        页面请求貌似要验证Referer和cookies，暂时不用这个方法
        """

if __name__ == '__main__':
    p = GetProxyIP()
    p.getProxy_goubanjia()
    # p.page2IPByRequests()
