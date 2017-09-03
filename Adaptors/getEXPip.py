# -*- coding:utf-8 -*-
import requests
import re
import time


def getExpIp():
    times = 3
    while times:
        data = requests.get('http://httpbin.org/ip', timeout=5)
        if data:
            # print data.text
            real_ip = re.search('[^"]+[\d.]+', data.text).group()
            return real_ip
        else:
            times -= 1
            time.sleep(1)


if __name__ == '__main__':
    getExpIp()

