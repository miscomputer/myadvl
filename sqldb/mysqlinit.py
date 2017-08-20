# -*- coding:utf-8 -*-
import MySQLdb
import os,re

def creMydb():
    conn = MySQLdb.connect(host='localhost', user='root', passwd='root', port=3306)
    cur = conn.cursor()
    try:
        cur.execute("create database myadvl")
    except Exception as e:
        # print str(e)
        print 'Database myadvl exists!'
    conn.select_db('myadvl')
    cur.execute("DROP TABLE IF EXISTS myproxy")
    try:
        cre_sql = """CREATE TABLE MYPROXY (
                 id INT(4) PRIMARY KEY auto_increment NOT NULL,
                 proxyip VARCHAR (20) NOT NULL,
                 create_time VARCHAR (20) NOT NULL,
                 verify_time DATETIME,
                 proxy_type text,
                 proxy_level text,
                 location text,
                 site_name VARCHAR(20),
                 url VARCHAR (50),
                 remarks text
                 )"""
        cur.execute(cre_sql)
    except Exception as e:
        print e
        print('The table proxyip exists!')


def connDB():
    conn = MySQLdb.connect(host='localhost',user='root',passwd='root',db='test',port=3306)
    cur = conn.cursor()
    cur.execute("select * from test")
    ret = cur.fetchall()
    print ret

if __name__ == '__main__':
    # path = re.search('\S*myadvl', os.path.dirname(__file__))
    # print path.group()
    creMydb()