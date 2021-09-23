import json,time,re,datetime,os
from urllib.parse import unquote
from http.server import HTTPServer, BaseHTTPRequestHandler

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global dailydict
        data = self.rfile.read(int(self.headers['content-length']))
        data = unquote(str(data, encoding='utf-8'))
        json_obj = json.loads(data)
        print(json_obj)
        self.send_response(200)
        self.end_headers()
if __name__ == "__main__":
    global dailydict
    dailydict = []
    addr = ('', 2334)
    server = HTTPServer(addr, RequestHandler)
    server.serve_forever()
