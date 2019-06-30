# -*- coding: utf-8 -*-
import os

setting = dict(
    host='127.0.0.1',
    port=9655,

    standard_format='utf-8',

    security_key='a7s8d7aS98d7a8Rsd7aG8sd90',

    http_state={
        200: 'Ok',
        400: 'Bad Request',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        500: 'Internal Server Error',
    },

    # 本地文件数据库的存放地址
    neko_db_data_path=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'data',
    ),

    # 静态文件的存放地址
    static_path=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'static',
    ),

    # html模版文件的存放地址
    template_path=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'template',
    ),
)
