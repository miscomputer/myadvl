# -*- coding:utf-8 -*-
import ConfigParser
import os
import re

conf = ConfigParser.ConfigParser()
conf_path = re.search('\S*myadvl', os.path.dirname(__file__)).group() +'\\conf\\myadvl.ini'
conf.read(conf_path)
phantomjs = conf.get('path', 'PhantomJS')
print phantomjs