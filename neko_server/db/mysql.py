# -*- coding: utf-8 -*-
import pymysql

from utils.log import log


def check_initialize(func):
    def wrapper(self, *args, **kwargs):
        # 没有建立连接则建立连接
        if self.conn is None:
            self.initialize()
        r = func(self, *args, **kwargs)
        return r
    return wrapper


class MysqlOperate:

    host = None
    port = None
    user = None
    password = None
    db = None

    def __init__(self):
        self.conn = None

    def initialize(self):
        log('MysqlOperate, initialize', self.host, self.port, self.user, self.password, self.db)
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db,
            charset='utf8mb4',
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor
        )

    @check_initialize
    def create(self, table_name, fields):
        field_sql = ['{} {}'.format(k, v) for k, v in fields.items()]
        field_sql = ''.join(field_sql)
        sql_create_table = '''
            CREATE TABLE `{}` (
            {}
        );
        '''.format(table_name, field_sql)
        with self.conn.cursor() as c:
            c.execute(sql_create_table)

    @check_initialize
    def insert(self, table_name, fields):
        fields_name = ['`{}`'.format(k) for k in fields.keys()]
        place_item = ['%s'] * len(fields_name)
        place_item = ','.join(place_item)
        fields_name = ','.join(fields_name)
        value = tuple(fields.values())
        sql = '''
        INSERT INTO
            `{}` ({})
        VALUES
            ({});
        '''.format(table_name, fields_name, place_item)
        # 参数拼接要用 %s，execute 中的参数传递必须是一个 tuple 类型
        with self.conn.cursor() as cursor:
            log('mysql insert', table_name, sql, value)
            cursor.execute(sql, value)

    @check_initialize
    def delete(self, table_name, delete_ids):
        delete_ids = ','.join([str(int(delete_id)) for delete_id in delete_ids])
        sql = '''
        DELETE FROM
            `{}`
        WHERE
            id in ({});
        '''.format(table_name, delete_ids)
        with self.conn.cursor() as cursor:
            log('mysql delete', table_name, sql)
            cursor.execute(sql)

    @check_initialize
    def update(self, table_name, fields):
        update_id = fields.pop('id')
        fields_name = ['`{}`=%s'.format(k) for k in fields.keys()]
        fields_name = ','.join(fields_name)
        values = list(fields.values())
        values.append(update_id)
        values = tuple(values)
        sql_update = '''
        UPDATE
            `{}`
        SET
            {}
        WHERE
            `id`=%s;
        '''.format(table_name, fields_name, update_id)
        with self.conn.cursor() as cursor:
            log('mysql update', table_name, sql_update, values)
            cursor.execute(sql_update, values)

    @check_initialize
    def _select(self, sql, table_name, fields):
        fields_name = ['`{}`=%s'.format(k) for k in fields.keys()]
        fields_name = ' AND '.join(fields_name)
        values = tuple(fields.values())
        sql = sql.format(table_name, fields_name)
        with self.conn.cursor() as cursor:
            log('mysql _select', table_name, sql, values)
            cursor.execute(sql, values)
            result = cursor.fetchall()
            return result

    @check_initialize
    def select_one(self, table_name, fields):
        sql = '''
        SELECT
            *
        FROM
            `{}`
        WHERE
            {}
        LIMIT
            1;
        '''
        r = self._select(sql, table_name, fields)
        return r

    @check_initialize
    def select_all_by(self, table_name, fields):
        sql = '''
        SELECT
            *
        FROM
            `{}`
        WHERE
            {};
        '''
        r = self._select(sql, table_name, fields)
        return r

    @check_initialize
    def select_all(self, table_name):
        sql = '''
        SELECT
            *
        FROM
            `{}`;
        '''.format(table_name)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = iter(cursor)
            return result
