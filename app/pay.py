from tornado.web import url
import tornado.web
from tornado import httpclient
from .base import BaseHandler,BaseManage
from .models import User,Category,Course,Order
from .config import site_domain
from utils.alipay import AliPay
from utils.decorators import jwt_async,auth_validated,role_validated
import peewee
import random
import io
import json

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import paypalrestsdk
from paypalrestsdk import Sale


# Paypal支付类

class Paypal:

    def __init__(self):

        self.client_id = "AV4Qd-byRrKnWSWa4PsuHNAI45rvZWZsCMe3FpOhvWBnd5ifS_FvaQS-wLWdTLOCCZksQFw1eR0kbm4h"
        self.client_secret = "ECRo9sXE2D2F7JMe8JOKKHIOpYdDNwrQCIi4IIoxBZRpPQdk_PhqS1jokMtJ34QZlt_KlrmWTJJwqcO3"
        self.return_url = site_domain + "/paypal_back/"
        self.cancel_url = site_domain + "/paypal_cancel/"

        paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id":self.client_id,
  "client_secret": self.client_secret })

        self.paypalrestsdk = paypalrestsdk

    # 退款方法
    async def refund(self,paymentId):

        payment = self.paypalrestsdk.Payment.find(paymentId)
        sale = Sale.find(payment["transactions"][0]["related_resources"][0]["sale"]["id"])

        refund = sale.refund({
            "amount": {
                "total":payment["transactions"][0]["related_resources"][0]["sale"]["amount"]["total"],
                "currency": "USD"}})

        # Check refund status
        if refund.success():
           return True
        else:
            print(refund.error)
            return False



    # 支付方法
    async def pay(self,price,currency,title):
        
        payment = self.paypalrestsdk.Payment({
    "intent": "sale",
    "payer": {
        "payment_method": "paypal"},
    "redirect_urls": {
        "return_url": self.return_url,
       "cancel_url": self.cancel_url
        },
    "transactions": [{
        "amount": {
            "total": price,
            "currency": currency},
        "description": title}]})
        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = str(link.href)
                    return payment["id"],approval_url
        else:
            print(payment.error)
            return False


# Paypal回调
class PaypalBack(BaseHandler):

    async def get(self):

        paymentId = self.get_argument("paymentId")
        PayerID = self.get_argument("PayerID")

        pp = Paypal()
        payment = pp.paypalrestsdk.Payment.find(paymentId)

        if payment.execute({"payer_id": PayerID}):
            self.finish({"msg":"支付成功","errcode":0})
        else:
            print(payment.error)
            self.finish({"msg":"支付失败","errcode":1})



# paypal支付接口
class PaypalHandler(BaseHandler):

    # 退款
    async def post(self):

        orderid = self.get_argument("orderid")

        paymentId = self.application.redis.get(orderid)

        pp = Paypal()

        res = await pp.refund(paymentId)

        if res:

            self.finish({"msg":"退款成功","errcode":0})
        else:
            self.finish({"msg":"退款失败","errcode":1})




    async def get(self):

        orderid = self.get_argument("orderid")
        order = await self.application.objects.get(Order.select().where(Order.orderid==orderid))

        # 汇率转换
        usd = float(order.price) / 6.74
        pp = Paypal()
        res = await pp.pay(str(round(usd,2)),"USD",order.cid.title)

        if res:
            # 记录订单号
            await self.application.redis.set(orderid,res[0])
            await self.application.redis.set(res[0],orderid)
            self.redirect(res[1])
        else:
            self.finish({"msg":"支付失败","errcode":1})

    


# 回调方法
class AlipayBack(BaseHandler):

    async def get(self):

        orderid = self.get_argument("out_trade_no")
        order = await self.application.objects.get(Order.select().where(Order.orderid==orderid))
        order.state = 1
        await self.application.objects.update(order)
        order.save()

        self.redirect("/order/")



class AlipayHandler(BaseHandler):

    def __init__(self,*args,**kwargs):

        super(BaseHandler,self).__init__(*args,**kwargs)
        self.rt = 0
        self.alipay = self.get_ali_object()


    # 退款
    async def post(self):

        orderid = self.get_argument("orderid")
        order = await self.application.objects.get(Order.select().where(Order.orderid==orderid))
        alipay = self.get_ali_object()
        #调用退款方法
        res = await alipay.api_alipay_trade_refund(
        out_trade_no=orderid,
        refund_amount=order.price,
        )
        if res["alipay_trade_refund_response"]["code"] == "10000":

            order.state = 3
            await self.application.objects.update(order)
            order.save()
        self.finish({"msg":"ok","errcode":0})

    # 支付跳转
    async def get(self):

        orderid = self.get_argument("orderid")
        order = await self.application.objects.get(Order.select().where(Order.orderid==orderid))
        query_params = self.alipay.direct_pay(
            subject=order.cid.title,
            out_trade_no=orderid, 
            total_amount=order.price, 
        )
        pay_url = "https://openapi.alipaydev.com/gateway.do?{0}".format(query_params)  # 支付宝网关地址（沙箱应用）
        self.redirect(pay_url)

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

    url('/pay/',AlipayHandler),
    url('/paypal/',PaypalHandler),
    url('/alipay_back/',AlipayBack),
    url('/paypal_back/',PaypalBack),
]