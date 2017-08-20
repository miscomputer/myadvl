# -*- coding:utf-8 -*-
import MySQLdb

class connMydb:

    def __init__(self):
        self.conn = MySQLdb.connect(host='localhost', user='root', passwd='root', port=3306, db='myadvl')

    def closeDB(self):
        self.conn.close()

    def insertData(self, table, **kwargs):
        curs = self.conn.cursor()
        print tuple(kwargs.keys())
        insert_sql = "INSERT INTO {0}{1}VALUES {2}".format(table, tuple(kwargs.keys()), tuple(kwargs.values()))
        print insert_sql
        curs.executemany(insert_sql, kwargs.items())
        self.conn.commit()
        self.closeDB()

    def test(self):
        curs = self.conn.cursor()
        v = {
                'name': '127.0.0.2',
                'key': '2017-08-21 00:34:31'
            }

        try:
            # curs.executemany("insert into myproxy('proxyip', 'create_time') values ('127.0.0.2', 'aaa'),")

            curs.execute('insert into test ("name","key")values ("127.0.0.2","2017-08-21 00:34:31"),%s' % v)
            # curs.execute("select * from myproxy")
            # ret = curs.fetchall()
            # print ret
            self.conn.commit()
        except Exception as e:
            print e
            self.conn.rollback()
        finally:
            self.closeDB()

if __name__ == '__main__':
    conn = connMydb()
    fields = {
        'proxyip':'127.0.0.1',
        'create_time':'2017-08-21 00:34:31'
    }

    # conn.insertData('myproxy', **fields)
    conn.test()

