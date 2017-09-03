# -*- coding:utf-8 -*-
import re
import os
import ConfigParser


def getProjpath():
    coml_ret = re.search('\S*myadvl', os.path.dirname(__file__))
    if coml_ret:
        return coml_ret.group()
    else:
        return False


def getRecipient():
    conf = ConfigParser.ConfigParser()
    conf.read(getProjpath() + '\\conf\\myadvl.ini')
    section = conf.options('mail')
    recipient = []
    for i in section:
        recipient.append(conf.get('mail', i))
    return recipient

if __name__ == '__main__':
    print getRecipient()