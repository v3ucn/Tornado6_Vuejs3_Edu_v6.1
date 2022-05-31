# 设置模块路径，否则 app 无法导入
import os, sys
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)
sys.path.append(os.path.join(base_path,'app'))
from tornado import web,ioloop
from app.base import BaseHandler
from app.models import User,database,Course
from app.audit import ListQueue
from app.config import redis_link
import aioredis
import roundrobin

 
class MainHandler(BaseHandler):
    def get(self):
        self.write('Hello Tornado')

get_weighted = roundrobin.weighted([("1",3), ("2",7)])
 
async def run():

    course_id = await lq.out()
    if course_id:
        course = Course.get(id=course_id)
        course.audit = get_weighted()
        course.save()
        
 
if __name__ == '__main__':
    application = web.Application([
        (r'/', MainHandler),
    ])
    application.listen(8001)
    ioloop.PeriodicCallback(run,10000).start()
    ioloop.IOLoop.instance().start()

