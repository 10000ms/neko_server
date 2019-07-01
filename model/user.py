# -*- coding: utf-8 -*-
import hashlib
from uuid import uuid4

from neko_server.db.model import Model
from neko_server.db.field import StringField


class User(Model):

    account = StringField('account')
    password = StringField('password')
    username = StringField('username')
    session = StringField('session')

    def create_session(self):
        s = uuid4().hex
        self.session = s
        self.save()
        return s

    @classmethod
    def current_user(cls, session):
        user = cls.find_by(session=session)
        return user

    @classmethod
    def salted_password(cls, password):
        salted = password + cls.security_key
        hash_password = hashlib.sha256(salted.encode()).hexdigest()
        return hash_password

    @classmethod
    def login(cls, account, password):
        salted = cls.salted_password(password)
        u = cls.find_by(account=account, password=salted)
        if u is not None:
            result = '登陆成功'
        else:
            result = '用户名或密码错误'
        return u, result

    @classmethod
    def register(cls, account, password, username):
        if len(account) > 6 and len(password) > 6 and len(username) > 2:
            d = {
                'account': account,
                'password': cls.salted_password(password),
                'username': username,
            }
            u = cls.new(d)
            u.save()
            result = '注册成功'
        else:
            result = '注册验证不通过'
            u = None
        return u, result
