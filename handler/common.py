from neko_server.views.common import render_template
from neko_server.http.response import Response


def index(request):
    return render_template(request, 'index.html')


# Test
# def index(request):
#     return Response(request, request.setting)
