# -*- coding: utf-8 -*-
from views.static import static_handler
from views.index import index_handler


class Router:

    def __init__(self):
        self._routes = {}
        self.update_route(static_handler)
        self.update_route(index_handler)

    def set_route(self, routes):
        rs = routes.copy()
        self._routes = self.analyse_route_dict(rs)

    @staticmethod
    def analyse_route(route_string):
        # TODO: 更好的分析模式
        return route_string.split('/')[1]

    def analyse_route_dict(self, routes):
        d = {}
        for k, v in routes.items():
            key = self.analyse_route(k)
            d[key] = v
        return d

    def update_route(self, routes):
        rs = routes.copy()
        self._routes.update(self.analyse_route_dict(rs))

    def get(self, path, default):
        p = self.analyse_route(path)
        r = self._routes.get(p, default)
        return r


route = Router()
