# -*- coding: utf-8 -*-
from enum import (
    Enum,
    auto,
)

from component.template_loader import TemplateLoader


class NodeType(Enum):

    html_node = auto()
    if_node = auto()
    for_node = auto()
    end_node = auto()
    else_node = auto()
    value_node = auto()


class TemplateNode:
    """
    模版的节点类

    目前支持的节点：
    1. 纯html节点
    2. if 判断开始节点： 语法为 {{ if xxx }}，if和xxx中间只可以有一个空格，其中xxx一定要为environment中存在的key
    3. else 判断else节点：语法为 {{ else }}
    4. for 循环开始节点：语法为 {{ for yyy in xxx }}，for和xxx中间只可以有一个空格, 其中xxx一定要为environment中存在的key
    5. end 结束判断和循环的节点：语法为 {{ end }}
    6. value 变量取值节点：语法为 {{ xxx }} 或 {{ xxx.yyy }}等，可以从字典或者是对象中取值，
       xxx一定要为environment中存在的key或者是循环开始节点中增加定义的yyy

    处理流程：
    1. 先确定节点类型
    2. 根据节点类型进行预处理
    3. 传入数据的时候根据数据渲染不同的节点
    4. 返回html
    """

    def __init__(self, content, html_only=True, father_node=None):
        self.content = content
        self.html_only = html_only
        self.node_type = None

        # if_node和for_node还会子节点或者父节点
        self.child_nodes = []
        self.father_node = father_node

        # 生成html时需要的环境内容
        self.environment = None
        self.done = False

        self.type_for_node()
        self.analyse()

    def _analyse_html_node(self):
        self.done = True

    def _analyse_if_node(self):
        temp_content = self.content.strip()
        self.content = temp_content[3:]

    def _analyse_for_node(self):
        temp_content = self.content.strip()
        t = temp_content[4:]
        self.content = t.split()

    def _analyse_end_node(self):
        self.content = ''
        self.father_node.done = True
        self.done = True

    def _analyse_else_node(self):
        self.content = ''
        self.done = True

    def _analyse_value_node(self):
        value_name = self.content.strip()
        value = value_name.split('.')
        self.content = value
        self.done = True

    def analyse(self):
        """
        根据自身不同的节点类型，使用不同的方法进行分析和处理
        """
        type_analyse_methods = {
            NodeType.html_node: self._analyse_html_node,
            NodeType.if_node: self._analyse_if_node,
            NodeType.for_node: self._analyse_for_node,
            NodeType.end_node: self._analyse_end_node,
            NodeType.else_node: self._analyse_else_node,
            NodeType.value_node: self._analyse_value_node,
        }
        m = type_analyse_methods[self.node_type]
        m()

    def type_for_node(self):
        """
        分析确实自身节点类型
        """
        if self.html_only is True:
            self.node_type = NodeType.html_node
        else:
            temp_content = self.content.strip()
            if temp_content[:3] == 'if ':
                self.node_type = NodeType.if_node
            elif temp_content[:4] == 'for ':
                self.node_type = NodeType.for_node
            elif temp_content == 'else':
                self.node_type = NodeType.else_node
            elif temp_content == 'end':
                self.node_type = NodeType.end_node
            else:
                self.node_type = NodeType.value_node

    @classmethod
    def new(cls, content, html_only, father_node):
        return cls(content, html_only, father_node)

    def _add_content(self, content, html_only):
        if self.node_type == NodeType.if_node or self.node_type == NodeType.for_node:
            new_node = self.new(content, html_only, self)
            self.child_nodes.append(new_node)
            if new_node.done is False:
                return_node = new_node
            else:
                return_node = self
            return return_node
        else:
            raise TypeError('当前node类型不正确')

    def add_content(self, content, html_only):
        target_dict = {
            True: self.father_node,
            False: self,
        }
        r = target_dict[self.done]._add_content(content, html_only)
        return r

    def renew_environment(self, environment):
        if environment is not None:
            self.environment.update(environment)

    def html_from_html_node(self):
        return self.content

    def html_from_if_node(self):
        statement = bool(self.environment[self.content])
        r = ''
        current_part = True
        changed = False
        for n in self.child_nodes:
            if n.node_type == NodeType.else_node and changed is False:
                current_part = False
                changed = True
            elif n.node_type == NodeType.else_node and changed is True:
                raise SyntaxError('模板if语句有多个else！')
            if statement == current_part:
                r += n.html_from_self(self.environment)
        return r

    def html_from_for_node(self):
        iter_item = self.environment[self.content[-1]]
        r = ''
        key_name = self.content[0]
        for i in iter_item:
            new_environment = self.environment.copy()
            new_environment.update({key_name: i})
            for n in self.child_nodes:
                r += n.html_from_self(new_environment)
        return r

    def html_from_end_node(self):
        return self.content

    def html_from_else_node(self):
        return self.content

    def html_from_value_node(self):
        t = self.environment
        for c in self.content:
            if isinstance(t, dict):
                t = t[c]
            else:
                t = getattr(t, c)
        return str(t)

    def html_from_self(self, environment):
        """
        根据自身不同的类型，使用对应方法，输出html
        """
        type_html_methods = {
            NodeType.html_node: self.html_from_html_node,
            NodeType.if_node: self.html_from_if_node,
            NodeType.for_node: self.html_from_for_node,
            NodeType.end_node: self.html_from_end_node,
            NodeType.else_node: self.html_from_else_node,
            NodeType.value_node: self.html_from_value_node,
        }
        m = type_html_methods[self.node_type]
        self.environment = environment
        return m()


class TemplateNodeManage:
    """
    节点管理器，存放主节点
    """

    def __init__(self):
        self.node_list = []
        self.current_node = None

    def add_content(self, content, html_only):
        if len(self.node_list) > 0 and self.node_list[-1].done is False:
            r = self.current_node.add_content(content, html_only)
            self.current_node = r
            return r
        else:
            t = TemplateNode(content, html_only)
            self.node_list.append(t)
            self.current_node = t
            return t

    def html_from_node(self, environment):
        html = ''.join([h.html_from_self(environment) for h in self.node_list])
        return html


class Render:

    def __init__(self, setting):
        self.template_loader = TemplateLoader(setting.template_path)

    @staticmethod
    def renew_search_state(new_item='}'):
        """
        获取搜索模板语法的标签和状态
        """
        html = False
        if new_item == '{':
            return '}', html
        elif new_item == '}':
            html = True
            return '{', html

    def content_to_node_manage(self, content):
        """
        将文本内容转化为分析好的node管理器
        """
        manage = TemplateNodeManage()
        last_index = 0
        index = 0
        # html用来确定当前搜索内容是否为html only
        search_item, html = self.renew_search_state()
        while index < len(content):
            if content[index] == search_item and content[index+1] == search_item:
                manage.add_content(content[last_index:index], html)
                search_item, html = self.renew_search_state(search_item)
                # 跳过搜索的标识符号
                index += 1
                last_index = index + 1
            index += 1
        # 把剩下部分也加入到数列当中
        manage.add_content(content[last_index:index+1], html)
        return manage

    def render(self, template, environment):
        """
        渲染出 html
        :param template: 模板名
        :param environment: 环境dict
        """
        content = self.template_loader.get_source(template)
        template_manage = self.content_to_node_manage(content)
        html = template_manage.html_from_node(environment)
        return html
