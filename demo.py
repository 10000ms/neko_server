# -*- coding: utf-8 -*-
from neko_server.server import server_start


if __name__ == '__main__':
    config_dict = {
        'host': '127.0.0.1',
        'port': 9655,
    }
    server_start(**config_dict)
