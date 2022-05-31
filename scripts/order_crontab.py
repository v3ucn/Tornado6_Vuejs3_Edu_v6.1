# 设置模块路径，否则 app 无法导入
import os, sys
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)
sys.path.append(os.path.join(base_path,'app'))
from tornado import web,ioloop
from app.base import BaseHandler
from app.models import Order
from app.order import OrderQuery
from app.config import redis_link
from utils.delayqueue import DelayQueue
import aioredis


 
class MainHandler(BaseHandler):
    def get(self):
        self.write('Hello Tornado')
 
async def run():

    redis = await aioredis.create_redis_pool(redis_link, minsize=1, maxsize=10000, encoding='utf8')

    dq = DelayQueue(redis)

    res = await dq.out()

    if res:
        oq = OrderQuery()
        order = await oq.query(res[0])
        print(order)

 
if __name__ == '__main__':
    application = web.Application([
        (r'/', MainHandler),
    ])
    application.listen(8001)
    ioloop.PeriodicCallback(run,2000).start()
    ioloop.IOLoop.instance().start()

