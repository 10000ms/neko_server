# -*- coding: utf-8 -*-
import socket
import _thread

from request import Request
from utils import log


# follow RFC 2616
standard_format = 'iso-8859-1'


def request_from_connection(connection):
    c = connection
    request = b''
    buffer_size = 1024
    while True:
        r = c.recv(buffer_size)
        request += r
        if len(r) < buffer_size:
            request = request.decode(standard_format)
            return request


def process_request(connection):
    with connection as c:
        r = request_from_connection(c)
        log('request\n {}'.format(r))
        request = Request(r)
        # response = response_for_path(request)
        # c.sendall(response)
        c.sendall(b'HTTP/1.1 404 NOT FOUND\r\nContent-Type: text/html\r\n\r\n<h1>NOT FOUND</h1>')


def run(host, port):
    log('start web server in {}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        s.listen()
        while True:
            connection, address = s.accept()
            log('accept ip: <{}>'.format(address))
            _thread.start_new_thread(process_request, (connection, ))


if __name__ == '__main__':
    config_dict = {
        'host': '127.0.0.1',
        'port': 9655,
    }
    run(**config_dict)
