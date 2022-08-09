from tornado.web import url
import tornado.web
from tornado import httpclient
from .base import BaseHandler,BaseManage
from .models import User,Category,Course

from utils.utils import create_password,create_code,sendMail,MyJwt,get_tree,toSelect,paginate
from utils.decorators import jwt_async,auth_validated,role_validated
import peewee

import random

import io
import json

from datetime import datetime
import uuid
import aiofiles
import os
from .config import FILE_CHECK,FILE_SIZE
import math



# 课程管理接口
class CourseManage(BaseManage):

    @jwt_async()
    @role_validated
    async def get(self):

        courses = await self.get_all(Course)

        self.finish({"courses":courses,"errcode":0})

# 课程管理页面
class AdminCourse(BaseHandler):

    async def get(self):

        self.render("admin_course.html")


# 模糊查询检索
class CourseSearch(BaseHandler):

    async def get(self):

        keyword = self.get_argument("keyword",None)

        courses = []

        if keyword:

            courses = await self.application.objects.execute(Course.select().where( (Course.title.contains(keyword) ) | (Course.desc.contains(keyword)) ))

            courses = [self.application.json_model(x) for x in courses]

        self.render("search.html",courses=courses)

from aiocache import cached,Cache

# 排行榜
class CourseRank(BaseHandler):

    @cached(ttl=30,key="rank",cache=Cache.REDIS)
    async def get_rank(self):

        rank = await self.application.redis.zrevrange('course_rank', 0,9, withscores=True)
        rank_ids = [value[0] for value in rank]
        rank_dict = {value[0]:value[1] for value in rank}
        courses = await self.application.objects.execute(Course.raw(" select * from course where id in ("+",".join(rank_ids)+") order by field (id,"+",".join(rank_ids)+")  "))
        courses = [self.application.json_model(x) for x in courses]
        for value in courses:
            value["views"] = rank_dict.get(str(value["id"]))

        courses = json.dumps(courses,default=str)
        return courses

    async def get(self):

        courses = await self.get_rank()
        self.render("rank.html",courses=json.loads(courses))

# 课程接口
class CourseHandler(BaseHandler):

    # 课程
    async def get(self):

        id = self.get_argument("id",None)

        page = int(self.get_argument("page",1))
        size = int(self.get_argument("size",20))

        if id:

            try:
                course = await self.application.objects.get(Course.select().where(Course.id==id))
            except Exception as e:
                self.finish({"msg":"该课程不存在","errcode":1})

            course = self.application.json_model(course)

            await self.application.redis.zincrby('course_rank',1,course['id'])

            views = await self.application.redis.zscore("course_rank",course['id'])

                

            self.render("view.html",course=course,courseid=course['id'],views=views)

        else:
            print(self.application.objects.connect())
            total = await self.application.objects.count(Course.select())
            all_page = math.ceil(total / size)
            courses = await self.application.objects.execute(Course.select().paginate(page,size))
            # 序列化操作
            courses = [self.application.json_model(x) for x in courses]

            page_str = paginate("/",page,all_page)


            self.render("index.html",courses=courses,page_str=page_str)

    # 课程发布
    @jwt_async()
    @role_validated
    async def post(self):

        data = self.request.body.decode('utf-8') if self.request.body else "{}"
        data = json.loads(data)
        data["uid"] = self._current_user.id
        try:
            await self.application.objects.create(Course,**data)
            self.finish({"msg":"发布成功","errcode":0})
        except Exception as e:
            print(str(e))
            self.finish({"msg":"未知错误","errcode":1})

# 文件上传
class UploadHandler(BaseHandler):

    @jwt_async()
    async def post(self):

        back_file = ""

        file = self.request.files['file']

        for key in file:

            new_file_name = ''.join(str(uuid.uuid1()).split('-'))
            file_name = key['filename']
            file_size = len(key['body'])
            file_content = key['body']
            check_name = file_name.split('.')[-1]

            if check_name.lower() not in FILE_CHECK:
                self.finish({"msg":"不是规定的文件类型","errcode":2})
            if file_size > FILE_SIZE:
                self.finish({"msg":"文件过大","errcode":2})
            save_file_name = new_file_name + '.' + check_name
            back_file = save_file_name
        
            async with aiofiles.open("./static/uploads/"+save_file_name, 'wb') as f:
                await f.write(file_content)


        self.finish({"msg":"ok","errcode":0,"file":back_file})


class CourseUploadHandler(BaseHandler):
    
    # 课程上传页面
    async def get(self):

        # 异步读取分类
        cates = await self.application.objects.execute(Category.select())
        # 序列化操作
        cates = [self.application.json_model(x) for x in cates]

        cate_tree = get_tree(cates)

        select = toSelect(cate_tree)

        self.render("course_upload.html",select=select)


# 分片上传
class SliceUploadHandler(BaseHandler):
    
    async def post(self):

        file = self.request.files["file"][0]
        filename = self.get_argument("filename")
        count = self.get_argument("count")

        filename = '%s_%s' % (filename,count) # 构成该分片唯一标识符

        contents = file['body'] #异步读取文件
        async with aiofiles.open('./static/uploads/%s' % filename, "wb") as f:
            await f.write(contents)

        self.finish({"filename": file.filename,"errcode":0})

# 分片合并
class MergeUploadHandler(BaseHandler):
    
    async def post(self):

        filename = self.get_argument("filename")
        chunk = 0

        async with aiofiles.open('./static/uploads/%s' % filename,'ab') as target_file:

            while True:
                try:
                    source_file = open('./static/uploads/%s_%s' % (filename,chunk), 'rb')
                    await target_file.write(source_file.read())
                    source_file.close()
                except Exception as e:
                    print(str(e))
                    break

                chunk = chunk + 1
        self.finish({"msg":"ok","errcode":0})

from redisearch import Client,TextField,NumericField

# 数据同步
class SyncData(BaseHandler):

    async def get(self):

        client = Client('course',host='localhost',port='6666')
        # Creating the index definition and schema
        client.create_index((TextField('title'),TextField('desc')))

        courses = await self.application.objects.execute(Course.select())
        courses = [self.application.json_model(x) for x in courses]

        for value in courses:

            client.add_document(value["id"], title = value["title"],desc =value["desc"],language='chinese')

        self.finish({"msg":"ok","errcode":0})


# 全文检索
class Redisearch(BaseHandler):

    async def get(self):

        client = Client('course',host='localhost',port='6666')

        keyword = self.get_argument("keyword",None)

        res = client.search(keyword)

        self.finish({"data":res.docs,"errcode":0})


urlpatterns = [

    url('/course_upload/',CourseUploadHandler),
    url('/course/',CourseHandler),
    url('/upload/',UploadHandler),
    url('/',CourseHandler),
    url('/view/',CourseHandler),
    url('/rank/',CourseRank),
    url('/search/',CourseSearch),
    url('/admin_course/',AdminCourse),
    url('/admin/course/',CourseManage),
]



