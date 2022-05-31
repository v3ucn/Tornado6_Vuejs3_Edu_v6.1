import json
import tornado


class BaseHandler(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        tornado.web.RequestHandler.__init__(self, *args, **kwargs)
        self.rt = 0

    def set_default_headers(self):
        print("setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST,GET,PUT,DELETE')

    def render(self,template_name,**kwargs):
        self.rt = 1
        tornado.web.RequestHandler.render(self,template_name,**kwargs)

    def finish(self, chunk=None):

        if chunk is not None and self.rt == 0 and not isinstance(chunk,bytes):
            chunk = json.dumps(chunk,indent=4, sort_keys=True, default=str,ensure_ascii=False)
        try:
            tornado.web.RequestHandler.write(self,chunk)
        except Exception as e:
            pass
        tornado.web.RequestHandler.finish(self)

    def post(self):
        self.write('some post')

    def get(self):
        self.write('some get')

    def put(self):
        self.write('some get')

    def delete(self):
        self.write('some get')

    def options(self, *args):
        # no body
        # `*args` is for route with `path arguments` supports
        self.set_status(204)
        self.finish()


# 封装操作类

class BaseManage(BaseHandler):

    async def get_all(self,model):

        datas = await self.application.objects.execute(model.select())
        datas = [self.application.json_model(x) for x in datas]

        return datas

    async def get_one(self,model,id):

        data = await self.application.objects.get(model.select().where(model.id==id))
        data = self.application.json_model(data)

        return data

    async def create(self,model,data):

        await self.application.objects.create(model,**data)

        return True

    async def update(self,model,id,fields):

        data = await self.application.objects.get(model.select().where(model.id==id))
        model.update(**fields).where(model.id==data.id).execute()

        return True

    async def remove(self,model,id):

        data = await self.application.objects.get(model.select().where(model.id==id))
        model.update(**{"state":4}).where(model.id==data.id).execute()

        return True