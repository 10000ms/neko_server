# -*- coding: utf-8 -*-
import socket
import _thread

from conf import setting
from http.request import Request
from http.response import Response
from utils.log import log
from component.route import Router
from views.error import route_not_found


def response_for_path(request):
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    r = Router()
    request_handler = r.get(request.path, route_not_found)
    log('request_handler', request_handler)
    response = request_handler(request)
    if isinstance(response, Response):
        return response
    else:
        raise TypeError('返回类型错误，必须为http.response.Response或其子类')


def request_from_connection(connection):
    c = connection
    request = b''
    buffer_size = 1024
    while True:
        r = c.recv(buffer_size)
        request += r
        if len(r) < buffer_size:
            request = request.decode(setting.standard_format)
            return request


def request_validation(request):
    """
    检查请求，防止出现因chrome一类的浏览器的空请求错误
    """
    return '\r\n\r\n' in request


def process_request(connection):
    with connection as c:
        r = request_from_connection(c)
        log('accept request\n <{}>'.format(r))
        if request_validation(r) is True:
            request = Request(r)
            response = response_for_path(request)
            r = response.make_response()
            log('send response\n <{}>'.format(r))
            c.sendall(r)


def server_start(host=None, port=None):
    if host is None:
        host = setting.host
    if port is None:
        port = setting.port

    log('start web server in {}:{}'.format(host, port))

    with socket.socket() as s:
        s.bind((host, port))
        s.listen()
        while True:
            connection, address = s.accept()
            log('accept ip: <{}>'.format(address))
            _thread.start_new_thread(process_request, (connection, ))
