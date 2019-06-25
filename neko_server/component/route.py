# -*- coding: utf-8 -*-
import copy


class Router:

    def __init__(self):
        self._routes = {}

    def set_route(self, routes):
        self._routes = copy.deepcopy(routes)

    def update_route(self, routes):
        d = copy.deepcopy(routes)
        self._routes.update(d)

    def get(self, path, default):
        r = self._routes.get(path, default)
        return r


route = Router()
