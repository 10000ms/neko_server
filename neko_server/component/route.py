# -*- coding: utf-8 -*-
from views.static import static_handler
from views.index import index_handler


class Router:

    def __init__(self):
        self._routes = {}
        self.update_route(static_handler)
        self.update_route(index_handler)

    def set_route(self, routes):
        self._routes = routes.copy()

    def update_route(self, routes):
        d = routes.copy()
        self._routes.update(d)

    def get(self, path, default):
        for rule, handler in self._routes.items():
            rule_len = len(rule)
            if len(path) >= rule_len and path[:rule_len] == rule:
                return handler
        return default


route = Router()
