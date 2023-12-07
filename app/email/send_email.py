import smtplib
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader


def send_email(result):
    template_folder = "./templates"  # 模板文件所在的目录

    # 使用绝对路径构建模板文件路径
    template_path = os.path.join(template_folder, "email.html")
    print('template_path',template_path)

    # 创建模板加载器
    env = Environment(loader=FileSystemLoader(template_folder))
    
    # 加载模板
    template = env.get_template("email.html")

    result_html = template.render(result)

    GMAIL_USERNAME = "cloudnativeg23"
    GMAIL_APP_PASSWORD = "kdsojnesnwrdyhob"
    recipients = ["chien00772211@gmail.com"]
    msg = MIMEText(result_html, 'html') 
    msg["Subject"] = "Email report: a simple sum"
    msg["To"] = ", ".join(recipients)
    msg["From"] = f"{GMAIL_USERNAME}@gmail.com"
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(GMAIL_USERNAME, GMAIL_APP_PASSWORD)
    smtp_server.sendmail(msg["From"], recipients, msg.as_string())
    smtp_server.quit()
    