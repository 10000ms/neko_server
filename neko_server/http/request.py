from json import loads
from urllib.parse import unquote_plus

from ..utils.log import (
    log,
    log_error,
)
from .header import (
    HttpHeader,
    SingleHttpHeader,
)


class HTTPError(Exception):
    pass


class Request:
    """
    request对象
    """

    def __init__(self, raw_data, setting):
        header, self.body = raw_data.split('\r\n\r\n', 1)
        h = header.split('\r\n')

        parts = h[0].split()
        self.method = parts[0]
        self.method = self.method.lower()
        self.version = parts[-1]
        part = parts[1]
        self.path = ''
        self.query = {}
        self.parse_path(part)

        self.headers = {}
        self.cookies = {}
        self.add_headers(h[1:])

        self.setting = setting

        log('Request init over', self.__dict__)

    def form(self):
        """
        将 form data转化为dict
        """
        body = unquote_plus(self.body)
        args = body.split('&')
        r = {}
        for a in args:
            k, v = a.split('=')
            r[k] = v
        return r

    def json(self):
        return loads(self.body)

    def add_headers(self, header):
        """
        处理头部信息

        :param header:
            Host: localhost:9654
            Connection: keep-alive
            Pragma: no-cache
        """
        for l in header:
            k, v = l.split(': ', 1)
            self.headers[k] = v

        if 'Cookie' in self.headers:
            cookies = self.headers['Cookie']
            cookies = cookies.split('; ')
            for c in cookies:
                k, v = c.split('=', 1)
                self.cookies[k] = v

    def parse_path(self, part):
        """
        处理path
        :param part: /aaa?message=hello&author=bbb
        """
        if '?' in part:
            self.path, query_string = part.split('?', 1)
            args = query_string.split('&')
            for a in args:
                if '=' in a:
                    k, v = a.split('=')
                    self.query[k] = v
        else:
            self.path = part


class RequestV2:
    """
    request对象
    """

    def __init__(self, setting):
        self.raw_header = b''
        self.raw_body = b''
        self.setting = setting
        self.end_parse_header = False

    def parse_header(self):
        header = self.raw_header.decode()
        h = header.split('\r\n')

        parts = h[0].split()
        self.method = parts[0]
        self.method = self.method.lower()
        self.version = parts[-1]
        part = parts[1]
        self.path = ''
        self.query = {}
        self.parse_path(part)

        self.headers = HttpHeader()
        self.cookies = {}
        self.add_headers(h[1:])

        if 'Content-Length' in self.headers:
            self.content_length = int(self.headers['Content-Length'].value)
        else:
            self.content_length = None

        self.end_parse_header = True

    def no_body_request(self):
        return self.method in ['head', 'get', 'option']

    def parse_body(self):
        if self.no_body_request():
            self.raw_body = b''
        else:
            self.body = self.raw_body.decode()

    def form(self):
        """
        将 form data转化为dict
        """
        body = unquote_plus(self.body)
        args = body.split('&')
        r = {}
        for a in args:
            k, v = a.split('=')
            r[k] = v
        return r

    def json(self):
        return loads(self.body)

    def add_headers(self, header):
        """
        处理头部信息

        :param header:
            Host: localhost:9654
            Connection: keep-alive
            Pragma: no-cache
        """
        for l in header:
            k, v = l.split(': ', 1)
            s = SingleHttpHeader(k, v)
            self.headers.add_header(s)

        if 'Cookie' in self.headers:
            cookies = self.headers['Cookie'].value
            cookies = cookies.split('; ')
            for c in cookies:
                k, v = c.split('=', 1)
                self.cookies[k] = v

    def parse_path(self, part):
        """
        处理path
        :param part: /aaa?message=hello&author=bbb
        """
        if '?' in part:
            self.path, query_string = part.split('?', 1)
            args = query_string.split('&')
            for a in args:
                if '=' in a:
                    k, v = a.split('=')
                    self.query[k] = v
        else:
            self.path = part


class RawRequestHandler:

    def __init__(self, settings, connection, buffer_size, request_handler):
        self.settings = settings
        self.connection = connection
        self.buffer_size = buffer_size

        self.unhandler_buffer = b''
        self.current_request = RequestV2(self.settings)
        self.waiting_handler_request = []

        self.request_handler = request_handler

        self.end_connect = False

    def header_end_func(self):
        if self.unhandler_buffer[-4:] == b'\r\n\r\n':
            self.current_request.raw_header = self.unhandler_buffer[:-4]
            self.current_request.parse_header()
            self.unhandler_buffer = b''

    def check_end_connect(self):
        connection_key = 'Connection'
        if self.current_request.version in ['1.0', '1.1']:
            if self.current_request.version == '1.0':
                if (connection_key not in self.current_request.headers
                        or self.current_request.headers[connection_key].value != 'keep-alive'):
                    self.end_connect = True
            elif self.current_request.version == '1.1':
                if (connection_key in self.current_request.headers
                        and self.current_request.headers[connection_key].value == 'close'):
                    self.end_connect = True
        else:
            self.end_connect = True

    def body_end_func(self):
        if self.current_request.content_length and len(self.unhandler_buffer) == self.current_request.content_length:
            self.current_request.raw_body = self.unhandler_buffer
            self.current_request.parse_body()
            self.unhandler_buffer = b''
            # 确认是否需要关闭连接
            self.check_end_connect()
            # 重新使用一个request
            self.waiting_handler_request.append(self.current_request)
            self.current_request = RequestV2(self.settings)
        elif self.current_request.content_length == 0:
            self.current_request.parse_body()
            self.unhandler_buffer = b''
            # 确认是否需要关闭连接
            self.check_end_connect()
            # 重新使用一个request
            self.waiting_handler_request.append(self.current_request)
            self.current_request = RequestV2(self.settings)
        elif self.current_request.content_length is None and not self.current_request.no_body_request():
            self.end_connect = True

    @property
    def handle_func(self):
        if self.current_request.end_parse_header is not True:
            return self.header_end_func
        else:
            return self.body_end_func

    def parse(self, buffer):
        log('buffer parse')
        log(buffer)
        log(self.unhandler_buffer)
        for integer in buffer:
            self.unhandler_buffer += bytes([integer])
            f = self.handle_func
            f()

    def read_step(self):
        log('read_step')
        buffer = self.connection.recv(self.buffer_size)
        if buffer == b'':
            raise HTTPError('客户端请求关闭')
        self.parse(buffer)

    def process(self):
        log('process')
        while self.end_connect is False or len(self.waiting_handler_request) > 0:
            # 如果有没有处理的请求，先处理请求
            if len(self.waiting_handler_request) > 0:
                for r in self.waiting_handler_request:
                    self.request_handler(request=r, connection=self.connection)
                return self.end_connect
            else:
                try:
                    self.read_step()
                except IOError as e:
                    log_error(f'process, IOError: {e}')
                    return self.end_connect
                except HTTPError as e:
                    log_error(f'process, HTTPError: {e}')
                    return True
        return self.end_connect
