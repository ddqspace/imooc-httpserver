# -*- encoding=utf-8 -*-


from server.base_http_server import BaseHTTPServer


class SimpleHTTPServer(BaseHTTPServer):

    def __init__(self, server_address, handler_class):
        self.server_name = 'SimpleHTTPServer'
        self.version = 'v0.1'
        BaseHTTPServer.__init__(self, server_address, handler_class)
