# -*- coding:utf-8 -*-
import MySQLdb
from log import Logger

log = Logger()


def creMydb():
    conn = MySQLdb.connect(host='localhost', user='root', passwd='root', port=3306, charset='utf8')
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
    cur.execute("DROP TABLE IF EXISTS PROXY")
    try:
        cre_sql = """CREATE TABLE PROXY (
              id integer primary key auto_increment ,
              proxyip VARCHAR (30) NOT NULL,
              create_time DATETIME NOT NULL,
              verify_time DATETIME,
              proxy_type text,
              proxy_level text,
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
        creIP_sql = """create table ip
        (id integer primary key auto_increment,
        ip VARCHAR (20) NOT NULL UNIQUE,
        response_time FLOAT (8),
        timout_count INTEGER (4)
        )
        """
        cur.execute(creIP_sql)
        log.info('数据表ip创建完成')
    except Exception as e:
        log.error('数据表ip创建失败： {}'.format(e))
    finally:
        conn.close()


if __name__ == '__main__':
    creMydb()
