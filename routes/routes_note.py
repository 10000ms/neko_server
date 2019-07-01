# -*- coding: utf-8 -*-
from neko_server.views.common import render_template
from neko_server.views.error import error
from neko_server.views.common import redirect

from model.user import User
from model.note import Note


def note_index(request):
    session = request.cookies.get('session', None)
    login = False
    if session is not None:
        u = User.current_user(session)
        if u:
            login = True
    notes = Note.all()
    d = {
        'login': login,
        'note': notes,
    }
    return render_template(request, 'note_index.html', d)


def note_add(request):
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
    m = request.method
    if m == 'get':
        return render_template(request, 'note_add.html')
    elif m == 'post':
        d = request.form()
        note_id = request.query.get('id', None)
        if note_id is not None:
            note = Note.find_by(id=note_id)
            note.title = d['title']
            note.content = d['content']
            note.save()
            return redirect(request, '/note')
        else:
            return error(request, 404)
    else:
        return error(request, 405)


def note_delete(request):
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
