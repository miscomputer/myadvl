# _*_ coding:utf-8 _*_
# author:@shenyi
import ConfigParser
import datetime
import os
import re
import sys
import time
import pymysql
from selenium import webdriver
from Adaptors.log import Logger
from sqldb.mysqlController import getMySql
reload(sys)
sys.setdefaultencoding('utf-8')

log = Logger()
conf = ConfigParser.ConfigParser()
conf_path = re.search('\S*myadvl', os.path.dirname(__file__)).group() +'\\conf\\myadvl.ini'
conf.read(conf_path)
PHANTOMJS = conf.get('path', 'PhantomJS')
PNG_PATH = re.search('\S*myadvl', os.path.dirname(__file__)).group() + conf.get('path', 'screenshotSave')


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
        conn = getMySql()
        cur = conn.cursor()
        self.driver.get('http://www.goubanjia.com')
        server_showtime = self.driver.find_element_by_xpath('//div[@class="entry entry-content"]/h4').text.encode('utf-8')
        refresh_time = re.search('\d{4}.+[\s]', server_showtime)
        if refresh_time:
            log.info('goubanjia ip 更新时间：{}'.format(refresh_time.group()))
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
                    后期如果遇到mysql性能瓶颈，修改成获取所有代理IP后，一次写入
                '''
                try:
                    proxy_ranks_trs = self.driver.find_elements_by_xpath('//div[@class="entry entry-content"]//tbody/tr')
                    for ip_info in proxy_ranks_trs:
                        ip_port = ip_info.find_element_by_xpath('.//td[@class="ip"]').text.encode('utf-8')  # 非得把ip分开显示
                        proxy_level = ip_info.find_element_by_xpath('.//td[2]').text.encode('utf-8')
                        proxy_type = ip_info.find_element_by_xpath('.//td[3]').text.encode('utf-8')
                        if 'https' in proxy_type:
                            proxy_type = 'https'
                        location = ip_info.find_element_by_xpath('.//td[4]').text.encode('utf-8')
                        remarks = ip_info.find_element_by_xpath('.//td[5]').text.encode('utf-8')
                        insert_proxy_sql = """INSERT INTO PROXY (proxyip,create_time,proxy_type,proxy_level,location,site_name,url,remarks
                                                        ) values(
                                                        '%s','%s','%s','%s','%s','%s','%s','运营商：%s'
                                                        )""" % (
                                        ip_port, nowTime, proxy_type, proxy_level, location, site_name, url, remarks)
                        insert_ip_sql = 'INSERT INTO IP (ip,proxy_type,proxy_level) VALUES ("%s","%s","%s")' % (ip_port, proxy_type, proxy_level)
                        try:
                            cur.execute(insert_proxy_sql)
                            if proxy_type:  # 如果代理类型为空，则不写入ip表
                                cur.execute(insert_ip_sql)
                            conn.commit()
                        except pymysql.err.IntegrityError:
                            log.warn('重复IP不入库：%s（%s）' % (url, ip_port))
                        except Exception as e:
                            conn.rollback()
                            log.error('插入代理IP数据失败，回滚插入事务：{0} {1}'.format(e, ip_port))
                except Exception as e:
                    time_stamp = int(time.time())
                    self.driver.save_screenshot(PNG_PATH + '\\{}.png'.format(time_stamp))
                    log.error('页面元素获取失败(截屏日志{0})：{1}'.format(time_stamp, url))
                    log.debug(str(e))
        log.info('"goubanjia"网站代理ip获取完成')
        conn.close()
        self.closeDriver()
        log.info('关闭driver和数据库')

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
