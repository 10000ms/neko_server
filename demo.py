# -*- coding: utf-8 -*-
import os

from neko_server.server import server_start
from neko_server.component.route import Router
from neko_server.conf.base import setting as base
from neko_server.conf.setting_manage import SettingManage

from routes import routes_publish


def route():
    r = Router()
    r.update_route(routes_publish.publish_handler)
    return r


def setting():
    config_dict = {
        'host': '127.0.0.1',
        'port': 9654,
        'static_path': os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static',
        ),
        'template_path': os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'template',
        ),
    }
    s = SettingManage(base)
    s.update_setting(config_dict)
    return s


def main():
    s = setting()
    r = route()
    # 启动服务器
    server_start(s, r)


if __name__ == '__main__':
    main()
