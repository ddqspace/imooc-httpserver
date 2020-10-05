# -*- encoding=utf-8 -*-

import logging
import posixpath
import mimetypes

from util import *

from handler.base_handler import StreamRequestHandler

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


DEFAULT_ERROR_MESSAGE = """\
<head>
<title>Error response</title>
</head>
<body>
<h1>Error response</h1>
<p>Error code %(code)d.
<p>Message: %(message)s.
<p>Error code explanation: %(code)s = %(explain)s.
</body>
"""

DEFAULT_ERROR_CONTENT_TYPE = "text/html"


class BaseHTTPRequestHandler(StreamRequestHandler):

    default_http_version = 'HTTP/1.1'

    def __init__(self, server, request, client_address):
        self.request_line = None
        self.method = None
        self.path = None
        self.version = None
        self.headers = None
        self.body = None
        StreamRequestHandler.__init__(self, server, request, client_address)

    def parse_headers(self):
        headers = {}
        while True:
            line = self.readline()
            if line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                headers[key] = value
            else:
                break
        return headers

    def parse_request(self):
        # 解析请求行
        self.method = None
        self.path = None
        self.version = None
        self.request_line = self.readline()
        print(self.request_line)
        words = self.request_line.split()
        self.method, self.path, self.version = words
        # 解析请求头
        self.headers = self.parse_headers()
        # 解析请求body
        key = 'Content-Length'
        if key in self.headers.keys():
            body_length = int(self.headers.get(key).strip())
            self.body = self.read(body_length)
        return True

    def handle(self):
        try:
            if not self.parse_request():
                return
            method_name = 'do_' + self.method
            if not hasattr(self, method_name):
                self.write_error(501, "Unsupported method (%r)" % self.method)
                return
            method = getattr(self, method_name)
            method()
            self.send()
        except Exception as e:
            logging.exception(e)
            return

    def write_error(self, code, msg):
        s_msg, l_msg = self.responses[code]
        if msg:
            s_msg = msg
        logging.error('code %s, message %s' % (code, msg))
        self.write_response(code, msg)

        content = None
        if code >= 200:
            content = (DEFAULT_ERROR_MESSAGE % {
                'code': code,
                'message': s_msg,
                'explain': l_msg
            })
            self.write_header("Content-Type", DEFAULT_ERROR_CONTENT_TYPE)
        self.end_headers()

        if self.method != 'HEAD' and content:
            self.write_content(content)

    def write_response(self, code, message=None):
        logging.info("%s, code: %d." % (self.request_line, code))
        if message is None:
            if code in self.responses:
                message = self.responses[code][0]
            else:
                message = ''
        response = "%s %d %s\r\n" % (self.default_http_version, code, message)
        self.write_content(response)
        self.write_header('Server', '%s:%s' % (self.server.server_name, self.server.version))
        self.write_header('Date', date_time_string())

    def write_header(self, keyword, value):
        msg = "%s: %s\r\n" % (keyword, value)
        self.write_content(msg)

    def end_headers(self):
        self.write_content('\r\n')

    def do_GET(self):
        msg = '<h1>Hello World</h1>'
        self.write_response(200, len(msg))
        # msg = DEFAULT_ERROR_MESSAGE
        self.write_header('Content-Length', len(msg))
        self.write_header('Content-type', 'text/html')
        self.end_headers()
        self.write_content(msg)

    def do_POST(self):
        pass

    def do_DELETE(self):
        pass

    def do_UPDATE(self):
        pass

    responses = {
        100: ('Continue', 'Request received, please continue'),
        101: ('Switching Protocols',
              'Switching to new protocol; obey Upgrade header'),

        200: ('OK', 'Request fulfilled, document follows'),
        201: ('Created', 'Document created, URL follows'),
        202: ('Accepted',
              'Request accepted, processing continues off-line'),
        203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
        204: ('No Content', 'Request fulfilled, nothing follows'),
        205: ('Reset Content', 'Clear input form for further input.'),
        206: ('Partial Content', 'Partial content follows.'),

        300: ('Multiple Choices',
              'Object has several resources -- see URI list'),
        301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
        302: ('Found', 'Object moved temporarily -- see URI list'),
        303: ('See Other', 'Object moved -- see Method and URL list'),
        304: ('Not Modified',
              'Document has not changed since given time'),
        305: ('Use Proxy',
              'You must use proxy specified in Location to access this '
              'resource.'),
        307: ('Temporary Redirect',
              'Object moved temporarily -- see URI list'),

        400: ('Bad Request',
              'Bad request syntax or unsupported method'),
        401: ('Unauthorized',
              'No permission -- see authorization schemes'),
        402: ('Payment Required',
              'No payment -- see charging schemes'),
        403: ('Forbidden',
              'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed',
              'Specified method is invalid for this resource.'),
        406: ('Not Acceptable', 'URI not available in preferred format.'),
        407: ('Proxy Authentication Required', 'You must authenticate with '
                                               'this proxy before proceeding.'),
        408: ('Request Timeout', 'Request timed out; try again later.'),
        409: ('Conflict', 'Request conflict.'),
        410: ('Gone',
              'URI no longer exists and has been permanently removed.'),
        411: ('Length Required', 'Client must specify Content-Length.'),
        412: ('Precondition Failed', 'Precondition in headers is false.'),
        413: ('Request Entity Too Large', 'Entity is too large.'),
        414: ('Request-URI Too Long', 'URI is too long.'),
        415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
        416: ('Requested Range Not Satisfiable',
              'Cannot satisfy request range.'),
        417: ('Expectation Failed',
              'Expect condition could not be satisfied.'),

        500: ('Internal Server Error', 'Server got itself in trouble'),
        501: ('Not Implemented',
              'Server does not support this operation'),
        502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
        503: ('Service Unavailable',
              'The server cannot process the request due to a high load'),
        504: ('Gateway Timeout',
              'The gateway server did not receive a timely response'),
        505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
    }

    def guess_type(self, path):
        if not mimetypes.inited:
            mimetypes.init()
        base, ext = posixpath.splitext(path)
        if ext in mimetypes.types_map:
            return mimetypes.types_map[ext]
        ext = ext.lower()
        if ext in mimetypes.types_map:
            return mimetypes.types_map[ext]
        else:
            return 'text/plain'


if __name__ == '__main__':
    from server.base_http_server import BaseHTTPServer
    BaseHTTPServer(('127.0.0.1', 9999), BaseHTTPRequestHandler).serve_forever()
