#!/usr/bin/python
# -*-encoding=utf8 -*-


import time
import socket
import requests
import threading

from server.socket_server import TCPServer
from server.base_http_server import BaseHTTPServer
from handler.base_handler import StreamRequestHandler
from handler.base_http_handler import BaseHTTPRequestHandler


class TestBaseRequestHandler(StreamRequestHandler):

    def __init__(self, request, client_address):
        StreamRequestHandler.__init__(self, request, client_address)

    def handle(self):
        time.sleep(1)
        print('TestBaseRequestHandler.handle sleep 1s.')


class SocketServerTest:

    def run_server(self):
        tcp_server = TCPServer(('127.0.0.1', 9999), TestBaseRequestHandler)
        tcp_server.serve_forever()
        # tcp_server.serve_forever_multithread()

    def client_connect(self):
        client = socket.socket()
        client.connect(('127.0.0.1', 9999))

    def gen_clients(self, num):
        clients = []
        for i in range(num):
            client_thread = threading.Thread(target=self.client_connect)
            clients.append(client_thread)
        return clients

    def run(self):
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()
        clients = self.gen_clients(10)
        for client in clients:
            client.start()

        server_thread.join()
        for client in clients:
            client.join()


class BaseHTTPServerTest:

    host = '127.0.0.1'
    port = 9999

    def run_server(self):
        BaseHTTPServer(('127.0.0.1', 9999), BaseHTTPRequestHandler).serve_forever()

    def verify(self, response):
        pass

    def run(self):
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()
        response = requests.get('http://%s:%d' % (self.host, self.port))
        self.verify(response)


if __name__ == '__main__':
    # SocketServerTest().run()
    BaseHTTPServerTest().run()
