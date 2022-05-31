from tornado.web import url
import tornado.web
from tornado import httpclient
from .base import BaseHandler,BaseManage
from .models import User,Category,Course,Order
from utils.utils import create_order
from utils.decorators import jwt_async,websocket_validated
from utils.alipay import AliPay
import peewee
import random
import io
import json
from .config import site_domain
import os
import tornado.websocket
from app.config import redis_link
import aioredis

#from .chat_ai import get_response
from .chat_think import Think

clients = {}

class WebSocketHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    @websocket_validated
    def open(self):
        self.set_nodelay(True)
        clients[self._current_id]={"id":self._current_id,"object":self}
        #self.write_message("hello uid:%s" % str(self._current_id))
    @websocket_validated
    def on_close(self):
        if self._current_id in clients:
            del clients[self._current_id]
            print("Client %s is closed"%(self._current_id))

    async def on_message(self, message):#收到消息时被调用
        print("Client %s received a message:%s"%(self._current_id,message))

        try:
            message = json.loads(message)

            if message["type"] == "private":

                await self.send_private_message(message["id"],message["text"])

            elif message["type"] == "ai":
                think = Think()
                res = await think.get_res(message["text"])
                #res = await get_response(message["text"])
                await self.send_private_message(self._current_id,res)

        except Exception as e:
            pass
    
    async def send_private_message(self,id,text):

        text = {"type":"private","text":text}
        text = json.dumps(text)

        if id in clients:

            clients[id]["object"].write_message(text)





# 消息保存
class MsgSave:

    def __init__(self,redis):

        self.r = redis
        self.key = "msglist"

    # 保存消息
    async def save(self,id,content):

        await self.r.hset(self.key,id,content)

    # 获取未读消息
    async def get(self,id):

        await self.r.hget(self.key,id)

# 消息推送
async def send_msg(text,id=None):

    text = {"type":"public","text":text}
    text = json.dumps(text)

    if id:
        if id in clients:
            clients[id]["object"].write_message(text)
        else:
            redis = await aioredis.create_redis_pool(redis_link, minsize=1, maxsize=10000, encoding='utf8')
            ms = MsgSave(redis)
            await ms.save(id,text)
    else:
        for key in clients.keys():
            clients[key]["object"].write_message(text)


urlpatterns = [

    url('/websocket/',WebSocketHandler),
]