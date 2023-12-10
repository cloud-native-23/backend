import smtplib
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from app.core.config import settings
from fastapi import BackgroundTasks

def get_formatted_html(result):
    html_format = '''
    <html>
    <body style="margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, Helvetica, sans-serif;">
    <div style="width: 100%; background: #efefef; border-radius: 10px; padding: 10px;">
    <div style="margin: 0 auto; width: 90%; text-align: center;">
        <h1 style="background-color: rgba(0, 53, 102, 1); padding: 5px 10px; border-radius: 5px; color: white;">Stadium Notifications</h1>
        <div style="margin: 30px auto; background: white; width: 40%; border-radius: 10px; padding: 50px; text-align: center;">
        <h3 style="margin-bottom: 100px; font-size: 24px;">{}!</h3>
        </div>
    </div>
    </div>
    </body>
    </html>
    '''.format(result)
    return html_format

def send_email(subject, mail_content, recipients: list):
    result_html = get_formatted_html(mail_content)
    msg = MIMEText(result_html, 'html') 
    msg["Subject"] = subject
    msg["To"] = ", ".join(recipients)
    msg["From"] = settings.ADMIN_EMAIL
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(settings.ADMIN_NAME, settings.ADMIN_PASSWORD)
    smtp_server.sendmail(msg["From"], recipients, msg.as_string())
    smtp_server.quit()

def send_email_background(background_tasks: BackgroundTasks, subject, mail_content, recipients: list):
    background_tasks.add_task(
       send_email, subject, mail_content, recipients)