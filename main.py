import tornado.ioloop
import tornado.web

import peewee
import peewee_async

import aioredis
import asyncio

from app import user,course,audit,order,pay,msg
from app.base import BaseHandler
from app.models import database,User
from app.config import debug,redis_link

from playhouse.shortcuts import model_to_dict
import json

from tornado.options import define, options
define('port', default=8000, help='default port',type=int)


def json_model(model):
    return model_to_dict(model)

# 三方登录中转页面
class TransferHandler(BaseHandler):

    async def get(self):

        token = self.get_argument("token",None)
        email = self.get_argument("email",None)

        self.render("transfer.html",token=token,email=email)


urlpatterns = [
    (r"/transfer/",TransferHandler),
]

urlpatterns += (user.urlpatterns + course.urlpatterns + audit.urlpatterns + order.urlpatterns + pay.urlpatterns + msg.urlpatterns)

import os

# 创建Tornado实例
application = tornado.web.Application(urlpatterns,template_path=os.path.join(os.path.dirname(__file__), "templates"),static_path=os.path.join(os.path.dirname(__file__),"static"),debug=debug)

# pewee数据库对象注入Tornado实例
application.objects = peewee_async.Manager(database)


async def redis_pool(loop):
    
    return await aioredis.create_redis_pool(redis_link, minsize=1, maxsize=10000, encoding='utf8', loop=loop)

loop = asyncio.get_event_loop()
application.redis = loop.run_until_complete(redis_pool(loop))

application.json_model = json_model

if __name__ == "__main__":
    tornado.options.parse_command_line()
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()