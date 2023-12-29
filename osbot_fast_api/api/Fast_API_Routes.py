from fastapi import APIRouter
from osbot_utils.decorators.lists.index_by import index_by

from osbot_utils.utils.Misc import lower

from osbot_utils.utils.Str import str_safe

from osbot_fast_api.utils.Fast_API_Utils import Fast_API_Utils

#DEFAULT_ROUTES = ['/docs', '/docs/oauth2-redirect', '/openapi.json', '/redoc']

class Fast_API_Routes:

    def __init__(self, app, tag):
        self.router = APIRouter()
        self.app    = app
        self.prefix = f'/{lower(str_safe(tag))}'
        self.tag    = tag
        self.setup()

    def add_route(self, path, function, methods):
        self.router.add_api_route(path=path, endpoint=function, methods=methods)
        return self

    def add_route_get(self, path, function):
        return self.add_route(path=path, function=function, methods=['GET'])

    def add_route_post(self, path, function):
        return self.add_route(path=path, function=function, methods=['POST'])

    def fast_api_utils(self):
        return Fast_API_Utils(self.app)

    @index_by
    def routes(self):
        return self.fast_api_utils().fastapi_routes(router=self.router)

    # @index_by
    # def routes(self, include_prefix=False):
    #     if include_prefix is False:
    #         return fastapi_routes(self.router)
    #     routes = []
    #     for route in fastapi_routes(self.router):
    #         route['http_path'] = f'{self.prefix}{route["http_path"]}'
    #         routes.append(route)
    #     return routes

    # def routes_paths(self):
    #     return list(self.routes(index_by='http_path'))

    def setup(self):
        self.setup_routes()
        self.app.include_router(self.router, prefix=self.prefix, tags=[self.tag])

    def setup_routes(self):     # overwrite this to add routes to self.router
        pass



    # def routes_list(self):
    #     items = []
    #     for route in self.routes():
    #         for http_methods in route.get('http_methods'):
    #             item = f'{http_methods:4} | {route.get("method_name"):14} | {route.get("http_path")}'
    #             items.append(item)
    #     return items