import smtplib
from email.mime.text import MIMEText

subject = "测试邮件"
content = "hello world"
sender = "657102455@qq.com"
receiver = '''1225858108@qq.com,215342243@qq.com'''
password = "ydbjmfzjtelxbgaa"
message = MIMEText(content,"plain","utf-8")
message["Subject"] = subject
message["To"] = receiver
message["From"] = sender
smtp = smtplib.SMTP_SSL("smtp.qq.com",465)
smtp.login(sender,password)
smtp.sendmail(sender,receiver.split(","),message.as_string())
smtp.close()