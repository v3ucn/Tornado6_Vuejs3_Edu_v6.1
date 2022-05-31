from peewee import Model, DateTimeField
from datetime import datetime
from .config import mysql_db,mysql_password,mysql_user,mysql_host,mysql_port
import peewee_async
import peewee

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



#课程分类
class Category(BaseModel):
    
    name = peewee.CharField(unique=True,verbose_name='分类名称', help_text='分类名称')
    pid = peewee.IntegerField(default=0,verbose_name='父类id', help_text='父类id')
    
    class Meta:
        db_table = "category"

#课程
class Course(BaseModel):
    
    title = peewee.CharField(unique=True,verbose_name='课程标题', help_text='课程标题')
    desc = peewee.TextField(default='',verbose_name='课程描述', help_text='课程描述')
    cid = peewee.ForeignKeyField(Category, backref='courses')
    price = peewee.BigIntegerField(default=0,verbose_name='课程价格', help_text='课程价格')
    thumb = peewee.CharField(verbose_name='缩略图', help_text='缩略图')
    video = peewee.TextField(verbose_name='课程视频', help_text='课程视频')
    vtype = peewee.IntegerField(default=1,verbose_name='视频类型', help_text='视频类型')
    uid = peewee.ForeignKeyField(Category, backref='users',verbose_name='用户uid', help_text='用户uid')
    audit = peewee.IntegerField(default=0,verbose_name='审核员id', help_text='审核员id')
    state = peewee.IntegerField(default=0,verbose_name='课程状态', help_text='课程状态')
    
    class Meta:
        db_table = "course"

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

# 订单表
class Order(BaseModel):

    orderid = peewee.CharField(unique=True,verbose_name='订单id', help_text='订单id')
    price = peewee.BigIntegerField(default=0,verbose_name='订单价格', help_text='订单价格')
    uid = peewee.ForeignKeyField(User)
    cid = peewee.ForeignKeyField(Course)
    channel = peewee.IntegerField(default=1,verbose_name='支付渠道', help_text='支付渠道，1阿里2微信3Paypal')
    state = peewee.IntegerField(default=0,verbose_name='订单状态', help_text='订单状态，0待支付1已支付2订单关闭')

    class Meta:
        db_table = "order"



if __name__ == "__main__":

    Order.create_table(True)
