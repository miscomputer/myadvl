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


class SqliteInit:

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
              create_time DATETIME,
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
    # 如果fields不是星号，则把里边的字符串按，或空格切开
    column = repr(re.split('[\s,]', fields))[1:-1].replace("'", "")
    if conditions is None:
        select_sql = 'select %s from %s' % (column, table)
    else:
        select_sql = 'select %s from %s %s' % (column, table, conditions)
    print select_sql
    try:
        curs.execute(select_sql)
    except Exception as e:
        log.error('查询错误: {}'.format(e))
    ret = curs.fetchall()
    sqlite.close()
    return ret


def insertData(table, **kwargs):
    sqlite = sqlite3.connect(sqlite_path)
    curs = sqlite.cursor()
    insert_sql = 'insert into %s %s values %s' % (table, fields, values)  # FIXME 字典改成字段和值
    print insert_sql
    curs.execute(insert_sql)
    sqlite.commit()


if __name__ == '__main__':
    sql = SqliteInit()
    table = 'proxy'
    # field = 'proxyip,url'
    conditions = 'where proxyip="1"'
    # ret = queryData(table='proxy', fields=field, conditions=conditions)
    # print ret
    field = ('proxyip', 'url')
    # values = (2, 3)
    insertData(table,*field,values=(2,3))