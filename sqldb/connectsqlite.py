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
    sqlite = sqlite3.connect(sqlite_path)
    curs = sqlite.cursor()
    insert_sql = 'insert into %s %s values %s' % (table, tuple(kwargs.keys()), tuple(kwargs.values()))
    try:
        curs.execute(insert_sql)
        sqlite.commit()
        log.info('插入{0}表数据： {1}'.format(table, kwargs))
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
    conditions = "where proxyip='127.0.0.3'"
    # ret = queryData(table='proxy', fields=field, conditions=conditions)
    # print ret
    field = ('proxyip', 'url')
    values = {'url': 'www.baidu.com', 'remarks': 'beizhu','create_time': 1}
    # insertData(table, **values)

    updataSQL(table, conditions, **values)