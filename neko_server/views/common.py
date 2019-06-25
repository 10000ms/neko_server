# -*- coding: utf-8 -*-
from http.response import Response


def redirect(url, state_code=302, state_string='Found'):
    r = Response()
    r.add_header('Location', url)
    r.set_state(state_code, state_string)
    return r
