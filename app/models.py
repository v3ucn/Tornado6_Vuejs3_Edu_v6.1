from peewee import Model, DateTimeField
from datetime import datetime
from .config import mysql_db,mysql_password,mysql_user,mysql_host,mysql_port
import peewee_async
import peewee

# 这里mytest和root分别指代数据库名称以及用户和密码
database = peewee_async.PooledMySQLDatabase(mysql_db,host=mysql_host,port=mysql_port,user=mysql_user,password=mysql_password)

# 建立基础类

class BaseModel(Model):

    id = peewee.BigIntegerField(primary_key=True, unique=True,
            constraints=[peewee.SQL('AUTO_INCREMENT')])
    create_time = DateTimeField(default=datetime.now, verbose_name="添加时间", help_text='添加时间')
    update_time = DateTimeField(default=datetime.now, verbose_name='更新时间', help_text='更新时间')

    def save(self, *args, **kwargs):
        if self._pk is None:
            self.create_time = datetime.now()
        self.update_time = datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)
    

    class Meta:
        database = database

class Role(BaseModel):
    
    role_name = peewee.CharField(unique=True,verbose_name='角色名称', help_text='角色名称')
    auth = peewee.IntegerField(default=0,verbose_name='角色权限', help_text='角色权限')
    
    class Meta:
        db_table = "role"

class User(BaseModel):
    
    email = peewee.CharField(unique=True,verbose_name='邮箱', help_text='邮箱')
    
    password = peewee.CharField(verbose_name='密码', help_text='密码')

    #role = peewee.IntegerField(default=1,verbose_name='角色', help_text='角色 1老师 2学生 3后台管理 4客服')
    role = peewee.ForeignKeyField(Role, backref='roles')

    state = peewee.IntegerField(default=0,verbose_name='状态', help_text='0待激活 1已激活 2已注销')
    
    class Meta:
        db_table = "user"



# 文章类
class Article(BaseModel):
    
    id = peewee.BigIntegerField(primary_key=True, unique=True,
            constraints=[peewee.SQL('AUTO_INCREMENT')])
    
    title = peewee.CharField(null=False,verbose_name='文章标题', help_text='文章标题')
    
    content = peewee.CharField(null=False,verbose_name='文章内容', help_text='文章内容')
    
    class Meta:
        db_table = "article"


if __name__ == "__main__":

    # User.drop_table(True)
    # Role.create_table(True)
    # User.create_table(True)
    Role.create(role_name="老师")
    Role.create(role_name="学生")
    Role.create(role_name="后台管理")
    Role.create(role_name="客服")
