# -*- coding:utf-8 -*-
import ConfigParser
import os
import re

values = {'proxyip': '127.0.0.1', 'url': 'www.baidu.com', 'create_time': '2017-08-21 00:34:31'}

column = []
for k,v in values.items():
    column.append('{0} = {1}'.format(k,v))
print repr(column)[1:-1]