# -*- coding: utf-8 -*-
import time


def log(*args, **kwargs):
    time_format = '%Y/%m/%d %H:%M:%S'
    localtime = time.localtime(int(time.time()))
    formatted = time.strftime(time_format, localtime)
    print(formatted, *args, **kwargs)
