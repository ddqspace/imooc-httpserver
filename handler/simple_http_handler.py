# -*- encoding=utf-8 -*-


import os
import json
from urllib import parse

from util import date_time_string
from handler.base_http_handler import BaseHTTPRequestHandler

RESOURCES_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../resources')

HOST = '127.0.0.1'
PORT = 8888


class SimpleHTTPHandler(BaseHTTPRequestHandler):

    def _send_head(self, clength, last_modified=date_time_string()):
        self.write_response(200)
        # self.write_header("Content-type", ctype)
        self.write_header("Content-Length", clength)
        self.write_header("Last-Modified", last_modified)
        self.write_header("Access-Control-Allow-Origin", "http://%s:%d" % (HOST, PORT))
        self.end_headers()

    def do_GET(self):
        found, resource_path = self.get_resources(self.path)
        if not found:
            self.write_error(404, 'File not found')
            self.send()
            return

        # ctype = self.guess_type(resource_path)
        f = open(resource_path, 'rb')
        fs = os.fstat(f.fileno())
        clength = str(fs[6])
        self._send_head(clength)
        while 1:
            buf = f.read(1024)
            if not buf:
                break
            self.write_content(buf)
        f.close()

    def get_resources(self, path):
        url_result = parse.urlparse(path)
        resource_path = str(url_result[2])
        if resource_path.startswith('/'):
            resource_path = resource_path[1:]
        # resource_path = RESOURCES_PATH + resource_path
        resource_path = os.path.join(RESOURCES_PATH, resource_path)
        if os.path.exists(resource_path) and os.path.isfile(resource_path):
            return True, resource_path
        return False, resource_path

    def do_POST(self):
        body = json.loads(self.body)
        username = body['username']
        password = body['password']
        if username == 'dongdongqiang' and password == '123456':
            response = {"message": "success", "code": 0}
        else:
            response = {"message": "failed", "code": -1}
        response = json.dumps(response)
        self._send_head(len(response))
        self.write_content(response)


if __name__ == '__main__':
    from server.base_http_server import BaseHTTPServer
    BaseHTTPServer((HOST, PORT), SimpleHTTPHandler).serve_forever()
