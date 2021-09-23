from mirai import Mirai, HTTPAdapter, FriendMessage,GroupMessage
from mirai.models.events import BotInvitedJoinGroupRequestEvent,MemberJoinRequestEvent
from mirai.models.message import deserialize

import json,time,re,datetime,os

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

if __name__ == '__main__':
    global dailydict
    dailydict = []
    bot = Mirai(
        qq=3337523821, # 改成你的机器人的 QQ 号
        adapter=HTTPAdapter(verify_key=None, host='localhost', port=8080, single_mode=True)
    )

    @bot.on(FriendMessage)
    def on_friend_message(event: FriendMessage):
        if str(event.message_chain) == '你好':
            return bot.send(event, 'Hello, World!')

    @bot.on(BotInvitedJoinGroupRequestEvent)
    def on_group_invited(event: BotInvitedJoinGroupRequestEvent):
        if str(event.from_id) == '1747222904':
            return bot.allow(event)

    @bot.on(MemberJoinRequestEvent)
    def on_group_join(event: MemberJoinRequestEvent):
        print(str(event.group_name))
        print(str(event.nick))
        print(str(event.message))
        blocklist = ['']
        # if(str(event.from_id) in blocklist):
        #     return bot.decline(event, '您已被加入黑名单')
        # else:
        #     return bot.allow(event)
    
    @bot.on(GroupMessage)
    def on_group_message(event: GroupMessage):
        char = '#### '
        for i in event.message_chain:
            if i.type == 'Source':
                gettime = time.strftime("%H:%M:%S ", time.localtime(i.time))
                char = char + gettime +' '+str(event.sender) + '：\n\n'
            elif i.type == 'Quote':
                char = char + '<blockquote>'+ i.origin.text +'</blockquote>\n '
            elif i.type == 'Plain':
                char = char + i.text
            elif i.type == 'Image':
                char = char + '<img src="'+i.url+'" max_width="50%" />'
            elif i.type == 'Face':
                char = char + '[' + i.name + ']'
            elif i.type == 'At':
                # char = chat + '(@'+str(i['target'])[:2]+'****'+str(i['target'])[-2:]+') '
                char = char + '(@了某人) '
            elif i.type == 'Xml':
                url = re.findall(r'url=\"(.+?)\"',i.xml)[0]
                title = re.findall(r'\<title\>(.+?)\</title\>',i.xml)[0]
                char = char + ' ['+title+']'+'('+url+')'
            elif i.type == 'App':
                dat = json.loads(i.content)
                url = dat['meta']['detail_1']['qqdocurl']
                title = dat['meta']['detail_1']['desc']
                char = char + ' ['+title+']'+'('+url+')'
        char = char + '\n\n*****\n\n'
        char = re.sub(r'\((\d{1})\d+(\d{1})\)','(\1****\2)',char)
        print(char)
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
            
        # msgchain = str(event.message_chain)
        # print(msgchain)
        # sendername = json_obj['sender']['memberName'] +'('+str(json_obj['sender']['id'])[:2]+'****'+str(json_obj['sender']['id'])[-2:]+')'
        # sendername = json_obj['sender']['memberName']
        # # print(json_obj)
        # char = '#### '
        # for i in msgchain:
        #     if i.type == 'Source':
        #         gettime = time.strftime("%H:%M:%S ", time.localtime(i['time']))
        #         char = char + gettime +' '+sendername + '：\n\n'
        #     elif i.type == 'Quote':
        #         char = char + '<blockquote>'+ i['origin'][0]['text'] +'</blockquote>\n '
        #     elif i.type == 'Plain':
        #         char = char + i['text']
        #     elif i.type == 'Image':
        #         char = char + '<img src="'+i['url']+'" max_width="50%" />'
        #     elif i.type == 'Face':
        #         char = char + '[' + i['name'] + ']'
        #     elif i.type == 'At':
        #         # char = chat + '(@'+str(i['target'])[:2]+'****'+str(i['target'])[-2:]+') '
        #         char = char + '(@了某人) '
        #     elif i.type == 'Xml':
        #         url = re.findall(r'url=\"(.+?)\"',i['xml'])[0]
        #         title = re.findall(r'\<title\>(.+?)\</title\>',i['xml'])[0]
        #         char = char + ' ['+title+']'+'('+url+')'
        #     elif i.type == 'App':
        #         dat = json.loads(i['content'])
        #         url = dat['meta']['detail_1']['qqdocurl']
        #         title = dat['meta']['detail_1']['desc']
        #         char = char + ' ['+title+']'+'('+url+')'
        # char = char + '\n\n*****\n\n'
        # char = re.sub(r'\((\d{1})\d+(\d{1})\)','(\1****\2)',char)
        # print(char)
        # dailydict.append(char)
        # if len(dailydict) >= 10:
        #     toyear = datetime.datetime.now().strftime('%Y')
        #     tomonth = datetime.datetime.now().strftime('%Y-%m')
        #     today = datetime.datetime.now().strftime('%Y-%m-%d')
        #     mkdir('./'+toyear)
        #     mkdir('./'+toyear+'/'+tomonth)
        #     with open ('./'+toyear+'/'+tomonth+'/'+today+'.md','a',encoding='utf-8') as f:
        #         f.writelines(dailydict)
        #     dailydict.clear()

    bot.run()
