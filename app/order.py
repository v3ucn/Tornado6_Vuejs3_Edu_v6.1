from tornado.web import url
import tornado.web
from tornado import httpclient
from .base import BaseHandler,BaseManage
from .models import User,Category,Course,Order

from utils.utils import create_order
from utils.decorators import jwt_async,auth_validated,role_validated
from utils.alipay import AliPay
import peewee
import random
import io
import json
from .config import site_domain
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 订单管理
class OrderManage(BaseHandler):

    @jwt_async()
    async def get(self):

        orders = await self.application.objects.execute(Order.select().where(Order.uid==self._current_user.id))
        orders = [self.application.json_model(x) for x in orders]

        self.finish({"data":orders,"errcode":0})

# 订单生成
class OrderHandler(BaseHandler):

    async def get(self):

        self.render("order.html")


    @jwt_async()
    async def post(self):

        course_id = self.get_argument("id")

        orderid = create_order()

        course = await self.application.objects.get(Course.select().where(Course.id==course_id))

        await self.application.objects.create(Order,orderid=orderid,cid=course.id,uid=self._current_user.id,price=course.price)

        self.finish({"msg":"ok","errcode":0})


# 订单状态查询
class OrderQuery:

    def __init__(self):

        self.alipay = self.get_ali_object()

    async def query(self,orderid):

        alipay = self.alipay
        #调用查询方法
        res = await alipay.api_alipay_trade_query(
        out_trade_no=orderid,
        )
        print(res)

    # 支付宝支付实例
    def get_ali_object(self):

        # 沙箱环境地址：https://openhome.alipay.com/platform/appDaily.htm?tab=info
        app_id = "2016092600603658"  #  APPID （沙箱应用）
        # 异步通知
        notify_url = site_domain+"/alipay_back/"
        # 支付完成后，跳转的地址。
        return_url = notify_url
        merchant_private_key_path = os.path.join(BASE_DIR, 'utils/keys/app_private_2048.txt') # 应用私钥
        alipay_public_key_path = os.path.join(BASE_DIR, 'utils/keys/alipay_public_2048.txt')# 支付宝公钥

        alipay = AliPay(
            appid=app_id,
            app_notify_url=notify_url,
            return_url=return_url,
            app_private_key_path=merchant_private_key_path,
            alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用
            debug=True,
        )
        return alipay

urlpatterns = [

    url('/order/',OrderHandler),
    url('/myorders/',OrderManage),
]

