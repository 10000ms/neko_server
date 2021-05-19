from neko_server.views.common import render_template
from neko_server.http.response import Response
from neko_server.views.error import error
from neko_server.views.common import redirect

from model.user import User


def user_index(request):
    """
    用户主页路由
    """
    session = request.cookies.get('session', None)
    login = False
    current_user = '未登录用户'
    if session is not None:
        u = User.current_user(session)
        if u is not None:
            current_user = u.username
            login = True
    users = User.all()
    d = {
        'user': users,
        'current_user': current_user,
        'login': login,
    }
    return render_template(request, 'user_index.html', d)


def user_login(request):
    """
    用户登录路由
    """
    m = request.method
    if m == 'get':
        return render_template(request, 'user_login.html')
    elif m == 'post':
        d = request.form()
        account = d['account']
        password = d['password']
        u = User.login(account, password)
        if u is not None:
            r = Response(request.setting)
            session = u.create_session()
            r.add_cookie('session', session, Path='/')
            return redirect(request, '/user', response=r)
        else:
            return error(request, 400, '账号密码错误')
    else:
        return error(request, 405)


def user_logout(request):
    """
    用户登出路由
    """
    session = request.cookies.get('session', None)
    if session is not None:
        user = User.current_user(session)
        user.logout()
        return redirect(request, '/user')
    else:
        return error(request, 400, '用户未登陆')


def user_register(request):
    """
    用户注册路由
    """
    m = request.method
    if m == 'get':
        return render_template(request, 'user_register.html')
    elif m == 'post':
        d = request.form()
        account = d['account']
        password = d['password']
        username = d['username']
        repeat_password = d['repeat_password']
        if repeat_password == password:
            u, result = User.register(account, password, username)
            if u is not None:
                r = Response(request.setting)
                session = u.create_session()
                r.add_cookie('session', session, Path='/')
                return redirect(request, '/user', response=r)
            else:
                return error(request, 400, result)
        else:
            return error(request, 400, '两次密码不一致')
    else:
        return error(request, 405)
