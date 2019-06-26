# -*- coding: utf-8 -*-
from http.response import Response
from component.render import Render


def redirect(url, state_code=302, state_string='Found'):
    r = Response()
    r.add_header('Location', url)
    r.set_state(state_code, state_string)
    return r


def render_template(template, **kwargs):
    content = Render().render(template, **kwargs)
    r = Response(content)
    return r
