# _*_ coding:utf-8 _*_
# author:@shenyi
import logging
import os
import inspect
import ctypes
import re
import datetime

STD_OUTPUT_HANDLE = -11
FOREGROUND_WHITE = 0x0007
FOREGROUND_BLUE = 0x01  # text color contains blue.
FOREGROUND_GREEN = 0x02  # text color contains green.
FOREGROUND_RED = 0x04  # text color contains red.
FOREGROUND_INTENSITY = 0x08 # text color is intensified.
FOREGROUND_YELLOW = FOREGROUND_RED | FOREGROUND_GREEN

BACKGROUND_BLUE = 0x10  # background color contains blue.
BACKGROUND_GREEN = 0x20  # background color contains green.
BACKGROUND_RED = 0x40  # background color contains red.
BACKGROUND_INTENSITY = 0x80  # background color is intensified.

nowDays = datetime.datetime.today().strftime('%Y-%m-%d')
log_path = re.search('\S*myadvl', os.path.dirname(__file__)).group()


def set_color(color, handle=ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)):
    bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return bool


class Logger:
    def __init__(self):
        path = log_path + '\\logs\\log_%s.log' % nowDays
        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        self.logger.addHandler(sh)
        fh = logging.FileHandler(path)
        fh.setFormatter(fmt)
        self.logger.addHandler(fh)
        self.case_result = True

    def __getLogInfo(self):
        try:
            _file, line = inspect.stack()[2][1:3]
            return 'file:%s line:%s' % (os.path.basename(_file), line)
        except:
            return ''

    def debug(self, *data):
        data = len(data) == 1 and data[0] or ' '.join(map(str, data))
        loginfo = self.__getLogInfo()
        data = '%s %s' % (loginfo, data)
        self.info(data, logging.DEBUG, FOREGROUND_WHITE | FOREGROUND_INTENSITY)

    def error(self, data, color=FOREGROUND_RED):
        loginfo = self.__getLogInfo()
        data = '%s %s' % (loginfo, data)
        self.info(data, logging.ERROR, color | FOREGROUND_INTENSITY)
        self.case_result = False

    def fatal(self, data, color=FOREGROUND_GREEN):
        self.info(data, logging.FATAL)

    def info(self, data, level=logging.INFO, color=FOREGROUND_GREEN):
        set_color(color | FOREGROUND_INTENSITY)
        self.logger.log(level, data)
        set_color(FOREGROUND_WHITE)

    def warn(self, data, color=FOREGROUND_YELLOW):
        self.info(data, logging.WARN, color | FOREGROUND_INTENSITY)


def logging_base():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='{0}\\logs\\{1}_taskInfo.log'.format(log_path, nowDays),
                        filemode='a')


if __name__ == '__main__':
    log = Logger()
    log.info(data='test')
    log.error(data='test')