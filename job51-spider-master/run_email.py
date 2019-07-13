'''
#https://www.cnblogs.com/elroye/p/8041821.html 感谢elroye贡献
'''
import pymysql
from config import MYSQL_DATA_DB, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWD, MYSQL_CHARSET, MYSQL_HOST
import re, time, hashlib, random
import datetime


def insert_into(table_name, cols, values):
    while True:
        try:
            # 连接mysql
            connect = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWD, MYSQL_DATA_DB, charset=MYSQL_CHARSET,
                                      port=MYSQL_PORT)
            cursor = connect.cursor()
            # 创建sql语句
            sql = "INSERT INTO `{}` ({}) VALUES ({})".format(table_name,','.join(cols),','.join(['%s'] * len(values)))
            # 执行sql语句
            cursor.execute(sql, values)
            connect.commit()
            cursor.close()
            connect.close()
            break
        except Exception as e:
            print(e)


def get_data_from_db():
    # 填写你的sql语句
    tables=['job_51job'] #可扩展
    connect = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWD, MYSQL_DATA_DB, charset=MYSQL_CHARSET,
                              port=MYSQL_PORT)
    cursor = connect.cursor()
    cursor.execute('truncate jobs_parser')
    connect.commit()

    for table in tables:
        sql = '''select company,district,url,salary,position,degree,job_demand from {} where Insert_database_time like "{}" '''.format(table,'%'+str(datetime.datetime.now())[0:10]+'%')
        # 连接mysql
        print(sql)
        cursor.execute(sql)
        connect.commit()
        results = cursor.fetchall()
        txt=''
        for r in results:
            txt=txt+" "+r[0]+r[1]+" "+r[2]+'\n'
        print(txt)
        cursor.close()
        connect.close()
        return txt


def email_qq(txt):
    import smtplib
    from email.mime.text import MIMEText
    from email.utils import formataddr

    my_sender='896603142@qq.com'    # 发件人邮箱账号
    my_pass = 'kobyjqhfbnnmbbj'   # 发件人邮箱密码(当时申请smtp给的口令)
    my_user='896603142@qq.com'      # 收件人邮箱账号，我这边发送给自己
    def mail():
        ret=True
        try:
            msg=MIMEText(txt,'plain','utf-8')
            msg['From']=formataddr(["jobs_parse",my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To']=formataddr(["Woods",my_user])              # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject']="jobs_{}".format(str(datetime.datetime.now())[:16])                # 邮件的主题，也可以说是标题

            server=smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
            server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(my_sender,[my_user,],msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()# 关闭连接
        except Exception as e:# 如果 try 中的语句没有执行，则会执行下面的 ret=False
            ret=False
            print(str(e))
        return ret

    ret=mail()
    if ret:
        print("邮件发送成功")
    else:
        print("邮件发送失败")

if __name__=="__main__":

    import os
    def run(web=True,email_=True):
        if web:
            os.system("cd e:/job51-spider-master && python3 job_51job_url.py")
        if email_:
            txt = get_data_from_db()
            print(txt)
            email_qq(txt)

    run(web=True,email_=True)