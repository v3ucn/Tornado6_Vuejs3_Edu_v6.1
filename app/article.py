from tornado.web import url
import tornado.web

from .models import Article
from .base import BaseHandler


class ArticleHandler(BaseHandler):
    
    # 添加文章
    async def post(self):

        title = self.get_argument("title")
        content = self.get_argument("content")

        article = await self.application.objects.create(Article,title=title,content=content)


        self.finish({"code":200,"msg":"添加文章成功","id":article.id})

    # 删除文章
    async def delete(self):

        id = self.get_argument("id")

        article = await self.application.objects.get(Article,id=id)
        await self.application.objects.delete(article)

        self.finish({"code":200,"msg":"删除文章成功"})

    # 修改文章
    async def put(self):

        id = self.get_argument("id")

        content = self.get_argument("content")

        article = await self.application.objects.get(Article,id=id)
        article.content = content
        await self.application.objects.update(article)
        article.save()


        self.finish({"code":200,"msg":"修改文章成功"})

    # 查看文章
    async def get(self):

        id = self.get_argument("id")

        article = await self.application.objects.get(Article.select().where(Article.id==1))

        article = self.application.json_model(article)

        self.render("content.html",article=article)

        #self.finish(article)


urlpatterns = [
    url('/article/',ArticleHandler),
]



