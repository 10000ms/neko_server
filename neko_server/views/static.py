# -*- coding: utf-8 -*-
import os

from http.response import Response
from views.error import error

# 常见文件对应的HTTP Content-type
# 参考：https://tool.oschina.net/commons
file_type_dict = {
    'tif': 'image/tiff',
    'gif': 'image/gif',
    'ico': 'image/x-icon',
    'jpe': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'jpg': 'image/jpeg',
    'bmp': 'application/x-bmp',
    'svg': 'text/xml',

    'js': 'application/x-javascript',
    'css': 'text/css',
    'html': 'text/html',
    'htm': 'text/html',

    'mp3': 'audio/mp3',
    'wav': 'audio/wav',

    'mp4': 'video/mpeg4',
    'mpg': 'video/mpg',
    'mpeg': 'video/mpg',
    'avi': 'video/avi',

    'ttf': 'font/ttf',
    'eot': 'font/eot',
    'otf': 'font/otf',
    'woff': 'font/woff',
    'woff2': 'font/woff2',
}

default_type = 'application/octet-stream'


def static(request):
    """
    静态资源的处理, 读取图片并生成响应返回
    """
    file_path = request.path.split('/')
    # 第一个为'', 第二个为static，移除
    file_path = file_path[2:]
    path = os.path.join(
        request.setting.static_path,
        *file_path,
    )
    isfile = os.path.isfile(path)
    if isfile:
        # 确定文件类型
        file_name_list = file_path[-1].rsplit('.', 1)
        file_type = file_name_list[-1]
        if len(file_name_list) == 2:
            content_type = file_type_dict.get(file_type.lower(), default_type)
        else:
            content_type = default_type
        with open(path, 'rb') as f:
            r = Response(request.setting, f.read())
            r.add_header('Content-Type', content_type)
            return r
    else:
        return error(request.setting)


static_handler = {
    '/static/*': static,
}
