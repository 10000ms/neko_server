from collections import OrderedDict

from ..views.static import static_handler
from ..views.index import index_handler


def default_rule_comparator(rule, path):
    """
    默认路由规则比较方法，需要值等
    """
    return rule == path


def all_rule_comparator(rule, path):
    """
    all路由规则比较方法，直接返回true
    """
    return True


class Router:

    # 路由规则对应的比较器
    rule_comparators = {
        '*': all_rule_comparator
    }

    # 默认的比较器
    default_rule_comparator = default_rule_comparator

    def __init__(self):
        self._routes = OrderedDict()
        # 框架默认的静态文件路由和index路由
        self.update_route(static_handler)
        self.update_route(index_handler)

    def set_route(self, routes):
        self._routes = routes.copy()

    def update_route(self, routes):
        d = routes.copy()
        self._routes.update(d)

    @staticmethod
    def split_route(route, max_split=-1):
        r = route.split('/', max_split)
        if '?' in r[-1]:
            r[-1] = r[-1].split('?', 1)[0]
        return r

    def get(self, path, default):
        """
        使用 / 分割路由规则，
        然后再根据分割出来的数组长度分割实际的请求地址
        再使用比较器与之比较，完全符合就是目标路由
        """
        for rule, handler in self._routes.items():
            temp_rule = self.split_route(rule)
            temp_rule_len = len(temp_rule)
            temp_path = self.split_route(path, temp_rule_len-1)
            target = True
            n = 0
            while n < temp_rule_len:
                comparator = self.rule_comparators.get(temp_rule[n], default_rule_comparator)
                r = comparator(temp_rule[n], temp_path[n])
                if r is not True:
                    target = False
                    break
                n += 1
            if target is True:
                return handler
        return default
