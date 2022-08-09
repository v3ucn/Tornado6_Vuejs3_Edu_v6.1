from functools import wraps
from .utils import MyJwt
from app.models import User
import jwt

# websocket认证
def websocket_validated(func):

    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        
        token = self.get_argument("token",None)
        if not token or token == "null":
            self.close(code =1002,reason = "身份认证信息未提供。")
            return
        try:
            myjwt = MyJwt()
            uid = myjwt.decode(token).get("id")
            user = await self.application.objects.get(User,id=uid)
            if not user:
                self.close(code =1003,reason = "用户不存在")
                return
            self._current_id = user.id
            await func(self, *args, **kwargs)
        except Exception as e:
            print(str(e))
            self.close(code =1002,reason = "token异常")
            return

    return wrapper



def jwt_async():
    ''''
    JWT认证装饰器
    '''
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                token = self.request.headers.get('token', None)
                if not token or token == "null":
                    return self.finish({"msg": "身份认证信息未提供。", "errorCode":1})

                myjwt = MyJwt()
                uid = myjwt.decode(token).get("id")
                user = await self.application.objects.get(
                    User,
                    id=uid
                )
                if not user:
                    return self.finish({"msg": "用户不存在", "errcode": 5, "data": {}})

                self._current_user = user
                await func(self, *args, **kwargs)
            except jwt.exceptions.ExpiredSignatureError as e:
                return self.finish({"msg": "Token过期", "errcode":2})
            except jwt.exceptions.DecodeError as e:
                return self.finish({"msg": "Token不合法", "errcode":3,})
            except Exception as e:
                print(str(e))
                return self.finish({"msg": "Token异常", "errcode": 4,})
        return wrapper
    return decorator


def auth_validated(func):
    '''
    动态权限装饰器：根据用户所属角色的权限auth来判断对应的路由是否有权限：查看、新增、修改、删除
    '''
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        user = self._current_user
        if user.role.auth == 0:
            return self.finish({"msg": "无权限，禁止访问。", "errcode": 1, "data": {}})

        if self.request.method == 'GET' and not user.role.auth & 1:
            return self.finish({"msg": "无查看权限，禁止访问。", "errcode": 2, "data": {}})

        if self.request.method == 'POST' and not user.role.auth & 8:
            return self.finish({"msg": "无新增权限，禁止访问。", "errcode": 2, "data": {}})

        if self.request.method == 'PUT' and not user.role.auth & 2:
            return self.finish({"msg": "无修改权限，禁止访问。", "errcode": 2, "data": {}})

        if self.request.method == 'DELETE' and not user.role.auth & 4:
            return self.finish({"msg": "无删除权限，禁止访问。", "errcode": 2, "data": {}})

        await func(self, *args, **kwargs)
    return wrapper

def role_validated(func):

    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        user = self._current_user

        if(user.role.id != 1 and self.request.method == 'POST' and self.request.uri == "/course/"):
            return self.finish({"msg": "无发布权限", "errcode": 2, "data": {}})

        await func(self, *args, **kwargs)
    return wrapper