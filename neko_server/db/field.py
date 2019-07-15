import datetime


class Field:

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default
        self.model_field = True

    def __str__(self):
        return '{}, {}:{}'.format(self.__class__.__name__, self.column_type, self.name)

    @staticmethod
    def check_value(value):
        return value is None


class StringField(Field):

    def __init__(self, name=None, primary_key=False, default=None, column_type='varchar(100)'):
        super().__init__(name, column_type, primary_key, default)

    def check_value(self, value):
        r = super().check_value(value)
        return r or isinstance(value, str)


class BooleanField(Field):

    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)

    def check_value(self, value):
        r = super().check_value(value)
        return r or isinstance(value, bool)


class IntegerField(Field):

    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)

    def check_value(self, value):
        r = super().check_value(value)
        return r or isinstance(value, int)


class FloatField(Field):

    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)

    def check_value(self, value):
        r = super().check_value(value)
        return r or isinstance(value, float)


class TextField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)

    def check_value(self, value):
        r = super().check_value(value)
        return r or isinstance(value, str)


class DatetimeField(Field):

    def __init__(self, name=None, default=None):
        self._default = default
        super().__init__(name, 'datetime', False, default)

    def check_value(self, value):
        r = super().check_value(value)
        return r or isinstance(value, datetime.datetime)

    @property
    def default(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @default.setter
    def default(self, value):
        self._default = value
