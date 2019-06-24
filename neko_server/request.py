# -*- coding: utf-8 -*-
from json import loads
from urllib.parse import unquote_plus

from utils import log


class Request:

    def __init__(self, raw_data):
        header, self.body = raw_data.split('\r\n\r\n', 1)
        h = header.split('\r\n')

        parts = h[0].split()
        self.method = parts[0]
        self.version = parts[-1]
        part = parts[1]
        self.path = ''
        self.query = {}
        self.parse_path(part)

        self.headers = {}
        self.cookies = {}
        self.add_headers(h[1:])

        log('Request init over', self.__dict__)

    def form(self):
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
                k, v = a.split('=')
                self.query[k] = v
        else:
            self.path = part

