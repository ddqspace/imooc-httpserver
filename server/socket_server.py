# -*- encoding=utf-8 -*-


import socket
import threading


class TCPServer:

    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5

    def __init__(self, server_address, handler_class):
        self.server_address = server_address
        self.HandlerClass = handler_class
        self.is_shutdown = False
        self.socket = socket.socket(self.address_family,
                                    self.socket_type)
        self.socket.bind(self.server_address)
        self.socket.listen(10)

    def serve_forever_multithread(self):
        while not self.is_shutdown:
            request, client_address = self.get_request()
            try:
                self.process_request_multithread(request, client_address)
            except Exception as e:
                print(e)
            finally:
                self.close_request(request)

    def serve_forever(self):
        while not self.is_shutdown:
            request, client_address = self.get_request()
            try:
                self.process_request(request, client_address)
            except Exception as e:
                print(e)
            finally:
                self.close_request(request)

    def shutdown(self):
        self.is_shutdown = True

    def get_request(self):
        return self.socket.accept()

    def process_request(self, request, client_address):
        handler = self.HandlerClass(self, request, client_address)
        handler.handle()

    def process_request_multithread(self, request, client_address):
        t = threading.Thread(target = self.process_request,
                             args = (request, client_address))
        t.start()

    def close_request(self, request):
        request.shutdown(socket.SHUT_WR)
        request.close()


