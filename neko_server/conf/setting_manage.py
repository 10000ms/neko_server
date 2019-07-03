# -*- coding: utf-8 -*-


class SettingManage:
    """
    setting管理器
    """

    def __init__(self, setting):
        self._setting = setting

    def update_setting(self, setting):
        self._setting.update(setting)

    def __call__(self, *args, **kwargs):
        return self._setting

    def __getattr__(self, name):
        return self._setting[name]
