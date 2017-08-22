# -*- coding:utf-8 -*-
import sqlite3
import ConfigParser
import re
import os

conf = ConfigParser.ConfigParser()
conf.read(re.search('\S*myadvl', os.path.realpath(__file__)).group() + '\\conf\\myadvl.ini')
sqlite_path = re.search('\S*myadvl', os.path.realpath(__file__)).group() + conf.get('path', 'sqlite')
# sqlite_path = ''
# print sqlite_path


class SqliteInit:

    def __init__(self):
        self.sqlite = sqlite3.connect(sqlite_path)

    def close(self):
        self.sqlite.close()

    def initTable(self):
        curs = self.sqlite.cursor()
        try:
            curs.execute('select * from proxy')
            self.sqlite.commit()
        except sqlite3.OperationalError as e:
            creTable_sql = """create table proxy 
              (id integer primary key,
              pid integer,name varchar(10) UNIQUE,
              nickname text NULL)
            """
            curs.execute(creTable_sql)

if __name__ == '__main__':
    sql = SqliteInit()
    sql.initTable()
    pass