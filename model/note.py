# -*- coding: utf-8 -*-
from neko_server.db.model import Model
from neko_server.db.field import (
    StringField,
    IntegerField,
)


class Note(Model):

    title = StringField('title')
    content = StringField('content')
    user = IntegerField('user')
