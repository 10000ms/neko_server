# -*- coding: utf-8 -*-
from utils.log import log


class Response:

    base_header = {
        'Content-Type': 'text/html',
    }

    def __init__(self, setting, body=''):
        self.version = 'HTTP/1.x'
        self.state_code = 200
        self.state_string = setting.http_state[200]
        self.header = self.base_header.copy()
        self.body = body
        self.cookie = []

        self.setting = setting

    def set_state(self, code, string):
        self.state_code = code
        self.state_string = string

    def formatted_header(self):
        """
        Content-Type: text/html
        """
        header = '{} {} {}\r\n'.format(self.version, self.state_code, self.state_string)
        header += ''.join([
            '{}: {}\r\n'.format(k, v) for k, v in self.header.items()
        ])
        if len(self.cookie) > 0:
            cookie_string = '\r\n'.join(self.cookie)
            header = '{}{}\r\n'.format(header, cookie_string)
        return header

    def add_cookie(self, key, value, *args, **kwargs):
        option = ''
        if len(args) != 0:
            temp_option = '; '.join(args)
            option += '; {}'.format(temp_option)
        if len(kwargs.keys()) != 0:
            temp_option = '; '.join([
                '{}={}'.format(k, v) for k, v in kwargs.items()
            ])
            option += '; {}'.format(temp_option)
        v = value + option
        s = 'Set-Cookie: {}={}'.format(key, v)
        self.cookie.append(s)

    def add_header(self, key, value):
        self.header[key] = value

    def make_response(self):
        header = self.formatted_header()
        header = header.encode(self.setting.standard_format)
        if not isinstance(self.body, bytes):
            self.body = self.body.encode(self.setting.standard_format)
        r = header + b'\r\n' + self.body

        log('Response make_response \r\n', r)

        return r
