from fastapi import APIRouter
from osbot_utils.decorators.lists.index_by import index_by

from osbot_utils.utils.Misc import lower

from osbot_utils.utils.Str import str_safe

DEFAULT_ROUTES = ['/docs', '/docs/oauth2-redirect', '/openapi.json', '/redoc']

class FastAPI_Router:

    def __init__(self, app, name):
        self.router = APIRouter()
        self.app    = app
        self.prefix = f'/{lower(str_safe(name))}'
        self.tag    = name
        self.setup()

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

    def setup_routes(self):     # overwrite this to add routes to self.router
        pass

    def setup(self):
        self.setup_routes()
        self.app.include_router(self.router, prefix=self.prefix, tags=[self.tag])

    # def routes_list(self):
    #     items = []
    #     for route in self.routes():
    #         for http_methods in route.get('http_methods'):
    #             item = f'{http_methods:4} | {route.get("method_name"):14} | {route.get("http_path")}'
    #             items.append(item)
    #     return items