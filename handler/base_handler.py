# -*- encoding=utf-8 -*-


import socket


class BaseRequestHandler:

    def __init__(self, server, request, client_address):
        self.server = server
        self.connection = request
        self.client_address = client_address

    def handle(self):
        pass


class StreamRequestHandler(BaseRequestHandler):

    def __init__(self, server, request, client_address):
        BaseRequestHandler.__init__(self, server, request, client_address)

        self.rfile = self.connection.makefile('rb')
        self.wfile = self.connection.makefile('wb')

        self.wbuf = []

    # 解码成字符串
    def decode(self, msg):
        return msg.decode()

    # 编码成字节码
    def encode(self, msg):
        return bytes(msg, encoding='utf-8')

    def write_content(self, msg):
        if not isinstance(msg, bytes):
            msg = self.encode(msg)
        self.wbuf.append(msg)
        # self.wfile.write(msg)

    def readline(self, length=65536):
        msg = self.rfile.readline(length).strip()
        if not isinstance(msg, str):
            msg = self.decode(msg)
        return msg

    def read(self, length):
        msg = self.rfile.read(length)
        if not isinstance(msg, str):
            msg = self.decode(msg)
        return msg

    def send(self):
        for line in self.wbuf:
            self.wfile.write(line)
        self.wfile.flush()
        self.wbuf = []

    def close(self):
        if not self.wfile.closed:
            try:
                self.wfile.flush()
            except socket.error:
                pass
        self.wfile.close()
        self.rfile.close()
