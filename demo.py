# -*- coding: utf-8 -*-
import os

from neko_server.server import server_start
from neko_server.component.route import route
from neko_server.conf import setting

from routes import routes_publish


def set_route():
    route.update_route(routes_publish.publish_handler)


def update_setting():
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
    }
    setting.update_setting(config_dict)


def main():
    update_setting()
    set_route()
    # 启动服务器
    server_start()


if __name__ == '__main__':
    main()
