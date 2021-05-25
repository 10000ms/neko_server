import os

from neko_server.server import (
    server_start_with_multi_thread,
    server_start_with_selector,
    server_start_with_selector_and_multiprocessing,
    server_start_with_uvloop,
    server_start_with_uvloop_and_multiprocessing,
)
from neko_server.component.route import Router
from neko_server.conf.base import setting as base
from neko_server.conf.setting_manage import SettingManage

from routes import routes_common
from routes import routes_user
from routes import routes_note


def route():
    """
    注册路由
    """
    r = Router()
    r.update_route(routes_user.user_handler)
    r.update_route(routes_note.note_handler)

    r.update_route(routes_common.common_handler)
    return r


def setting():
    """
    设置setting
    """
    config_dict = {
        'host': '127.0.0.1',
        'port': 9655,
        'static_path': os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static',
        ),
        'template_path': os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'template',
        ),
        'mysql': {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'test',
            'password': '123456',
            'db': 'neko',
        },
    }
    s = SettingManage(base)
    s.update_setting(config_dict)
    return s


def main():
    s = setting()
    r = route()
    # 启动服务器
    # server_start_with_multi_thread(s, r)
    # server_start_with_selector(s, r)
    # server_start_with_selector_and_multiprocessing(s, r)
    # server_start_with_uvloop(s, r)
    server_start_with_uvloop_and_multiprocessing(s, r)


if __name__ == '__main__':
    main()
