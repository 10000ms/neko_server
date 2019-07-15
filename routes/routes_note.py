from neko_server.views.common import render_template
from neko_server.views.error import error
from neko_server.views.common import redirect

from model.user import User
from model.note import Note


def note_index(request):
    """
    留言主页路由
    """
    session = request.cookies.get('session', None)
    login = False
    if session is not None:
        u = User.current_user(session)
        if u is not None:
            login = True
    notes = Note.all()
    d = {
        'login': login,
        'note': notes,
    }
    return render_template(request, 'note_index.html', d)


def note_add(request):
    """
    留言增加路由
    """
    m = request.method
    if m == 'get':
        return render_template(request, 'note_add.html')
    elif m == 'post':
        d = request.form()
        session = request.cookies.get('session', None)
        user = User.current_user(session)
        d.update({
            'user': user.id,
        })
        note = Note.new(d)
        note.save()
        return redirect(request, '/note')
    else:
        return error(request, 405)


def note_edit(request):
    """
    留言编辑路由
    """
    note_id = request.query.get('id', None)
    if note_id is not None:
        note = Note.find_by(id=note_id)
        if note is not None:
            m = request.method
            if m == 'get':
                d = {
                    'note': note,
                }
                return render_template(request, 'note_edit.html', d)
            elif m == 'post':
                d = request.form()
                note.title = d['title']
                note.content = d['content']
                note.save()
                return redirect(request, '/note')
            else:
                return error(request, 405)
    return error(request, 400)


def note_delete(request):
    """
    留言删除路由
    """
    note_id = request.query.get('id', None)
    if note_id is not None:
        Note.delete([note_id, ])
        return redirect(request, '/note')
    else:
        return error(request, 404)


note_handler = {
    '/note': note_index,
    '/note/add': note_add,
    '/note/edit': note_edit,
    '/note/delete': note_delete,
}
