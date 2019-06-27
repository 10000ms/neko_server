# -*- coding: utf-8 -*-
from neko_server.views.common import render_template


def user_index(request):
    return render_template('note_index.html')


def user_login(request):
    return render_template('note_index.html')


def user_logout(request):
    return render_template('note_index.html')


def user_register(request):
    return render_template('note_index.html')


note_handler = {
    '/user': user_index,
    '/user/login': user_index,
    '/user/logout': user_index,
    '/user/register': user_index,
}
