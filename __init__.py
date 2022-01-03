from botoy import async_decorators as deco
from botoy import jconfig, logger, S
import requests, json
__doc__ = """处理BT下载请求"""

mega_header = 'magnet:?xt=urn:btih:'
header_len = len(mega_header)
rpc_address = jconfig.host + ':6800/jsonrpc'
jsondata={
    "jsonrpc":"2.0",
    "id":"QXJpYU5nXzE1NDgzODg5MzhfMC4xMTYyODI2OTExMzMxMzczOA==",
    }

def SendMegaLink(code):
    Ret = True
    Error = ''
    if len(code) == 40:
        is_mega_code = True
        for char in code:
            if not ((char >= '0' and char <= '9') or
                (char >= 'a' and char <= 'z') or
                (char >= 'A' and char <= 'Z')):
                is_mega_code = False
                Ret = False
                Error = '不合法的磁力链接特征码'

        if is_mega_code:
            uri = mega_header + code
            print(uri)
            reqdata = jsondata
            reqdata['method'] = 'aria2.addUri'
            reqdata['params'] = [[],{}]
            reqdata['params'][0] = [uri]
            print(reqdata)

            res = requests.post(rpc_address,json=reqdata)
            if res.status_code != requests.codes.ok:
                Ret = False
                res = res.json()
                if 'error' in res:
                    Error = 'Code:{}, {}'.format(res['error']['code'], res['error']['message'])

    return Ret, Error
                

            

@deco.ignore_botself
async def receive_friend_msg(ctx):
    if ctx.FromUin == jconfig.superAdmin:
        Ret = True;
        Error = ''
        SentItem = 0
        Reply = ''
        Content = str.strip(ctx.Content)
        if len(Content) == 40:
            Ret, Error = SendMegaLink(Content)
            if Ret == True:
                SentItem += 1
        else:
            mag_start = ctx.Content.find(mega_header)
            while mag_start >= 0:
                mag_link = ctx.Content[mag_start+header_len:mag_start+header_len+40]
                Ret, Error = SendMegaLink(mag_link)
                if Ret == False:
                    break
                else:
                    SentItem += 1
                mag_start = ctx.Content.find(mega_header, mag_start+header_len+40)

        if Ret == False:
            Reply = '磁力链接下载请求失败:' + Error

        if SentItem > 0:
            Processed = '\n已处理链接:{}条'.format(SentItem)
            Reply += Processed

        Sender = S.bind(ctx)
        await Sender.atext(Reply)
            

