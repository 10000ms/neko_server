# -*- coding: utf-8 -*-
import os
import json

from conf import setting


def save(data, path):
    """
    把一个dict或者是一个list写入文件
    :param data: dict或者是list
    :param path: 文件保存的路径
    """
    s = json.dumps(data, indent=2, ensure_ascii=False)
    with open(path, 'w+', encoding='utf-8') as f:
        f.write(s)


def load(path):
    """
    从文件导入数据，并转化为dict或者是list
    :param path: 文件保存的路径
    """
    with open(path, 'w+', encoding='utf-8') as f:
        s = f.read()
        return json.loads(s)


class Model:

    def __init__(self, data_dict):
        self.id = data_dict.get('id', None)

    @classmethod
    def db_path(cls):
        """
        获取本地的db
        使用类名作为文件名
        """
        class_name = cls.__name__
        path = os.path.join(
            setting.neko_db_data_path,
            class_name
        )
        return path

    @classmethod
    def create(cls, data_dict):
        m = cls(data_dict)
        m.save()
        return m

    @classmethod
    def delete(cls, model_id):
        ms = cls.all()
        for i, m in enumerate(ms):
            if m.id == model_id:
                del ms[i]
                break
        data = [m.__dict__ for m in ms]
        p = cls.db_path()
        save(data, p)

    @classmethod
    def all(cls):
        p = cls.db_path()
        data = load(p)
        ms = [cls(m) for m in data]
        return ms

    @classmethod
    def find_by(cls, **kwargs):
        for m in cls.all():
            exist = True
            for k, v in kwargs.items():
                if not hasattr(m, k) or not getattr(m, k) == v:
                    exist = False
            if exist:
                return m

    @classmethod
    def find_all(cls, **kwargs):
        ms = []
        for m in cls.all():
            exist = True
            for k, v in kwargs.items():
                if not hasattr(m, k) or not getattr(m, k) == v:
                    exist = False
            if exist:
                ms.append(m)
        return ms

    def save(self):
        ms = self.all()
        if self.id is None:
            # 新建模式
            if len(ms) > 0:
                self.id = ms[-1].id + 1
            else:
                self.id = 1
            ms.append(self)
        else:
            # 修改模式
            for i, m in enumerate(ms):
                if m.id == self.id:
                    ms[i] = self
        data = [m.__dict__ for m in ms]
        p = self.db_path()
        save(data, p)

    def __repr__(self):
        class_name = self.__class__.__name__
        properties = ['{}: <{}>'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '<{}\n{}>\n'.format(class_name, s)
