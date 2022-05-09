import requests

if __name__ == "__main__":

    # 注册测试
    # data = {'email':'test123@hotmail.com','password':'test'}
    # r = requests.post("http://127.0.0.1:8000/user_signon/",data = data)
    # print(r.text)

    #登录
    r = requests.get("http://127.0.0.1:8000/user_signon/?email=123&password=123")
    print(r.text)

    # # 修改文章
    # data = {'id':1,'content':'修改文章内容'}
    # r = requests.put("http://127.0.0.1:8000/article/",data = data)
    # print(r.text)

    # 删除文章
    # r = requests.delete("http://127.0.0.1:8000/article/?id=2")
    # print(r.text)