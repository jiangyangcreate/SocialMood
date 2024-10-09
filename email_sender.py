# encoding: utf-8
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import List, Tuple, Optional

class EmailSender:
    SMTP_SERVERS = {
        'qq.com': 'smtp.qq.com',
        '163.com': 'smtp.163.com',
        'gmail.com': 'smtp.gmail.com',
    }
    DEFAULT_SMTP_SERVER = 'smtp.qq.com'

    @staticmethod
    def get_smtp_server(email: str) -> str:
        '''
        获取邮箱的SMTP服务器
        :param email: 邮箱地址
        :return: SMTP服务器地址
        '''
        domain = email.split('@')[-1].lower()
        return EmailSender.SMTP_SERVERS.get(domain, EmailSender.DEFAULT_SMTP_SERVER)

    @staticmethod
    def send_email(sender: Tuple[str, str], recipients: str, data: List[Tuple[str, str]], image_path: Optional[str] = None) -> None:
        '''
        发送邮件
        :param sender: 发件人邮箱和密码
        :param recipients: 收件人邮箱列表
        :param data: 新闻数据，每个元素是一个元组，包含新闻标题和链接
        :param image_path: 新闻图片路径，可选
        '''
        sender_email, password = sender
        recipient_list = recipients.split(',')
        
        smtp_server = EmailSender.get_smtp_server(sender_email)
        
        msg = MIMEMultipart()
        
        content = f'''
        现在是北京时间{datetime.now().strftime("%H:%M")}<br>
        早上好，一起来关注今日要闻吧:<br>
        {''.join(f'<p><a href="{link}">{title}</a></p>' for title, link in data)}
        '''
        
        msg.attach(MIMEText(content, 'html', 'utf-8'))
        
        if image_path:
            with open(image_path, 'rb') as img_file:
                mime_img = MIMEImage(img_file.read(), _subtype='octet-stream')
            mime_img.add_header('Content-ID', 'imageid')
            msg.attach(mime_img)
            mime_html = MIMEText(f'<html><body><p></p><p><img src="cid:imageid" alt="imageid"></p></body></html>', 'html', 'utf-8')
            msg.attach(mime_html)

        msg['From'] = sender_email
        msg['To'] = ','.join(recipient_list)
        msg['Subject'] = f"{datetime.now().strftime('%m月%d日')}热搜快递"
        
        with smtplib.SMTP_SSL(smtp_server, 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_list, msg.as_string())

# 使用示例
if __name__ == "__main__":
    sender = ("jiangyangcreate@gmail.com", "your_password")
    recipients = "jiangyangcreate@gmail.com"
    data = [("新闻标题1", "http://example.com/news1"), ("新闻标题2", "http://example.com/news2")]
    image_path = "path/to/image.jpg"
    
    EmailSender.send_email(sender, recipients, data, image_path)