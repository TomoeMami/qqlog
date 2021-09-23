import json,time,re,datetime,os
from urllib.parse import unquote
from http.server import HTTPServer, BaseHTTPRequestHandler

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

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global dailydict
        data = self.rfile.read(int(self.headers['content-length']))
        data = unquote(str(data, encoding='utf-8'))
        json_obj = json.loads(data)
        print(json_obj)
        if json_obj['type'] == 'GroupMessage':
            self.send_response(200)
            self.end_headers()
            msgchain = json_obj['messageChain']
            # sendername = json_obj['sender']['memberName'] +'('+str(json_obj['sender']['id'])[:2]+'****'+str(json_obj['sender']['id'])[-2:]+')'
            sendername = json_obj['sender']['memberName']
            # print(json_obj)
            char = '#### '
            for i in msgchain:
                if i['type'] == 'Source':
                    gettime = time.strftime("%H:%M:%S ", time.localtime(i['time']))
                    char = char + gettime +' '+sendername + '：\n\n'
                elif i['type'] == 'Quote':
                    char = char + '<blockquote>'+ i['origin'][0]['text'] +'</blockquote>\n '
                elif i['type'] == 'Plain':
                    char = char + i['text']
                elif i['type'] == 'Image':
                    char = char + '<img src="'+i['url']+'" max_width="50%" />'
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
        elif json_obj['type'] == 'BotInvitedJoinGroupRequestEvent':
            if json_obj['fromId'] == '1747222904':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                data = {
                "sessionKey":"",
                "eventId":json_obj['eventId'],
                "fromId":json_obj['fromId'],
                "groupId":json_obj['groupId'],
                "operate":0,
                "message":""
                }
                self.wfile.write(json.dumps(data).encode('utf-8'))
            else:
                self.send_response(200)
                self.end_headers()
if __name__ == "__main__":
    global dailydict
    dailydict = []
    addr = ('', 2333)
    server = HTTPServer(addr, RequestHandler)
    server.serve_forever()
