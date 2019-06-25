# -*- coding: utf-8 -*-
import os

setting = dict(
    host='127.0.0.1',
    port=9655,

    # RFC 2616
    standard_format='iso-8859-1',

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
        'data'
    ),

    # 静态文件的存放地址
    static_path=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'static'
    ),

    # html模版文件的存放地址
    template_path=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'template'
    ),
)
