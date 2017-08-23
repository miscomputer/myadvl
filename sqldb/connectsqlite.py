# -*- coding:utf-8 -*-
import sqlite3
import ConfigParser
import re
import os
from log import Logger

conf = ConfigParser.ConfigParser()
conf.read(re.search('\S*myadvl', os.path.realpath(__file__)).group() + '\\conf\\myadvl.ini')
sqlite_path = re.search('\S*myadvl', os.path.realpath(__file__)).group() + conf.get('path', 'sqlite')
log = Logger()


class SqliteController:

    def __init__(self):
        self.sqlite = sqlite3.connect(sqlite_path)
        self.__initTable()

    def close(self):
        self.sqlite.close()

    def __initTable(self):
        curs = self.sqlite.cursor()
        try:
            curs.execute('select * from proxy')
            self.sqlite.commit()
        except sqlite3.OperationalError:
            creTable_sql = """create table proxy 
              (id integer primary key autoincrement,
              proxyip VARCHAR (20) NOT NULL,
              create_time DATETIME NOT NULL,
              verify_time DATETIME,
              proxy_type text,
              proxy_level text,
              location text,
              site_name VARCHAR(20),
              url VARCHAR (50),
              remarks text)
            """
            curs.execute(creTable_sql)
            log.info('数据库初始化，完成proxy表创建')
        except Exception as e:
            log.debug(str(e))
        finally:
            self.close()

    def insertData(self):
        curs = self.sqlite.cursor()


def queryData(table, conditions=None, fields='*'):
    sqlite = sqlite3.connect(sqlite_path)
    curs = sqlite.cursor()
    if conditions is None:
        select_sql = 'select %s from %s' % (fields, table)
    else:
        select_sql = 'select %s from %s %s' % (fields, table, conditions)
    curs.execute(select_sql)
    ret = curs.fetchall()
    sqlite.close()
    return ret


if __name__ == '__main__':
    sql = SqliteController()
    field = ('proxyip','url')
    ret = queryData('proxy')
    print ret