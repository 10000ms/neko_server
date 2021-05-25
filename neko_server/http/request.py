import asyncio
import socket
import errno
import time
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
        self.keep_alive = False

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
        self.keep_alive = False

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
        if self.unhandler_buffer[-4:] == b'\r\n\r\n' and len(self.unhandler_buffer) == 4:
            # 特殊请求，保持连接，清空unhandler_buffer，不处理
            self.unhandler_buffer = b''
        elif self.unhandler_buffer[-4:] == b'\r\n\r\n':
            self.current_request.raw_header = self.unhandler_buffer[:-4]
            self.current_request.parse_header()
            self.unhandler_buffer = b''
            if not self.current_request.content_length:
                # 确认是否需要关闭连接
                self.check_end_connect()
                # 重新使用一个request
                self.current_request.keep_alive = self.end_connect is False
                self.waiting_handler_request.append(self.current_request)
                self.current_request = RequestV2(self.settings)

    def check_end_connect(self):
        connection_key = 'Connection'
        if self.current_request.version in ['HTTP/1.0', 'HTTP/1.1']:
            if self.current_request.version == 'HTTP/1.0':
                if (connection_key not in self.current_request.headers
                        or self.current_request.headers[connection_key].value not in ['keep-alive', 'Keep-Alive']):
                    self.end_connect = True
            elif self.current_request.version == 'HTTP/1.1':
                if (connection_key in self.current_request.headers
                        and self.current_request.headers[connection_key].value in ['close', 'Close']):
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
            self.current_request.keep_alive = self.end_connect is False
            self.waiting_handler_request.append(self.current_request)
            self.current_request = RequestV2(self.settings)

    @property
    def handle_func(self):
        if self.current_request.end_parse_header is not True:
            return self.header_end_func
        else:
            return self.body_end_func

    def parse(self, buffer):
        for integer in buffer:
            self.unhandler_buffer += bytes([integer])
            f = self.handle_func
            f()

    def read_step(self):
        buffer = None
        try:
            buffer = self.connection.recv(self.buffer_size)
        except socket.error as e:
            if e.errno == errno.EAGAIN:
                return None
        if buffer == b'':
            # 客户端请求关闭
            self.end_connect = True
            log('客户端请求关闭')
        elif buffer is not None:
            self.parse(buffer)

    async def read_step_async(self):
        buffer = None
        try:
            buffer = self.connection.recv(self.buffer_size)
        except socket.error as e:
            if e.errno == errno.EAGAIN:
                return None
        if buffer == b'':
            # 客户端请求关闭
            self.end_connect = True
            log('客户端请求关闭')
        elif buffer is not None:
            self.parse(buffer)

    def process(self):
        while self.end_connect is False or len(self.waiting_handler_request) > 0:
            # 如果有没有处理的请求，先处理请求
            if len(self.waiting_handler_request) > 0:
                for r in self.waiting_handler_request:
                    self.request_handler(request=r, connection=self.connection)
                self.waiting_handler_request = []
                if self.unhandler_buffer == b'':
                    log('process return', self.end_connect)
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
        log('process return', self.end_connect)
        return self.end_connect

    async def process_async(self):
        while self.end_connect is False or len(self.waiting_handler_request) > 0:
            # 如果有没有处理的请求，先处理请求
            if len(self.waiting_handler_request) > 0:
                for r in self.waiting_handler_request:
                    self.request_handler(request=r, connection=self.connection)
                self.waiting_handler_request = []
                if self.unhandler_buffer == b'':
                    log('process return', self.end_connect)
                    return self.end_connect
            else:
                try:
                    await self.read_step_async()
                except IOError as e:
                    log_error(f'process, IOError: {e}')
                    return self.end_connect
                except HTTPError as e:
                    log_error(f'process, HTTPError: {e}')
                    return True
        log('process return', self.end_connect)
        return self.end_connect
