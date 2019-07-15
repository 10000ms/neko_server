import socket
import _thread

from .http.request import Request
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


def server_start(setting, route):
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
