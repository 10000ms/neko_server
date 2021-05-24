import typing
import socket
import selectors
import _thread
import functools

from .http.request import (
    Request,
    RawRequestHandler,
)
from .utils.log import log
from .views.error import route_not_found
from .db.mysql import MysqlOperate


def response_for_path(request, route):
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    r = route
    request_handler = r.get(request.path, route_not_found)
    log('request_handler', request_handler)
    response = request_handler(request)
    if hasattr(response, 'make_response'):
        return response
    else:
        raise TypeError('返回类型错误，必须为http.response.Response或其子类, 而返回的是：<{}>'.format(response))


def request_from_connection(connection, setting):
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


def process_request(connection, setting, route):
    with connection as c:
        r = request_from_connection(c, setting)
        log('accept request\n <{}>'.format(r))
        if request_validation(r) is True:
            request = Request(r, setting)
            response = response_for_path(request, route)
            r = response.make_response()
            log('send response\n <{}>'.format(r))
            c.sendall(r)


def set_model(setting):
    """
    设置属性
    """
    MysqlOperate.host = setting.mysql['host']
    MysqlOperate.port = setting.mysql['port']
    MysqlOperate.user = setting.mysql['user']
    MysqlOperate.password = setting.mysql['password']
    MysqlOperate.db = setting.mysql['db']


def server_start_with_multi_thread(setting, route):
    """
    启动服务器
    """
    host = setting.host
    port = setting.port

    set_model(setting)

    log('start web server in {}:{}'.format(host, port))

    with socket.socket() as s:
        s.bind((host, port))
        s.listen()
        while True:
            connection, address = s.accept()
            log('accept ip: <{}>'.format(address))
            _thread.start_new_thread(process_request, (connection, setting, route))


def response_for_path_multiplexing(request, connection, route):
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    r = route
    c = connection
    log(f'get request\n <{request.raw_header}> <{request.raw_body}>')
    request_handler = r.get(request.path, route_not_found)
    log('request_handler', request_handler)
    response = request_handler(request)
    if hasattr(response, 'make_response'):
        resp = response.make_response()
        log('send response\n <{}>'.format(resp))
        c.sendall(resp)
    else:
        raise TypeError('返回类型错误，必须为http.response.Response或其子类, 而返回的是：<{}>'.format(response))


def close_connection(connection):
    try:
        connection.shutdown(socket.SHUT_RDWR)
    except OSError as e:
        log('connection.shutdown e', e)
    connection.close()


def process_request_multiplexing(selector, connection, handler):
    log('in process_request_multiplexing')
    end_connect = handler.process()
    if end_connect is True:
        selector.unregister(connection)
        close_connection(connection)


class TaskItem:

    def __init__(self, func: typing.Callable, params_dict: typing.Dict):
        self.func = func
        self.params_dict = params_dict


def process_accept(selector, accept_socket, setting, route):
    connection, address = accept_socket.accept()
    log('accept ip: <{}>'.format(address))
    connection.setblocking(False)
    handler = RawRequestHandler(
        settings=setting,
        connection=connection,
        buffer_size=1024,
        request_handler=functools.partial(response_for_path_multiplexing, route=route),
    )
    t = TaskItem(
        func=process_request_multiplexing,
        params_dict=dict(selector=selector, connection=connection, handler=handler)
    )
    selector.register(
        fileobj=connection,
        events=selectors.EVENT_READ,
        data=t
    )


def server_start_with_multiplexing(setting, route):
    """
    启动服务器
    """
    host = setting.host
    port = setting.port

    set_model(setting)

    log('start web server in {}:{}'.format(host, port))

    with socket.socket() as s:
        s.setblocking(False)
        server_address = (host, port)
        s.bind(server_address)
        s.listen()

        with selectors.DefaultSelector() as selector:
            t = TaskItem(
                func=process_accept,
                params_dict=dict(selector=selector, accept_socket=s, setting=setting, route=route)
            )
            selector.register(
                fileobj=s,
                events=selectors.EVENT_READ,
                data=t
            )
            while True:
                events = selector.select(timeout=0.1)
                for key, _ in events:
                    f = key.data.func
                    params = key.data.params_dict
                    f(**params)
