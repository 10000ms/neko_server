from ..http.response import Response
from ..component.render import Render


def redirect(request, url, state_code=302, state_string='Found', response=None):
    if response is None:
        r = Response(request.setting)
    else:
        r = response
    r.add_header('Location', url)
    r.set_state(state_code, state_string)
    return r


def render_template(request, template, environment=None):
    if environment is None:
        environment = {}
    s = request.setting
    content = Render(s).render(template, environment)
    r = Response(request.setting, content)
    return r
