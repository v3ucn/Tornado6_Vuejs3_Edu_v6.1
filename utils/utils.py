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


# 分页器
def paginate(url,page,total):

    if total == 1:
        return ""

    page_str = ""

    if page != 1:

        page_str += '<a class="page-numbers prev" href="'+url+"?page="+str(page-1)+'">上一页</a>'

    for i in range(total):

        if i+1 == page:
            page_str += '&nbsp;<span class="page-numbers current">'+str(i+1)+'</span>'
        else:
            page_str += '&nbsp;<a class="page-numbers" href="'+url+"?page="+str(i+1)+'">&nbsp;'+str(i+1)+'&nbsp;</a>'
    
    if page != total:

        page_str += '<a class="page-numbers next" href="'+url+"?page="+str(page+1)+'">下一页</a>'

    return page_str



#引用层级树
def get_tree(data):
    lists=[]
    tree={}
    for item in data:
        tree[item['id']]=item
    for i in data:
        if not i['pid']:
            lists.append(tree[i['id']])
        else:
            parent_id=i['pid']
            if "children" not in tree[parent_id]:
                tree[parent_id]["children"]=[]
            tree[parent_id]['children'].append(tree[i['id']])

    return lists

# 转换表单
def toSelect(arr,depth=0):  
    html = ''
    for v in arr:
        html+= '<option value="' +str(v['id'])+'">'
        for i in range(depth):
            html += '--'
        html+= v['name'] + '</option>'

        if 'children' in v:
            html+= toSelect(v['children'],depth+1)

    return html


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


async def sendMail(tomail,code):

    _user = "test@qq.com"  #发送者的邮箱
    _pwd = "test"  #发送者的授权码
    _to = "test@qq.com"  #接收者的邮箱

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


def create_order(order_type=1):
    '''
    生成订单编号
    :param order_type: 类型，根据类型生成不同的订单编号
    :return : 32位订单编号
    '''
    now_date_time_str = str(
        datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'))
    base_str = '01234567890123456789'
    random_num = ''.join(random.sample(base_str, 6))
    random_num_two = ''.join(random.sample(base_str, 5))
    order_num = now_date_time_str + str(order_type) + random_num + random_num_two
    return order_num