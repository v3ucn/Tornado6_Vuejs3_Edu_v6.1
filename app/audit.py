from tornado.web import url
import tornado.web
from tornado import httpclient
from .base import BaseHandler,BaseManage
from .models import User,Category,Course

from utils.utils import create_password
from utils.decorators import jwt_async,auth_validated,role_validated
import peewee
import random
import io
import json
from .msg import send_msg

# 审核队列
class ListQueue:

    def __init__(self,redis):

        self.r = redis
        self.key = "listqueue"

    # 审核任务入队
    async def push(self,item):

        await self.r.lpush(self.key,item)

    # 审核任务出队
    async def out(self):

        # 取值
        item = await self.r.rpop(self.key)

        return item

    # 审核任务出队(ack)
    async def wait_out(self,timeout=1):

        # 取值
        item = await self.r.brpoplpush(self.key,"listqueue_bak",timeout=timeout)

        return item

    # 获取审核队列
    async def get_list(self):

        # 取值
        items = await self.r.lrange(self.key,0,-1)

        return items


# 课程队列监控
class AuditList(BaseHandler):

    async def get(self):
        self.render("audit_list.html")

    @jwt_async()
    async def post(self):

        lq = ListQueue(self.application.redis)

        res = await lq.get_list()

        self.finish({"data":res,"errcode":0})



# 课程审核触发逻辑
class AuditHandler(BaseHandler):

    async def get(self):
        self.render("audit.html")

    @jwt_async()
    async def put(self):

        course_id = self.get_argument("id")
        state = self.get_argument("state")

        course = await self.application.objects.get(Course,id=course_id)
        course.state = state
        await self.application.objects.update(course)
        course.save()

        await send_msg("您的课程已经完成审核",course.uid.id)

        self.finish({"msg":"ok","errcode":0})


    @jwt_async()
    async def post(self):

        # 获取队列中的审核任务
        lq = ListQueue(self.application.redis)
        course_id = await lq.out()

        if course_id:
            course = await self.application.objects.get(Course,id=course_id)
            course.audit = self._current_user.id
            await self.application.objects.update(course)
            course.save()

        courses = await self.application.objects.execute(Course.select().where( (Course.audit == self._current_user.id) & (Course.state == 0)  ))
        courses = [self.application.json_model(x) for x in courses]

        self.finish({"data":courses,"errcode":0})


urlpatterns = [

    url('/audit/',AuditHandler),
    url('/auditlist/',AuditList),
]