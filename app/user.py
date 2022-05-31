from tornado.web import url
import tornado.web
from tornado import httpclient
from .base import BaseHandler
from .models import User,database

from utils.utils import create_password,create_code,sendMail,MyJwt
from utils.decorators import jwt_async,auth_validated
import peewee

import random
from PIL import ImageDraw
from PIL import Image
import io
import json

from abc import ABCMeta, abstractmethod
from .config import site_domain

from web3.auto import w3
from eth_account.messages import defunct_hash_message
import time

class CheckW3(BaseHandler):

    async def post(self):

        public_address = self.get_argument("public_address")
        signature = self.get_argument("signature")

        domain = self.request.host
        if ":" in domain:
            domain = domain[0:domain.index(":")]

        now = int(time.time())
        sortanow = now-now%600
   
        original_message = 'Signing in to {} at {}'.format(domain,sortanow)
        print("[+] checking: "+original_message)
        message_hash = defunct_hash_message(text=original_message)
        signer = w3.eth.account.recoverHash(message_hash, signature=signature)

        if signer == public_address:
            try:
                user = await self.application.objects.get(User,email=public_address)
            except Exception as e:
                user = await self.application.objects.create(User,email=public_address,password=create_password("third"),role=1)

            myjwt = MyJwt()
            token = myjwt.encode({"id":user.id})
            self.finish({"msg":"ok","errcode":0,"public_address":public_address,"token":token})
        else:
            self.finish({"msg":"could not authenticate signature","errcode":1})



# 用户管理
class UserManage(BaseHandler):

    # 查询
    @jwt_async()
    @auth_validated
    async def get(self):

        users = await self.application.objects.execute(User.select())
        users = [self.application.json_model(x) for x in users]

        self.finish({"data":users,"errcode":0})

    # 修改
    @jwt_async()
    @auth_validated
    async def put(self):

        id = self.get_argument("id")
        email = self.get_argument("email")

        user = await self.application.objects.get(User,id=id)
        user.email = email
        await self.application.objects.update(user)
        user.save()

        self.finish({"msg":"ok","errcode":0})

    # 添加
    @jwt_async()
    @auth_validated
    async def post(self):

        email = self.get_argument("email")
        password = self.get_argument("password")
        role = self.get_argument("role")

        user = await self.application.objects.create(User,email=email,password=create_password(password),role=int(role))

        self.finish({"msg":"ok","errcode":0})

    # 删除
    @jwt_async()
    @auth_validated
    async def delete(self):

        id = self.get_argument("id")

        user = await self.application.objects.get(User,id=id)
        user.state = 0
        await self.application.objects.update(user)
        user.save()

        self.finish({"msg":"ok","errcode":0})



# 用户详情
class UserInfo(BaseHandler):

    @jwt_async()
    @auth_validated
    async def get(self):

        if self._current_user:
            user = self._current_user
            self.finish({"uid":user.id,"email":user.email,"role_name":user.role.role_name})
        else:
            self.finish({"msg":"未登录","errcode":1})


class IdProvider(metaclass=ABCMeta):

    # 跳转url
    @abstractmethod
    def get_url(self):
        pass

    # 获取token
    @abstractmethod
    async def get_token(self,code):
        pass

    # 获取用户信息
    @abstractmethod
    async def get_user(self,token):
        pass

    # 用户信息留存
    @abstractmethod
    async def set_user(self,user):
        pass

class GithubProvider(IdProvider):

    def __init__(self):

        self.clientid = "249b69d8f6e63efb2590"
        self.clientsecret = "b5989f2c67d6f51d5dffc69fecd8140fbb8277a9"
        self.url = site_domain+"/github_back/"
        self.database = database

    def get_url(self):

        return "https://github.com/login/oauth/authorize?client_id=%s&redirect_uri=%s" % (self.clientid,self.url)


    async def get_token(self,code):

        headers = {'accept':'application/json'}

        url = "https://github.com/login/oauth/access_token?client_id=%s&client_secret=%s&code=%s" % (self.clientid,self.clientsecret,code)

        res = await httpclient.AsyncHTTPClient().fetch(url,method='POST',headers=headers,validate_cert=False,body=b'')

        print(json.loads(res.body.decode()))

        token = json.loads(res.body.decode())["access_token"]

        return token

    async def get_user(self, token):

        # 获取gitHub用户信息
        headers = {'accept':'application/json',"Authorization":"token %s" % token}
        res = await httpclient.AsyncHTTPClient().fetch("https://api.github.com/user",method='GET',headers=headers,validate_cert=False)

        userinfo = json.loads(res.body.decode())

        return userinfo

    async def set_user(self, user):

        try:
            user = await self.database.get(User,email=user['email'])
        except Exception as e:
            user = await self.database.create(User,email=email,password=create_password("third"),role=1)

        myjwt = MyJwt()
        token = myjwt.encode({"id":user.id})

        return token


class IdFactory:

    @staticmethod
    def create(name):
        if name == 'github':
            return GithubProvider()

# github登录类(工厂)
class GithubFactory(BaseHandler):

    def __init__(self,*args,**kwargs):

        super(GithubFactory,self).__init__(*args,**kwargs)

        self.github = IdFactory.create("github")

    async def get(self):

        code = self.get_argument("code")

        # 获取token
        token = await self.github.get_token(code)

        # 获取用户信息
        user = await self.github.get_token(token)

        # 留存用户信息
        token = await self.github.get_token(user)

        # 重定向
        self.redirect('/?token=%s' % token)




# github登录类
class GithubSign(BaseHandler):

    def __init__(self,*args,**kwargs):

        super(GithubSign,self).__init__(*args,**kwargs)

        self.clientid = "249b69d8f6e63efb2590"
        self.clientsecret = "b5989f2c67d6f51d5dffc69fecd8140fbb8277a9"
        self.url = site_domain+"/github_back/"

    async def set_user(self,email):

        try:
            user = await self.application.objects.get(User,email=email)
        except Exception as e:
            user = await self.application.objects.create(User,email=email,password=create_password("third"),role=1)

        myjwt = MyJwt()
        token = myjwt.encode({"id":user.id})

        return [token,user.email]


    def get_url(self):

        return "https://github.com/login/oauth/authorize?client_id=%s&redirect_uri=%s" % (self.clientid,self.url)

    # 回调网址
    async def get(self):

        code = self.get_argument("code")

        headers = {'accept':'application/json'}

        url = "https://github.com/login/oauth/access_token?client_id=%s&client_secret=%s&code=%s" % (self.clientid,self.clientsecret,code)

        res = await httpclient.AsyncHTTPClient().fetch(url,method='POST',headers=headers,validate_cert=False,body=b'',connect_timeout=30.0, request_timeout=30.0)

        print(json.loads(res.body.decode()))

        token = json.loads(res.body.decode())["access_token"]

        # 获取gitHub用户信息
        headers = {'accept':'application/json',"Authorization":"token %s" % token}
        res = await httpclient.AsyncHTTPClient().fetch("https://api.github.com/user",method='GET',headers=headers,validate_cert=False,connect_timeout=30.0, request_timeout=30.0)

        userinfo = json.loads(res.body.decode())

        token,email = await self.set_user(userinfo["email"])

        self.redirect('/transfer/?token=%s&email=%s' % (token,email))



class ImgCode(BaseHandler):

    def get_random_color(self):
        R = random.randrange(255)
        G = random.randrange(255)
        B = random.randrange(255)
        return (R,G,B)

    async def get(self):

        #定义画布大小 宽，高
        img_size = (120,50)
        #定义画笔 颜色种类,画布，背景颜色
        image = Image.new("RGB",img_size,'white')
        #定义画笔对象 图片对象,颜色类型
        draw = ImageDraw.Draw(image,'RGB')
        #定义随机字符
        source = '0123456789asdfghjkl'
        #定义四个字符
        #定义好容器，用来接收随机字符串
        code_str = ''
        for i in range(4):
            #获取随机颜色 字体颜色
            text_color = self.get_random_color()
            #获取随机字符串
            tmp_num = random.randrange(len(source))
            #获取字符集
            random_str = source[tmp_num]
            #将随机生成的字符串添加到容器中
            code_str += random_str
            draw.text((10+30*i,20),random_str,text_color)
        #self.application.redis.set("imgcode",code_str)
        #使用io获取一个缓存区
        buf = io.BytesIO()
        image.save(buf,'png')
        self.set_header('Content-Type','image/png')
        #将图片保存到缓存区
        return self.finish(buf.getvalue())

# 邮箱验证
class EmailActive(BaseHandler):

    async def get(self):

        email = self.get_argument("email")
        code = self.get_argument("code")

        redis_code = await self.application.redis.get(email)

        if redis_code and redis_code == code:
            self.finish({"msg":"验证成功"})
            user = await self.application.objects.get(User.select().where(User.email==email))
            user.state = 1
            await self.application.objects.update(user)
            user.save()

        else:
            self.finish({"msg":"验证码错误"})

        


class UserHandler(BaseHandler):

    # 用户登录
    async def get(self):

        email = self.get_argument("email")
        password = self.get_argument("password")

        try:
            user = await self.application.objects.get(User.select().where( (User.email == email) & (User.password == create_password(password))))
            myjwt = MyJwt()
            token = myjwt.encode({"id":user.id})
            self.finish({"msg":"登录成功","errcode":0,"token":token,"email":user.email})
        except Exception as e:
            print(str(e))
            self.finish({"msg":"用户名或者密码错误","errcode":1})


    # 用户注册
    async def post(self):

        email = self.get_argument("email")
        password = self.get_argument("password")
        role = self.get_argument("role",1)

        try:
            user = await self.application.objects.create(User,email=email,password=create_password(password),role=int(role))
            # 发送随机验证码
            code = create_code()
            await sendMail(user.email,code)
            await self.application.redis.set(user.email,code)

            self.finish({"msg":"注册成功","errcode":0})
        except peewee.IntegrityError as e:
            self.finish({"msg":"该邮箱已经存在","errcode":1})
        except Exception as e:
            print(str(e))
            self.finish({"msg":"发生未知错误","errcode":2})



class SignOnHandler(BaseHandler):
    

    # 用户注册页面
    async def get(self):

        self.render("sign_on.html")


class SignInHandler(BaseHandler):
    

    # 用户登录页面
    async def get(self):

        self.render("sign_in.html")

class AdminUserHandler(BaseHandler):
    

    # 用户管理
    async def get(self):

        self.render("admin_user.html")


urlpatterns = [
    url('/user_signon/',UserHandler),
    url('/sign_on/',SignOnHandler),
    url('/sign_in/',SignInHandler),
    url('/emailactive/',EmailActive),
    url('/imgcode/',ImgCode),
    url('/github_back/',GithubSign),
    url('/userinfo/',UserInfo),
    url('/checkw3/',CheckW3),
    url('/admin/user/',UserManage),
    url('/admin_user/',AdminUserHandler),
]



