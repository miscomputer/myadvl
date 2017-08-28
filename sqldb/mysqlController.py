# -*- coding:utf-8 -*-
import pymysql
import ConfigParser
import re
import os
from log import Logger

log = Logger()

conf = ConfigParser.ConfigParser()
conf_path = re.search('\S*myadvl', os.path.dirname(__file__)).group() + '\\conf\\myadvl.ini'
conf.read(conf_path)
DB_HOST = conf.get('mysql', 'ip')
DB_USER = conf.get('mysql', 'user')
DB_PWD = conf.get('mysql', 'password')
DB_PORT = conf.get('mysql', 'port')
DB_NAME = conf.get('mysql', 'dbName')


def creMydb():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PWD, port=3306, charset='utf8')
    cur = conn.cursor()
    cur.execute('show databases')
    databases = cur.fetchall()
    creDB = True
    for db in databases:
        if 'myadvl' == db[0]:
            creDB = False
            break
    if creDB:
        try:
            cur.execute("create database myadvl")
            log.info('创建myadvl数据库')
        except Exception as e:
            log.error('数据库myadvl创建失败: %s' % e)
    conn.select_db('myadvl')
    # cur.execute("DROP TABLE IF EXISTS PROXY")
    try:
        cre_sql = """CREATE TABLE IF NOT EXISTS PROXY(
              id integer primary key auto_increment ,
              proxyip VARCHAR (30) NOT NULL,
              create_time DATETIME NOT NULL,
              verify_time DATETIME,
              proxy_type VARCHAR (10),
              proxy_level VARCHAR (10),
              location text,
              site_name VARCHAR(50),
              url VARCHAR (50),
              useable INTEGER (10),
              remarks text,
              others text)"""
        cur.execute(cre_sql)
        log.info('数据表proxy创建完成')
    except Exception as e:
        log.error('数据表proxy创建失败： {}'.format(e))
    cur.execute("DROP TABLE IF EXISTS ip")
    try:
        # success_rate: 验证成功率内存数据表(verify_count - timeout_count / verify_count),计算后写到ip表
        creIP_sql = """create table ip
        (id integer primary key auto_increment,
        ip VARCHAR (30) NOT NULL UNIQUE,
        response_time FLOAT (8),
        proxy_type VARCHAR (10),
        proxy_level VARCHAR (10),
        success_rate FLOAT  (8),
        timout_count INTEGER (4)
        )
        """
        cur.execute(creIP_sql)
        log.info('数据表ip创建完成')
    except Exception as e:
        log.error('数据表ip创建失败： {}'.format(e))
    finally:
        conn.close()


def getMySql():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PWD, port=int(DB_PORT), db=DB_NAME, charset='utf8')
    return conn


def creMemTable(tableName, columns):
    """
    :param tableName:
    :param columns:  '''(id int(10),num int(10))'''
    :return:
    """
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PWD, port=int(DB_PORT), db=DB_NAME, charset='utf8')
    cur = conn.cursor()
    creMem_sql = "CREATE TABLE if NOT EXISTS %s %s ENGINE=MEMORY DEFAULT CHARSET=utf8" % (tableName, columns)
    try:
        cur.execute(creMem_sql)
        log.info('创建内存数据表 %s' % tableName)
        return True
    except Exception as e:
        log.error('创建内存数据表%s失败: %s' % (tableName,e))
        log.error(creMem_sql)
        return False
    finally:
        conn.close()


def creMemIPtable():
    """
    每日4点、12点、20点：将ip表的ip数据放到内存表,从内存表取IP，不在这个方法里
    :return:
    """
    conn = getMySql()
    cur = conn.cursor()
    tableName = 'tmp_memory_verifyIp'
    columns = """(
        id integer primary key auto_increment,
        ip VARCHAR (30) NOT NULL UNIQUE,
        verify_time DATETIME,
        verify_count INTEGER (4) DEFAULT 0,
        response_time FLOAT (8),
        proxy_type VARCHAR (10),
        proxy_level VARCHAR (10),
        timout_count INTEGER (4) DEFAULT 0,
        others VARCHAR (50)
        )
        """
    ret = creMemTable(tableName, columns)
    if ret:
        insert_sql = """
        insert into tmp_memory_verifyIp
        (ip,proxy_type,proxy_level) select 
        ip,proxy_type,proxy_level from ip
        """
        try:
            cur.execute(insert_sql)
            log.info('ip写入tmp_memory_verifyIp表成功')
        except Exception as e:
            log.error('ip写入tmp_memory_verifyIp表失败：{}'.format(e))
    conn.close()

if __name__ == '__main__':
    # creMydb()
    creMemIPtable()