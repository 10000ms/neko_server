# -*- coding: utf-8 -*-
from db.mysql import MysqlOperate
from db.field import (
    Field,
    IntegerField,
    DatetimeField,
)


_mysql_operate = None


def mysql_operate():
    global _mysql_operate
    if _mysql_operate is None:
        _mysql_operate = MysqlOperate()
    return _mysql_operate


def check_mysql(func):
    def wrapper(cls, *args, **kwargs):
        # 没有建立mysql操作对象则建立连接
        if cls.mysql is None:
            cls.mysql = mysql_operate()
        r = func(cls, *args, **kwargs)
        return r
    return wrapper


class Model:

    # 操作数据库的对象
    mysql = None
    # model类中实际的field
    field_items = None

    security_key = None

    # 默认创建field
    id = IntegerField('id', primary_key=True)
    create_time = DatetimeField('create_time')
    change_time = DatetimeField('change_time')

    @classmethod
    @check_mysql
    def new(cls, data_dict):
        cls._add_field_items()
        m = cls()
        d = {}
        for name, field in cls.field_items():
            if name in data_dict:
                value = data_dict[name]
                check = field.check_value(value)
                if check is True:
                    d[name] = value
                else:
                    raise ValueError('value错误, field:<{}>, value:<{}>'.format(name, value))
            else:
                d[name] = field.default
        for k, v in d.items():
            setattr(m, k, v)
        return m

    @classmethod
    def _add_field_items(cls):
        if cls.field_items is None:
            d = {}
            for i in dir(cls):
                if isinstance(i, Field):
                    d[i.name] = i
            cls.field_items = d

    @classmethod
    def table_name(cls):
        return cls.__name__.lower()

    @classmethod
    @check_mysql
    def delete(cls, model_ids):
        cls.mysql.delete(model_ids)

    @classmethod
    @check_mysql
    def all(cls):
        models = cls.mysql.select_all(cls.table_name())
        r = []
        for m in models:
            model = cls().new(m)
            r.append(model)
        return r

    @classmethod
    @check_mysql
    def find_by(cls, **kwargs):
        model = cls.mysql.select_one(cls.table_name(), kwargs)
        r = cls().new(model)
        return r

    @classmethod
    @check_mysql
    def find_all(cls, **kwargs):
        models = cls.mysql.select_all_by(cls.table_name(), kwargs)
        r = []
        for m in models:
            model = cls().new(m)
            r.append(model)
        return r

    @check_mysql
    def save(self):
        values = self.value_from_field()
        if self.id is None:
            self.mysql.insert(self.table_name(), values)
        else:
            self.mysql.update(self.table_name(), values)

    def value_from_field(self):
        r = {f: getattr(self, f) for f in self.field_items.keys()}
        return r

    def __repr__(self):
        class_name = self.table_name()
        properties = ['{}: <{}>'.format(k, v) for k, v in self.value_from_field()]
        s = '\n'.join(properties)
        return '<{}\n{}>\n'.format(class_name, s)
