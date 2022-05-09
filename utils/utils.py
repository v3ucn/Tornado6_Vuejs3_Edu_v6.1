import hashlib
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime

import jwt

class MyJwt:

    def __init__(self):

        self.password = "pvqdztafmwkqcafh"

    def encode(self,user):
        encode_str = jwt.encode(user,self.password,algorithm="HS256")
        return encode_str

    def encode_date(self,user):

        encode_str = jwt.encode({'exp': int((datetime.datetime.now() + datetime.timedelta(seconds=3000)).timestamp()),"data":user},self.password,algorithm='HS256')

        return encode_str
        
    def decode(self,jwt_str):
        
        return jwt.decode(jwt_str,self.password,algorithms=['HS256'])


if __name__ == "__main__":

    myjwt = MyJwt()
    print(myjwt.encode_date({"id":1}))


def create_code(abc=True):
    '''
    生成随机验证码
    :param abc: 类型，为真时返回带字母的验证码，否则返回不带字母的验证码
    :return : 六位验证码
    '''
    if abc:
        base_str = '0123456789qwerrtyuioplkjhgfdsazxcvbnm'
    else:
        base_str = '0123456789'
    return ''.join([random.choice(base_str) for _ in range(6)])

if __name__ == "__main__":
    print(create_code())

def sendMail(tomail,code):

    _user = "164850527@qq.com"  #发送者的邮箱
    _pwd = "pvqdztafmwkqcafh"  #发送者的授权码
    _to = "164850527@qq.com"  #接收者的邮箱

    # 如名字所示Multipart就是分多个部分
    msg = MIMEMultipart()
    msg["Subject"] = "邮箱验证"
    msg["From"] = _user
    msg["To"] = _to

    # ---这是文字部分---
    part = MIMEText("验证码为:%s" % code,"html","utf-8")
    msg.attach(part)


    s = smtplib.SMTP_SSL("smtp.qq.com", 465)
    s.login(_user, _pwd)  # 登陆服务器
    s.sendmail(_user, _to, msg.as_string())  # 发送邮件
    s.close()




def create_password(password):
    '''
    生成加密密码
    :param password: 明文密码
    :return : 密文密码
    '''
    h = hashlib.sha256()
    h.update(bytes(password, encoding='utf-8'))
    h_result = h.hexdigest()
    return h_result