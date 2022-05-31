import requests
import json


if __name__ == "__main__":

    files = {'file': ('test.mp4', open('/Users/liuyue/Downloads/test.mp4', 'rb'))}   

    # 注册测试
    # data = {'title':"Python News: What's New From April 2022",'desc':'Combining Data in Pandas With merge(), .join(), and concat()',"cid":1,"thumb":"A-Guide-to-Python-Keywords_Watermarked.73f8f57a93ed.jpeg","video":"<iframe src=\"https://player.bilibili.com/player.html?aid=251955199&bvid=BV13Y411s79j&cid=447815214&page=1\" allowfullscreen=\"allowfullscreen\" width=\"100%\" height=\"500\" scrolling=\"no\" frameborder=\"0\" sandbox=\"allow-top-navigation allow-same-origin allow-forms allow-scripts\"></iframe>","vtype":2}
    # headers = {'Content-Type': 'application/json'}
    # r = requests.post("http://127.0.0.1:8000/course/",data = json.dumps(data),headers=headers)
    # print(r.text)

    #登录
    # r = requests.get("http://127.0.0.1:8000/user_signon/?email=123&password=123")
    # print(r.text)

    # # 修改文章
    # data = {'id':1,'content':'修改文章内容'}
    # r = requests.put("http://127.0.0.1:8000/article/",data = data)
    # print(r.text)

    # 删除文章
    # r = requests.delete("http://127.0.0.1:8000/article/?id=2")
    # print(r.text)