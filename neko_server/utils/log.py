import traceback
import time


def log(*args, **kwargs):
    # time_format = '%Y/%m/%d %H:%M:%S'
    # localtime = time.localtime(int(time.time()))
    # formatted = time.strftime(time_format, localtime)
    # print(formatted, flush=True, *args, **kwargs)
    pass


def log_debug(*args, **kwargs):
    # time_format = '%Y/%m/%d %H:%M:%S'
    # localtime = time.localtime(int(time.time()))
    # formatted = time.strftime(time_format, localtime)
    # print(formatted, flush=True, *args, **kwargs)
    pass


def log_error(*args, **kwargs):
    time_format = '%Y/%m/%d %H:%M:%S'
    localtime = time.localtime(int(time.time()))
    formatted = time.strftime(time_format, localtime)
    print(formatted, flush=True, *args, **kwargs)
    traceback.print_exc()
