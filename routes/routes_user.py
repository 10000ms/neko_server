# -*- coding: utf-8 -*-
from neko_server.views.common import render_template

from model.user import User


def user_index(request):
    session = request.cookies.get('session', None)
    if session is not None:
        u = User.current_user(request)
        if u:
            current_user = u.username
        else:
            current_user = '未登录用户'
    else:
        current_user = '未登录用户'
    users = User.all()
    d = {
        'user': users,
        'current_user': current_user,
    }
    return render_template(request, 'user_index.html', d)


def user_login(request):
    return render_template('note_index.html')


def user_logout(request):
    return render_template('note_index.html')


def user_register(request):
    return render_template('note_index.html')


user_handler = {
    '/user': user_index,
    '/user/login': user_index,
    '/user/logout': user_index,
    '/user/register': user_index,
}
