# _*_ coding:utf-8 _*_
# author:@shenyi
import os
import re
import datetime
import smtplib
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from Adaptors import getconf

mailto_list = getconf.getRecipient()
mail_host = "smtp.sohu.com"  # 设置服务器
mail_user = "ppag0440f2b3f783"  # 用户名
mail_pass = "computer"  # 口令
mail_postfix = "sohu.com"  # 发件箱的后缀
beforday_log = re.search('\S*myadvl', os.path.dirname(__file__)).group() +'\\logs\\log_%s.log' % (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
# print beforday_log


def send_mail(to_list, sub, content):
    """
    :param to_list: 收件人列表
    :param sub: 主题
    :param content: 正文
    :return:
    """
    msg = MIMEMultipart()
    me = "hello" + "<" + mail_user + "@" + mail_postfix + ">"
    part1 = MIMEText(content, 'plain', 'gb2312')
    msg.attach(part1)
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)

    # 发送前一天的日志
    with open(beforday_log, 'r')as h:
        content_attach = h.read()
    log_attach = MIMEText(content_attach, 'plain', 'utf-8')
    log_attach['Content-Type'] = 'application/octet-stream'
    log_attach['Content-Disposition'] = 'attachment;filename="{}"'.format(os.path.split(beforday_log)[1])
    msg.attach(log_attach)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception, e:
        print str(e)
        # print traceback.print_exc()
        return False


if __name__ == '__main__':
    if send_mail(mailto_list, u"我是主题", u"我是正文"):
        print "发送成功"
    else:
        print "发送失败"