from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr

import sys
import web
import os
from git import Repo
import json
import smtplib

dirfile = r'D:\loonflow\pygit_hook'
urls = ('/update_server', 'update',
        '/send_mail', 'mail_server')
app = web.application(urls, globals())

class mailPool:
    def __init__(self) -> None:
        mail_pool = {'chenduping1@163.com':'smtp.163.com,BHNEBAWLSVXVGRZR',
                     'dict_007@163.com':'smtp.163.com,XOIPZIKIHTUZKZCR',
                     'exa160@139.com':'smtp.139.com,7b1970c65748aa039700',
                     }
        self.today = time.time.
        self.mail_server  = []
        self.mail_cnt = []
        self.mail_succ_cnt = []
        for mail_addr, mail_msg in mail_pool.items():
            mail_serveraddr = mail_msg.split(',')[0]
            mail_pass = mail_msg.split(',')[1]
            server=smtplib.SMTP_SSL(mail_serveraddr, 465)
            server.login(mail_addr, mail_pass)
            self.mail_server.append(server)
            self.mail_cnt.append(0)
            self.mail_succ_cnt.append(0)


    def get_pool(self):
        return self.mail_server

    def get_server(self):
        print(f'mcnt:{str(self.mail_cnt)}')
        index = self.mail_cnt.index(min(self.mail_cnt))
        return self.mail_server[index], index

    def send_mail(self, sender_list, msg):
        try_cnt = 0
        while try_cnt < 3:
            server, index = self.get_server()
            self.mail_cnt[index] += 1
            try_cnt += 1
            try:
                self.mail_sender(server, sender_list, msg)
                self.mail_succ_cnt[index] += 1
                break
            except Exception as e:
                print(e)

    @staticmethod
    def mail_sender(server, sender_list, msg):
        ser_name = server.auth_login()
        msg['From'] =formataddr(["DICT工单平台",ser_name])
        print(sender_list)
        msg['To'] = ';'.join(sender_list)
        print(msg['To'])
        try:
            server.sendmail(msg['From'], sender_list, msg.as_string())
        except smtplib.SMTPServerDisconnected as e:
            ser_pwd = server.auth_login(True)
            server=smtplib.SMTP_SSL(server._host, 465)  # 发件人邮箱中的SMTP服务器
            server.login(ser_name, ser_pwd)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(msg['From'], sender_list, msg.as_string())

            

mail_sender = mailPool()

class update:
    def POST(self):
        i = json.loads(web.data())
        if i.get('token') == 'mxu3nv74oiy7vi34n89xnf982bv824tdf34':
            
            repo = Repo(dirfile)
            g = repo.git
            i = 0
            while i < 5:
                i += 1
                try:
                    g.push()
                except Exception as e:
                    print(e)
                else:
                    print("Successful pull!")
                    return 'success'
                    break


class mail_server:
    def POST(self):
        paramsss = json.loads(web.data())
        # print(paramsss)
        # print(str(web.ctx.env))
        title_result = paramsss.get('title_result')
        last_state = paramsss.get('last_flow_log')
        participant_info_list = paramsss.get('participant_info_list')
        ticket_value_info = paramsss.get('ticket_value_info')
        last_state_name = last_state.get('state').get('state_name')
        last_participant_name = last_state.get('participant_info').get('participant_alias')
        content_result = paramsss.get('content_result')
        ticket_sn = ticket_value_info.get('sn')
        subject = '工单提醒:{}'.format(title_result)
        mail_receivers = [formataddr(parseaddr('{}<{}>'.format(info.get('alias'), info.get('email')))) for info in participant_info_list]
        html_message = f"""<h2>{title_result}</h2><br>
                           {content_result}<br><br>工单来自:{last_state_name}，处理人:{last_participant_name}，流水号：{ticket_sn}<br>请访问<a href="http://47.100.59.169:10000/" target=blank>工单平台：http://47.100.59.169:10000/</a>进行处理"""
            
        html_message = """<H>{}</H></br>\n
                        来源:{},上一步处理人:{}</br>
                        {}</br>""".format(title_result, last_state_name, last_participant_name, content_result)
        message = MIMEText(html_message, 'html', 'utf-8')
        message['Subject'] = subject
        mail_sender.send_mail(mail_receivers, message)


if __name__ == '__main__':
    sys.argv.append('10001')
    app.run()
