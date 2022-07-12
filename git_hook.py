from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr

import sys
import web
from git import Repo
import json
import smtplib
import time


dirfile = r'D:\loonflow\pygit_hook'
# web.py url注册
urls = ('/update_server', 'update',
        '/send_mail', 'mail_server',
        '/send_msg', 'send_msg')
app = web.application(urls, globals())

class mailPool:
    """邮件池
    
    发送邮件通知使用，通过大量个人邮箱实现的通知功能。
    发送成功后计数，轮流使用每一个邮箱。
    邮箱池的第一个邮箱，在每天的第一封邮件触发时，会收到关于前一天的邮件发送情况（不记录在本地，服务重启后记录清空）
    
    attr: 
    """
    def __init__(self) -> None:
        """
        初始化邮件池
        
        attr:
            all_mail:       所有邮箱地址 -> list
            mail_server:    smtplib实例  -> list
            mail_cnt:       邮件发送次数 -> list
            mail_succ_cnt:  发送成功次数 -> list
            true_cnt:       总成功次数 -> int
        """
        # 邮件池，格式：{'邮箱':'stmp地址,授权码'}
        mail_pool = {
                     'xxx@xxx.com':'smtp.xxx.com,xxxxxxxxxxxxx',
                     }
        self.all_mail = list(mail_pool.keys())
        self.today = time.strftime("%Y-%m-%d", time.localtime())
        self.mail_server  = []
        self.mail_cnt = []
        self.mail_succ_cnt = []
        self.true_cnt = 0
        # 循环注册smtplib实例
        for mail_addr, mail_msg in mail_pool.items():
            mail_serveraddr = mail_msg.split(',')[0]
            mail_pass = mail_msg.split(',')[1]
            server=smtplib.SMTP_SSL(mail_serveraddr, 465)
            server.login(mail_addr, mail_pass)
            self.mail_server.append(server)
            self.mail_cnt.append(0)
            self.mail_succ_cnt.append(0)

    def count_reset(self):
        """
        重置计数
        """
        self.true_cnt = 0
        self.mail_cnt = [0 for i in self.mail_cnt]
        self.mail_succ_cnt = [0 for i in self.mail_succ_cnt]

    def get_pool(self):
        return self.mail_server

    def get_server(self):
        """
        获取smtplib实例

        Returns:
            smtplib, index: smtplib实例, 下标
        """
        index = self.mail_cnt.index(min(self.mail_cnt))
        return self.mail_server[index], index

    def send_msg(self):
        """
        给首个邮箱发送昨天的邮件池通知情况
        """
        day_str = self.today
        send_cnt = mail_sender.true_cnt
        all_cnt = mail_sender.mail_cnt
        all_succ_cnt = mail_sender.mail_succ_cnt
        mail_msg = mail_sender.all_mail
        msg_str = f'{day_str}\r\n共发送通知：{send_cnt}，发送成功：{sum(all_succ_cnt)}\r\n邮箱信息：{str(mail_msg)}\r\n发送次数：{str(all_cnt)}\r\n成功次数：{str(all_succ_cnt)}'
        self.send_mail([self.all_mail[0]], '工单邮件通知情况', msg_str, 'plain')
                
    def send_mail(self, sender_list, subject, html_message, msgtype='html'):
        """
        发送邮件的入口，带有重试机制

        Args:
            sender_list (list): 需要发送的邮件列表
            subject (str): 标题
            html_message (str): html文本的邮件
            msgtype (str): 
        """
        try_cnt = 0
        code = 0
        errdata = ''
        while try_cnt < 3:
            server, index = self.get_server()
            self.mail_cnt[index] += 1
            try_cnt += 1
            try:
                # 必须每次重新创建MIMEText实例，重复发送同一个实例会导致收件人丢失
                message = MIMEText(html_message, msgtype, 'utf-8')
                message['Subject'] = subject
                self.mail_sender(server, sender_list, message)
                self.mail_succ_cnt[index] += 1
                break
            except Exception as e:
                errdata = e
                code==-1
                print(e)
        return code, errdata
    
    @staticmethod
    def mail_sender(server, sender_list, msg):
        """
        实现邮件发送

        Args:
            server (smtplib): smtplib实例
            sender_list (list): 需要发送的邮件列表
            msg (MIMEText): MIMEText
        """
        # 登录邮箱
        ser_name = server.auth_login()
        # 发件人加上邮箱姓名
        msg['From'] =formataddr(["DICT工单平台",ser_name])
        # print(sender_list)
        msg['To'] = ';'.join(sender_list)
        # print(msg['To'])
        try:
            server.sendmail(msg['From'], sender_list, msg.as_string())
        except smtplib.SMTPServerDisconnected as e:
            ser_pwd = server.auth_login(True)
            server=smtplib.SMTP_SSL(server._host, 465)  # 发件人邮箱中的SMTP服务器
            server.login(ser_name, ser_pwd)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(msg['From'], sender_list, msg.as_string())
            

mail_sender = mailPool()

class update:
    """
    支持git webhook更新触发服务器同步代码（暂未配置）
    """
    def POST(self):
        i = json.loads(web.data())
        if i.get('token') == 'mxu3nv74oiy7vi34n89xnf982bv824tdf34':
            
            repo = Repo(dirfile)
            g = repo.git
            i = 0
            while i < 5:
                i += 1
                try:
                    g.pull()
                except Exception as e:
                    print(e)
                else:
                    print("Successful pull!")
                    return 'success'
                    break


class send_msg:
    def GET(self):
        mail_sender.send_msg()


class mail_server:
    def GET(self):
        n_date = time.strftime("%Y-%m-%d", time.localtime())
        day_str = '{}--{}'.format(mail_sender.today, n_date)
        send_cnt = mail_sender.true_cnt
        all_cnt = mail_sender.mail_cnt
        all_succ_cnt = mail_sender.mail_succ_cnt
        mail_msg = mail_sender.all_mail
        # if mail_sender.today != n_date:
        #     mail_sender.today = n_date
        return f'{day_str}\r\n共发送通知：{send_cnt}，发送成功：{sum(all_succ_cnt)}\r\n邮箱信息：{str(mail_msg)}\r\n发送次数：{str(all_cnt)}\r\n成功次数：{str(all_succ_cnt)}'.encode('ansi')

    def POST(self):
        paramsss = json.loads(web.data())
        # http_prarms = web.ctx.env
        # timestamp = http_prarms.get('HTTP_TIMESTAMP', '')
        # token = 'w1b12f45vja7vc5ba92h'
        # ori_str = timestamp + token
        # signature = hashlib.md5(ori_str.encode(encoding='utf-8')).hexdigest()
        # if signature == http_prarms.get('HTTP_SIGNATURE'):
        #     pass
        # print(paramsss)
        # print(str(web.ctx.env))
        n_date = time.strftime("%Y-%m-%d", time.localtime())
        if mail_sender.today != n_date:
            mail_sender.send_msg()
            mail_sender.count_reset()
            mail_sender.today = n_date
        title_result = paramsss.get('title_result')
        subject = paramsss.get('subject', '')
        # suggestion = paramsss.get('title_result', '')
        last_state = paramsss.get('last_flow_log')
        participant_info_list = paramsss.get('participant_info_list')
        ticket_value_info = paramsss.get('ticket_value_info')
        last_state_name = last_state.get('state',{}).get('state_name')
        last_participant_name = last_state.get('participant_info',{}).get('participant_alias')
        content_result = paramsss.get('content_result')
        ticket_sn = ticket_value_info.get('sn')
        if subject == '':
            subject = '工单提醒:{}'.format(title_result)
        mail_receivers = [formataddr(parseaddr('{}<{}>'.format(info.get('alias'), info.get('email')))) for info in participant_info_list]
        if len(mail_receivers) == 0:
            # print(paramsss)
            return json.dumps({'code':0,'msg':'no receivers'})
        html_message = f"""<h2>{title_result}</h2><br>
                           {content_result}<br><br>工单来自:{last_state_name}，上一步处理人:{last_participant_name}，流水号：{ticket_sn}<br>请访问工单平台：<a href="http://47.110.59.169:10000/" target=blank>http://47.110.59.169:10000/</a>进行处理"""

        # html_message = """<H>{}</H></br>\n
        #                 来源:{},上一步处理人:{}</br>
        #                 {}</br>""".format(title_result, last_state_name, last_participant_name, content_result)

        mail_sender.true_cnt += 1
        code, errdata = mail_sender.send_mail(mail_receivers, subject, html_message)
        return json.dumps({'code':code,'msg':errdata})
        


if __name__ == '__main__':
    sys.argv.append('10001')
    app.run()

