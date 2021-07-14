from email.header import Header
from email.mime.text import MIMEText
import smtplib
import threading


def send(recipients, subject, content):
    sender = '2742331300@qq.com'  # 发件人邮箱
    password = 'vvjadrmsteradeij'  # 发件人邮箱密码
    # 收件人邮箱
    host = 'smtp.qq.com'  # 发件人邮箱主机
    msg = MIMEText(content)
    msg['From'] = sender
    msg['To'] = recipients
    msg['Subject'] = Header(subject, 'utf-8').encode()

    server = smtplib.SMTP_SSL(host, 465)
    server.login(sender, password)
    server.sendmail(sender, [recipients], msg.as_string())
    server.quit()


def sendEmail(emails):
    taskList = []
    for i in emails:
        item = threading.Thread(target=send, args=i)
        taskList.append(item)
    for i in taskList:
        i.start()
    for i in taskList:
        i.join()



if __name__ == '__main__':
    send('1506607292@qq.com', 'question url for you', '<h1>test</h1>')
