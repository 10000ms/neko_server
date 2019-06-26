# -*- coding: utf-8 -*-
from http.response import Response
from views.common import render_template


def index(request):
    print('in index', request)
    return render_template('index.html')


index_handler = {
    '/': index,
}
