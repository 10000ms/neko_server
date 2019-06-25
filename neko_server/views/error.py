# -*- coding: utf-8 -*-
from http.response import Response
from conf import setting


def error(request, code=404):
    e = setting.http_state
    state_string = e.get(code, e[500])
    content = '<h1>{}<h1>'.format(state_string)
    r = Response(content)
    r.set_state(code, state_string)
    return r
