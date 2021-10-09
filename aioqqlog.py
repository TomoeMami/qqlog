from aiohttp import web
import json,time,re,datetime,os
from urllib.parse import unquote



def mkdir(path):
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")
    path=path.encode('utf-8')
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists=os.path.exists(path)

    # 判断结果
    if not isExists:
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        return False

routes = web.RouteTableDef()

@routes.get('/hello')
async def hello(request):
    return web.Response(text="Hello, world")

@routes.post('/')
async def post_handler(request):
    json_obj = await request.json()
    if json_obj['type'] == 'GroupMessage':
        msgchain = json_obj['messageChain']
        # sendername = json_obj['sender']['memberName'] +'('+str(json_obj['sender']['id'])[:2]+'****'+str(json_obj['sender']['id'])[-2:]+')'
        sendername = json_obj['sender']['memberName']
        # print(json_obj)
        char = '#### '
        replymark = 0
        for i in msgchain:
            if i['type'] == 'Source':
                gettime = time.strftime("%H:%M:%S ", time.localtime(i['time']))
                char = char + gettime +' '+sendername + '：\n\n'
            elif i['type'] == 'Quote':
                char = char + '<blockquote>'+ i['origin'][0]['text'] +'</blockquote>\n '
            elif i['type'] == 'Plain':
                char = char + i['text']
            elif i['type'] == 'Image':
                char = char + '![]('+i['url']+'")'
            elif i['type'] == 'Face':
                char = char + '[' + i['name'] + ']'
            elif i['type'] == 'At':
                # char = chat + '(@'+str(i['target'])[:2]+'****'+str(i['target'])[-2:]+') '
                char = char + '(@了某人) '
            elif i['type'] == 'Xml':
                url = re.findall(r'url=\"(.+?)\"',i['xml'])[0]
                title = re.findall(r'\<title\>(.+?)\</title\>',i['xml'])[0]
                char = char + ' ['+title+']'+'('+url+')'
            elif i['type'] == 'App':
                dat = json.loads(i['content'])
                url = dat['meta']['detail_1']['qqdocurl']
                title = dat['meta']['detail_1']['desc']
                char = char + ' ['+title+']'+'('+url+')'
        # if replymark == 1:
        #     # print(msgid)
        #     self.send_response(200)
        #     # self.send_header("Content-type", "application/json")
        #     self.end_headers()
        #     # body = {
        #     #         'command': "mute",
        #     #         'content': {
        #     #             "sessionKey":"",
        #     #             "target":614391357,
        #     #             "memberId":1245464567,
        #     #             "time":1800
        #     #             }}
        #     # self.wfile.write(json.dumps(body).encode('utf-8'))
        # else:
        web.Response()
        char = char + '\n\n*****\n\n'
        char = re.sub(r'\((\d{1})\d+(\d{1})\)','(\1****\2)',char)
        dailydict.append(char)
        if len(dailydict) >= 10:
            toyear = datetime.datetime.now().strftime('%Y')
            tomonth = datetime.datetime.now().strftime('%Y-%m')
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            mkdir('./'+toyear)
            mkdir('./'+toyear+'/'+tomonth)
            with open ('./'+toyear+'/'+tomonth+'/'+today+'.md','a',encoding='utf-8') as f:
                f.writelines(dailydict)
            dailydict.clear()
    elif json_obj['type'] == 'FriendMessage':
        msgchain = json_obj['messageChain']
        senderid = json_obj['sender']['id']
        for i in msgchain:
            if i['type'] == 'Plain':
                if i['text'] == '你好':
                    body = {
                            'command': "sendFriendMessage",
                            'content': {
                                "sessionKey":"",
                                "target":senderid,
                                "messageChain":[
                                    { "type":"Plain", "text":"hello\n" },
                                    { "type":"Plain", "text":"world" }
                                ]}}
                    web.json_response(body)
    # elif json_obj['type'] == 'BotInvitedJoinGroupRequestEvent':
    #     if json_obj['fromId'] == '1747222904':
    #         body = {
    #                 'command': "resp_botInvitedJoinGroupRequestEvent",
    #                 'content': {
    #                     "sessionKey":"",
    #                     "eventId":json_obj['eventId'],
    #                     "fromId":json_obj['fromId'],
    #                     "groupId":json_obj['groupId'],
    #                     "operate":0,
    #                     "message":""
    #                     }}
    #         respond(self,body)
    # elif json_obj['type'] == 'MemberJoinRequestEvent':
    #     #{'type': 'MemberJoinRequestEvent', 'eventId': 1633094289803757, 'message': '问题：请输入asoul\n答案：asoul', 'fromId': 1465887523, 'groupId': 614391357, 'groupName': 'S1 A综QQ群纯良分宗', 'nick': '向晚大魔王'}
    #     blacklist = ()
    #     #这里直接填数字
    #     if '答案：asoul' in json_obj['message']:
    #         if json_obj['fromId'] not in blacklist:
    #             body = {
    #                     'command': "resp_memberJoinRequestEvent",
    #                     'content': {
    #                         "sessionKey":"",
    #                         "eventId":json_obj['eventId'],
    #                         "fromId":json_obj['fromId'],
    #                         "groupId":json_obj['groupId'],
    #                         "operate":0,
    #                         "message":""
    #                         }}
    #             respond(self,body)
    #     else:
    #         body = {
    #                 'command': "resp_memberJoinRequestEvent",
    #                 'content': {
    #                     "sessionKey":"",
    #                     "eventId":json_obj['eventId'],
    #                     "fromId":json_obj['fromId'],
    #                     "groupId":json_obj['groupId'],
    #                     "operate":1,
    #                     "message":""
    #                     }}
    #         respond(self,body)
    # elif json_obj['type'] == 'MemberJoinEvent':
    #     body = {
    #             'command': "sendGroupMessage",
    #             'content': {
    #                 "sessionKey":"",
    #                 "target":614391357,
    #                 "messageChain":[
    #                     { "type":"Plain", "text":"请新人查看群公告\n" },
    #                     { "type":"Plain", "text":"本群所有消息均存档，务必谨言慎行" }
    #                 ]}}
    #     respond(self,body)
    # else:
    #     self.send_response(200)
    #     self.end_headers()

app = web.Application()
app.add_routes(routes)
global dailydict
dailydict = []
web.run_app(app, host='0.0.0.0', port=1314)
