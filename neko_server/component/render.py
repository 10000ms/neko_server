# -*- coding: utf-8 -*-
from enum import (
    Enum,
    auto,
)

from conf import setting
from component.template_loader import TemplateLoader


class NodeType(Enum):

    html_content = auto()
    if_node = auto()
    for_node = auto()
    end_node = auto()
    value_node = auto()


class TemplateNode:

    def __init__(self, content, html_only=True):
        self.content = content
        self.html_only = html_only
        self.node_type = None
        self.node_mode_content = []
        self.done = False

        self.type_for_node()
        self.analyse()

    def analyse(self):
        if self.node_type == NodeType.html_content:
            self.node_mode_content = [(self.content, ), ]
            self.done = True
        elif self.node_type == NodeType.if_node:
            pass
        elif self.node_type == NodeType.for_node:
            pass
        elif self.node_type == NodeType.end_node:
            self.done = True
        elif self.node_type == NodeType.value_node:
            value_name = self.content.strip()
            value = value_name.split('.')
            value = tuple(value)
            self.node_mode_content = [value, ]
            self.done = True

    def type_for_node(self):
        if self.html_only is True:
            self.node_type = NodeType.html_content
        else:
            temp_content = self.content.lstrip()
            if temp_content[:2] == 'if':
                self.node_type = NodeType.if_node
            elif temp_content[:3] == 'for':
                self.node_type = NodeType.for_node
            elif temp_content[:3] == 'end':
                self.node_type = NodeType.for_node
            else:
                self.node_type = NodeType.value_node

    @classmethod
    def new(cls, content, html_only):
        return cls(content, html_only)

    def add_content(self, content):
        pass


class Render:

    def __init__(self):
        self.template_loader = TemplateLoader(setting.template_path)

    @staticmethod
    def renew_search_item(new_item='}'):
        if new_item == '{':
            return '}'
        elif new_item == '}':
            return '{'

    def split_content(self, content):
        r = []
        last_index = 0
        index = 0
        search_item = self.renew_search_item()
        while index < len(content):
            if content[index] == search_item and content[index+1] == search_item:
                r.append(content[last_index:index])
                last_index = index
                search_item = self.renew_search_item(search_item)
            index += 1
        # 把剩下部分也加入到数列当中
        r.append(content[last_index:index+1])
        return r

    def analyse(self, content):
        split_content = content.split()

    def render(self, template, **kwargs):
        content = self.template_loader.get_source(template)
        for k, v in kwargs.items():
            target = '{}{}{}'.format('{{', k, '}}')
            content.replace(target, v)
        return content
