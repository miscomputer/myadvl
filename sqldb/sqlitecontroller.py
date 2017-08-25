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
            creProxy_sql = """create table proxy
              (id integer primary key autoincrement,
              proxyip VARCHAR (20) NOT NULL,
              create_time DATETIME NOT NULL,
              verify_time DATETIME,
              proxy_type text,
              proxy_level text,
              location text,
              site_name VARCHAR(20),
              url VARCHAR (50),
              useable INTEGER (10),
              remarks text,
              others text)
            """
            curs.execute(creProxy_sql)

            creIP_sql = """create table ip
            (id integer primary key autoincrement,
            ip VARCHAR (20) NOT NULL UNIQUE,
            response_time FLOAT (8),
            timout_count INTEGER (4)
            )
            """
            curs.execute(creIP_sql)
            log.info('数据库初始化，完成表创建')
        except Exception as e:
            log.debug(str(e))
        finally:
            self.close()

    def insertData(self):
        curs = self.sqlite.cursor()


def queryData(table, conditions=None, fields='*'):
    """
    解码：str(j).decode('string_escape')
    :param table:
    :param conditions:
    :param fields:
    :return:
    """
    sqlite = sqlite3.connect(sqlite_path)
    curs = sqlite.cursor()
    # 如果fields不是星号，则把里边的字符串按，或空格切开
    column = repr(re.split('[\s,]', fields))[1:-1].replace("'", "")
    if conditions is None:
        select_sql = 'select %s from %s' % (column, table)
    else:
        select_sql = 'select %s from %s %s' % (column, table, conditions)
    # print select_sql
    try:
        curs.execute(select_sql)
    except Exception as e:
        log.error('数据库查询错误: {}'.format(e))
    ret = curs.fetchall()
    sqlite.close()
    return ret


def insertData(table, **kwargs):
    """
    :param table:
    :param kwargs: {column1: value1, column2: value2}
    :return:
    """
    sqlite = sqlite3.connect(sqlite_path, timeout=1)
    sqlite.text_factory = str
    curs = sqlite.cursor()
    fields = kwargs.values()
    insert_sql = 'insert into %s %s values %s' % (table, tuple(kwargs.keys()), tuple(kwargs.values()))
    # print insert_sql
    try:
        curs.execute(insert_sql)
        sqlite.commit()
        log.info('插入{0}表数据'.format(table))
    except Exception as e:
        log.error('数据库插入错误： {0}, INSERT：{1}'.format(str(e), insert_sql))
    finally:
        sqlite.close()


def updataSQL(table, conditions='', **kwargs):
    sqlite = sqlite3.connect(sqlite_path)
    curs = sqlite.cursor()
    fields = []
    for k, v in kwargs.items():
        fields.append('{0}="{1}"'.format(k, v))
    column = repr(fields)[1:-1].replace("'", "")
    updata_sql = 'update %s set %s %s' % (table, column, conditions)
    # print updata_sql
    try:
        curs.execute(updata_sql)
        sqlite.commit()
        log.info('更新{0}表数据： {1}'.format(table, column))
    except Exception as e:
        log.error('数据库更新错误： {0}, UPDATE：{1}'.format(str(e), updata_sql))
    finally:
        sqlite.close()


if __name__ == '__main__':
    sql = SqliteInit()
    table = 'proxy'
    # field = 'proxyip,url'
    # conditions = "where proxyip='127.0.0.3'"
    # ret = queryData(table='proxy', fields=field, conditions=conditions)
    # print ret
    # field = ('proxyip', 'url')
    values = {'proxyip':'12.7.0.0.1', 'create_time': '2017-02-02 12:21:21', 'url': 'www.baidu.com', 'remarks': '备注'}
    # insertData(table, **values)
    ret = queryData('proxy')
    # print str(ret[0][-2]).decode('string_escape')
    # updataSQL(table, conditions, **values)
    for i in ret:
        for j in i:
            print str(j).decode('string_escape')