from json import loads
from urllib.parse import unquote_plus

from ..utils.log import log
from .header import HttpHeader


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

        # TODO header 的key需要处理成标准的模式
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


class RawRequestHandler:
    """
    TODO

    1. 支持HTTP版本：1.0、1.1 的 keep alive机制，header：Connection
    2. body长度的处理以区分不同的request使用同一个connection，header：Content-Length、Transfer-Encoding
    3. body压缩，header：Content-Encoding

    处理逻辑
    1. 使用 unhandler_buffer 放置未处理的buffer
    2. 逐个字节的向unhandler_buffer加入数据
    3. unhandler_buffer可以处理的判断使用传入的函数判断
    4. unhandler_buffer可能放置的是header或者是body

    5. 增加对connection是否保持的判断
    6. 增加异常情况的处理

    """

    def __init__(self, connection, buffer_size):
        self.connection = connection
        self.buffer_size = buffer_size
        self._buffer = b''

        self.http_header = HttpHeader()
        self.header_check_index = None
        self.http_header_end = False
        self.current_content_length = None
        self.done = False

    @property
    def read_size(self):
        if self.current_content_length and self.current_content_length < self.buffer_size:
            return self.current_content_length
        else:
            return self.buffer_size

    def

    def check_header_end(self):
        if self.http_header_end is True:
            return
        for

    def check_single_request_end(self):
        pass

    def single_step(self):
        buffer = self.connection.recv(self.read_size)
        if buffer == b'':
            raise Exception('客户端请求关闭')
        self._buffer += buffer
        self.check_header_end()
        self.check_single_request_end()

    def run(self):
        while self.done is not False:
            self.single_step()
