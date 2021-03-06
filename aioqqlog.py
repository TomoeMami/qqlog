from aiohttp import web
import json,time,re,datetime,os
from urllib.parse import unquote
import aiohttp

async def b23_extract(text):
    b23 = re.compile(r'b23.tv/(\w+)|(bili(22|23|33|2233).cn)/(\w+)', re.I).search(text.replace("\\",""))
    if b23:
        url = f'https://{b23[0]}'
        async with aiohttp.request('GET', url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
            r = str(resp.url)
        return r
    else:
        return None

async def extract(text:str):
    try:
        aid = re.compile(r'av\d+', re.I).search(text)
        bvid = re.compile(r'BV([a-zA-Z0-9])+', re.I).search(text)
        if bvid:
            url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid[0]}'
        elif aid:
            url = f'https://api.bilibili.com/x/web-interface/view?aid={aid[0][2:]}'
        return url
    except:
        return None

async def video_detail(url):
    try:
        async with aiohttp.request('GET', url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
            res = await resp.json()
            res = res['data']
            vurl = f"https://www.bilibili.com/video/av{res['aid']}\n"
            title = f"标题：{res['title']}\n"
            up = f"UP主：{res['owner']['name']} \n"
            pic_url = res['pic']
            msg = str(title)+str(vurl)+str(up)
        return msg, pic_url
    except Exception as e:
        msg = "视频解析出错--Error: {}".format(type(e))
        return msg, None

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


global dailydict
dailydict = []
# global pushmsg
# pushmsg = []
# global pushflag
# pushflag = False
routes = web.RouteTableDef()

@routes.post('/')
async def post_handler(request):
    json_obj = await request.json()
    if json_obj['type'] == 'GroupMessage':
        msgchain = json_obj['messageChain']
        sendername = json_obj['sender']['memberName']
        char = '#### '
        at_flag = 0
        mark_flag = 0
        at_id = 0
        group_id = json_obj['sender']['group']['id']
        for i in msgchain:
            if i['type'] == 'Source':
                gettime = time.strftime("%H:%M:%S ", time.localtime(i['time']))
                char = char + gettime +' '+sendername + '：\n\n'
            elif i['type'] == 'Quote':
                char = char + '<blockquote>'+ i['origin'][0]['text'] +'</blockquote>\n '
            elif i['type'] == 'Plain':
                char = char + i['text']
                if '标记' in i['text']:
                    mark_flag = 1
            elif i['type'] == 'Image':
                char = char + '![]('+i['url']+'")'
            elif i['type'] == 'Face':
                char = char + '[' + i['name'] + ']'
            elif i['type'] == 'At':
                #char = chat + '(@'+str(i['target'])[:2]+'****'+str(i['target'])[-2:]+') '
                char = char + '(@了某人) '
                at_flag = 1
                at_id = i['target']
            elif i['type'] == 'Xml':
                url = re.findall(r'url=\"(.+?)\"',i['xml'])[0]
                title = re.findall(r'\<title\>(.+?)\</title\>',i['xml'])[0]
                char = char + ' ['+title+']'+'('+url+')'
            elif i['type'] == 'App':
                dat = json.loads(i['content'])
                url = dat['meta']['detail_1']['qqdocurl']
                title = dat['meta']['detail_1']['desc']
                char = char + ' ['+title+']'+'('+url+')'
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
        print(char)
        if json_obj['sender']['id'] == 1747222904 and at_flag == 1 and mark_flag == 1:
            with open ('./block.json','r',encoding='utf-8') as f:
                block_list = json.load(f)
            if str(at_id) in block_list.keys():
                block_list[str(at_id)] = block_list[str(at_id)] + 1
            else:
                block_list[str(at_id)] = 1
            with open ('./block.json','w',encoding='utf-8') as f:
                f.write(json.dumps(block_list,indent=2,ensure_ascii=False))
            with open ('./recall.json','r',encoding='utf-8') as f:
                recall_list = json.load(f)
            temp_reply = "-> 该用户已被标记" + str(block_list[str(at_id)]) +"次" 
            if str(at_id) in recall_list.keys():
                temp_reply = temp_reply + "，被撤回发言" + str(recall_list[str(at_id)])+ "次"
            body = {
           'command': "sendGroupMessage",
           'content': {
               "sessionKey":"",
               "target":group_id,
               "messageChain":[
                   { "type":"Plain", "text":temp_reply}
               ]}}
            return web.json_response(body)
        else:
            return web.Response()
    elif json_obj['type'] == 'BotInvitedJoinGroupRequestEvent':
        if json_obj['fromId'] == '1747222904':
            body = {
                'command': "resp_botInvitedJoinGroupRequestEvent",
                'content': {
                    "sessionKey":"",
                    "eventId":json_obj['eventId'],
                    "fromId":json_obj['fromId'],
                    "groupId":json_obj['groupId'],
                    "operate":0,
                    "message":""
                }}
            return web.json_response(body)
    elif json_obj['type'] == 'MemberJoinRequestEvent':
        #{'type': 'MemberJoinRequestEvent', 'eventId': 1633094289803757, 'message': '问题：请输入asoul\n答案：asoul', 'fromId': 1465887523, 'groupId': 614391357, 'groupName': 'S1 A综QQ群纯良分宗', 'nick': '向晚大魔王'}
        # blacklist = (2508649368)
        #这里直接填数字
        if '答案：asoul' in json_obj['message']:
            body = {
                'command': "resp_memberJoinRequestEvent",
                'content': {
                    "sessionKey":"",
                    "eventId":json_obj['eventId'],
                    "fromId":json_obj['fromId'],
                    "groupId":json_obj['groupId'],
                    "operate":0,
                    "message":""
                }}
            return web.json_response(body)
        else:
            body = {
                'command': "resp_memberJoinRequestEvent",
                'content': {
                    "sessionKey":"",
                    "eventId":json_obj['eventId'],
                    "fromId":json_obj['fromId'],
                    "groupId":json_obj['groupId'],
                    "operate":1,
                    "message":""
                }}
            return web.json_response(body)
#    elif json_obj['type'] == 'MemberJoinEvent':
#        body = {
#            'command': "sendGroupMessage",
#            'content': {
#                "sessionKey":"",
#                "target":590331701,
#                "messageChain":[
#                    { "type":"Plain", "text":"欢迎来到S1A-soul楼纯良公开群\n\n" },
#                    { "type":"Plain", "text":"本群立足于S1A-soul楼\n\n" },
#                    { "type":"Plain", "text":"讨论内容纯良，不涉政不违法不盒不搞直球黄色不辱骂吵架，谢绝皮套账号\n\n"},
#                    { "type":"Plain", "text":"聊天内容公开，进出群随意，群聊消息均存档，请谨言慎行。备份群：128740624\n\n"},
#                    { "type":"Plain", "text":"存档链接：https://github.com/TomoeMami/qqlog"}
#                ]}}
#        return web.json_response(body)
    # elif json_obj['type'] == 'ReplyPush':
    #     pushflag = True
    #     pushmsg = json_obj['msg']
    #     return web.Response()
    elif json_obj['type'] == 'GroupRecallEvent':
        if json_obj['operator']['id'] == 1747222904:
            with open ('./recall.json','r',encoding='utf-8') as f:
                block_list = json.load(f)
            author_id = json_obj['authorId']
            group_id = json_obj['group']['id']
            if str(author_id) in block_list.keys():
                block_list[str(author_id)] = block_list[str(author_id)] + 1
            else:
                block_list[str(author_id)] = 1
            with open ('./recall.json','w',encoding='utf-8') as f:
                f.write(json.dumps(block_list,indent=2,ensure_ascii=False))
        #     body = {
        #     'command': "sendGroupMessage",
        #     'content': {
        #         "sessionKey":"",
        #         "target":group_id,
        #         "messageChain":[
        #             { "type":"Plain", "text":"-> 该用户发言已被管理撤回" + str(block_list[str(author_id)]) +"次" }
        #         ]}}
        #     return web.json_response(body)
        # else:
        return web.Response()
    else:
        return web.Response()

app = web.Application()
app.add_routes(routes)

web.run_app(app, host='0.0.0.0', port=1314)


