
from handler.simple_http_handler import SimpleHTTPHandler
from server.base_http_server import BaseHTTPServer


if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 8888
    BaseHTTPServer((HOST, PORT), SimpleHTTPHandler).serve_forever()
