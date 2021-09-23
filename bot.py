import json,time,re,datetime,os
from urllib.parse import unquote
from http.server import HTTPServer, BaseHTTPRequestHandler

class RequestHandler(BaseHTTPRequestHandler):
    def handler(self):
        print("data:", self.rfile.readline().decode())
        self.wfile.write(self.rfile.readline())
    
    def do_POST(self):
        print(self.headers)
        print(self.command)
        data = self.rfile.read(int(self.headers['content-length']))
        # data = unquote(str(data, encoding='utf-8'))
        # json_obj = json.loads(data)
        json_obj = data.decode()
        print(json_obj)
        self.send_response(200)
        self.end_headers()
if __name__ == "__main__":
    addr = ('', 2334)
    server = HTTPServer(addr, RequestHandler)
    server.serve_forever()
