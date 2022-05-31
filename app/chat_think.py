from tornado import httpclient
import json

class Think:

    def __init__(self):

        self.appid = "118f1472e91c30c4c82df39c8e8c71ac"
        self.userid = "Aef4MHCp"

    async def get_res(self,text):

        res = await httpclient.AsyncHTTPClient().fetch("https://api.ownthink.com/bot?appid=%s&userid=%s&spoken=%s" % (self.appid,self.userid,text),method='GET',validate_cert=False,connect_timeout=30.0, request_timeout=30.0)
        res = json.loads(res.body.decode())
        return res["data"]["info"]["text"]