from functools import wraps
from .utils import MyJwt
from app.models import User
import jwt

def auth_async():
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