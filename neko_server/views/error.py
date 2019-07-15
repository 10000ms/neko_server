from ..http.response import Response

error_content = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
</head>
<body>
    <h1>{}</h1>
</body>
</html>
"""


def error(request, state_code=404, state_string=None, content=None):
    e = request.setting.http_state
    if state_string is None:
        state_string = e.get(state_code, e[500])
    if content is None:
        content = error_content.format(state_string)
    r = Response(request.setting, content)
    r.set_state(state_code, state_string)
    return r


def route_not_found(request):
    return error(request)
