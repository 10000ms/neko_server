# -*- coding: utf-8 -*-
from conf import setting
from component.template_loader import TemplateLoader


class Render:

    def __init__(self):
        self.template_loader = TemplateLoader(setting.template_path)

    def render(self, template, **kwargs):
        content = self.template_loader.get_source(template)
        for k, v in kwargs.items():
            target = '{}{}{}'.format('{{', k, '}}')
            content.replace(target, v)
        return content
