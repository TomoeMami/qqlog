from aiohttp import web
import json,time,re,datetime,os
from urllib.parse import unquote
import aiohttp

async def b23_extract(text):
    b23 = re.compile(r'b23.tv/(\w+)|(bili(22|23|33|2233).cn)/(\w+)', re.I).search(text.replace("\\",""))
    url = f'https://{b23[0]}'
    async with aiohttp.request('GET', url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
        r = str(resp.url)
    return r

async def extract(text:str):
    try:
        aid = re.compile(r'av\d+', re.I).search(text)
        bvid = re.compile(r'BV([a-zA-Z0-9])+', re.I).search(text)
        epid = re.compile(r'ep\d+', re.I).search(text)
        ssid = re.compile(r'ss\d+', re.I).search(text)
        mdid = re.compile(r'md\d+', re.I).search(text)
        room_id = re.compile(r"live.bilibili.com/(blanc/|h5/)?(\d+)", re.I).search(text)
        cvid = re.compile(r'(cv|/read/(mobile|native)(/|\?id=))(\d+)', re.I).search(text)
        if bvid:
            url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid[0]}'
        elif aid:
            url = f'https://api.bilibili.com/x/web-interface/view?aid={aid[0][2:]}'
        elif epid:
            url = f'https://bangumi.bilibili.com/view/web_api/season?ep_id={epid[0][2:]}'
        elif ssid:
            url = f'https://bangumi.bilibili.com/view/web_api/season?season_id={ssid[0][2:]}'
        elif mdid:
            url = f'https://bangumi.bilibili.com/view/web_api/season?media_id={mdid[0][2:]}'
        elif room_id:
            url = f'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={room_id[2]}'
        elif cvid:
            url = f"https://api.bilibili.com/x/article/viewinfo?id={cvid[4]}&mobi_app=pc&from=web"
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
        up = f"UP主：{res['owner']['name']} (https://space.bilibili.com/{res['owner']['mid']})\n"
        desc = f"简介：{res['desc']}"
        desc_list = desc.split("\n")
        desc = ""
        for i in desc_list:
            if i:
                desc += i + "\n"
        desc_list = desc.split("\n")
        if len(desc_list) > 4:
            desc = desc_list[0] + "\n" + desc_list[1] + "\n" + desc_list[2] + "……"
        msg = str(vurl)+str(title)+str(up)+str(desc)
        return msg, vurl
    except Exception as e:
        msg = "视频解析出错--Error: {}".format(type(e))
        return msg, None

async def bangumi_detail(url):
    try:
        async with aiohttp.request('GET', url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
            res = await resp.json()
            res = res['result']
        if "season_id" in url:
            vurl = f"https://www.bilibili.com/bangumi/play/ss{res['season_id']}\n"
        elif "media_id" in url:
            vurl = f"https://www.bilibili.com/bangumi/media/md{res['media_id']}\n"
        else:
            epid = re.compile(r'ep_id=\d+').search(url)
            vurl = f"https://www.bilibili.com/bangumi/play/ep{epid[0][len('ep_id='):]}\n"
        title = f"标题：{res['title']}\n"
        desc = f"{res['newest_ep']['desc']}\n"
        style = ""
        for i in res['style']:
            style += i + ","
        style = f"类型：{style[:-1]}\n"
        evaluate = f"简介：{res['evaluate']}\n"
        msg = str(vurl)+str(title)+str(desc)+str(style)+str(evaluate)
        return msg, vurl
    except Exception as e:
        msg = "番剧解析出错--Error: {}".format(type(e))
        msg += f'\n{url}'
        return msg, None

async def live_detail(url):
    try:
        async with aiohttp.request('GET', url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
            res = await resp.json()
        if res['code'] == -400 or res['code'] == 19002000:
            msg = "直播间不存在"
            return msg, None
        uname = res['data']['anchor_info']['base_info']['uname']
        room_id = res['data']['room_info']['room_id']
        title = res['data']['room_info']['title']
        live_status = res['data']['room_info']['live_status']
        lock_status = res['data']['room_info']['lock_status']
        parent_area_name = res['data']['room_info']['parent_area_name']
        area_name = res['data']['room_info']['area_name']
        online = res['data']['room_info']['online']
        tags = res['data']['room_info']['tags']
        vurl = f"https://live.bilibili.com/{room_id}\n"
        if lock_status:
            lock_time = res['data']['room_info']['lock_time']
            lock_time = datetime.fromtimestamp(lock_time).strftime("%Y-%m-%d %H:%M:%S")
            title = f"(已封禁)直播间封禁至：{lock_time}\n"
        elif live_status == 1:
            title = f"(直播中)标题：{title}\n"
        elif live_status == 2:
            title = f"(轮播中)标题：{title}\n"
        else:
            title = f"(未开播)标题：{title}\n"
        up = f"主播：{uname} 当前分区：{parent_area_name}-{area_name} 人气上一次刷新值：{online}\n"
        if tags:
            tags = f"标签：{tags}\n"
        player = f"独立播放器：https://www.bilibili.com/blackboard/live/live-activity-player.html?enterTheRoom=0&cid={room_id}"
        msg = str(vurl)+str(title)+str(up)+str(tags)+str(player)
        return msg, vurl
    except Exception as e:
        msg = "直播间解析出错--Error: {}".format(type(e))
        return msg, None

async def article_detail(url):
    try:
        async with aiohttp.request('GET', url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
            res = await resp.json()
            res = res['data']
        cvid = re.compile(r'id=(\d+)').search(url).group(1)
        vurl = f"https://www.bilibili.com/read/cv{cvid}\n"
        title = f"标题：{res['title']}\n"
        up = f"作者：{res['author_name']} (https://space.bilibili.com/{res['mid']})\n"
        view = f"阅读数：{res['stats']['view']} "
        favorite = f"收藏数：{res['stats']['favorite']} "
        coin = f"硬币数：{res['stats']['coin']}"
        share = f"分享数：{res['stats']['share']} "
        like = f"点赞数：{res['stats']['like']} "
        dislike = f"不喜欢数：{res['stats']['dislike']}"
        desc = view + favorite + coin + '\n' + share + like + dislike
        msg = str(vurl)+str(title)+str(up)+str(desc)
        return msg, vurl
    except Exception as e:
        msg = "专栏解析出错--Error: {}".format(type(e))
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

routes = web.RouteTableDef()

@routes.post('/')
async def post_handler(request):
    json_obj = await request.json()
    if json_obj['type'] == 'GroupMessage':
        msgchain = json_obj['messageChain']
        sendername = json_obj['sender']['memberName']
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
        if '\'type\': \'App\'' in str(msgchain):
            b23url = b23_extract(str(msgchain))

        else:
            return web.Response()
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
                    return web.json_response(data=body)
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
        blacklist = ()
        #这里直接填数字
        if '答案：asoul' in json_obj['message']:
            if json_obj['fromId'] not in blacklist:
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
    elif json_obj['type'] == 'MemberJoinEvent':
        body = {
                'command': "sendGroupMessage",
                'content': {
                    "sessionKey":"",
                    "target":614391357,
                    "messageChain":[
                        { "type":"Plain", "text":"请新人查看群公告\n" },
                        { "type":"Plain", "text":"本群所有消息均存档，务必谨言慎行" }
                    ]}}
        return web.json_response(body)
    else:
        return web.Response()

app = web.Application()
app.add_routes(routes)
global dailydict
dailydict = []
web.run_app(app, host='0.0.0.0', port=1314)
