# -*- coding: utf-8 -*-


class Field:

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '{}, {}:{}'.format(self.__class__.__name__, self.column_type, self.name)

    @staticmethod
    def check_value(value):
        return True


class StringField(Field):

    def __init__(self, name=None, primary_key=False, default=None, column_type='varchar(100)'):
        super().__init__(name, column_type, primary_key, default)

    @staticmethod
    def check_value(value):
        return isinstance(value, str)


class BooleanField(Field):

    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)

    @staticmethod
    def check_value(value):
        return isinstance(value, bool)


class IntegerField(Field):

    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)

    @staticmethod
    def check_value(value):
        return isinstance(value, int)


class FloatField(Field):

    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)

    @staticmethod
    def check_value(value):
        return isinstance(value, float)


class TextField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)

    @staticmethod
    def check_value(value):
        return isinstance(value, str)


class DatetimeField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'datetime', False, default)

    @staticmethod
    def check_value(value):
        return isinstance(value, str)
