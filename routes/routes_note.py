# -*- coding: utf-8 -*-
from neko_server.views.common import render_template


def note_index(request):
    return render_template('note_index.html')


def note_add(request):
    return render_template('note_index.html')


def note_edit(request):
    return render_template('note_index.html')


def note_delete(request):
    return render_template('note_index.html')


note_handler = {
    '/note': note_index,
    '/note/add': note_add,
    '/note/edit': note_edit,
    '/note/delete': note_delete,
}
