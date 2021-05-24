import os

# 框架基础配置
setting = dict(
    host='127.0.0.1',
    port=9655,

    standard_format='utf-8',

    security_key='63865f1c34cc4ba2bfa72032de6d9d03',

    http_state={
        200: 'OK',
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
