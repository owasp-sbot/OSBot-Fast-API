import inspect
from typing                                 import get_type_hints
from fastapi                                import APIRouter, FastAPI
from osbot_utils.type_safe.Type_Safe        import Type_Safe
from osbot_utils.decorators.lists.index_by  import index_by

class Fast_API_Routes(Type_Safe):       # refactor to Fast_API__Routes
    router : APIRouter
    app    : FastAPI = None
    prefix : str
    tag    : str

    def __init__(self, **kwargs):
        from osbot_utils.utils.Str import str_safe
        from osbot_utils.utils.Misc import lower

        super().__init__(**kwargs)
        self.prefix = f'/{lower(str_safe(self.tag))}'

    def add_route(self,function, methods):
        path = self.parse_function_name(function.__name__)
        self.router.add_api_route(path=path, endpoint=function, methods=methods)
        return self

    def add_route_delete(self, function):
        return self.add_route(function=function, methods=['DELETE'])

    def add_route_get(self, function):
        return self.add_route(function=function, methods=['GET'])

    def add_route_post(self, function):                         # add post with support for Type_Safe objects
        sig        = inspect.signature(function)                # Check if function has a Type_Safe parameter
        type_hints = get_type_hints(function)

        type_safe_param = False
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            param_type = type_hints.get(param_name)
            if param_type and inspect.isclass(param_type):
                if issubclass(param_type, Type_Safe):
                    type_safe_param = True
                    break

        if type_safe_param:
            def wrapper(data: dict):
                param_object = param_type.from_json(data)
                kwargs       = { param_name: param_object }
                result       = function(**kwargs)
                if isinstance(result, Type_Safe):
                    return result.json()
                return result


            # todo: the code below is not working (need to add support for supporting Type_Safe return values)
            # Remove the return type annotation to prevent FastAPI validation
            # wrapper.__annotations__ = function.__annotations__.copy()
            # if 'return' in wrapper.__annotations__:
            #     del wrapper.__annotations__['return']  # Remove return type so FastAPI doesn't validate


            #path = '/' + function.__name__.replace('_', '-')
            path = self.parse_function_name(function.__name__)
            self.router.add_api_route(path=path, endpoint=wrapper, methods=['POST'])
            return self
        else:
            # Normal route
            return self.add_route(function=function, methods=['POST'])

    def add_route_put(self, function):
        return self.add_route(function=function, methods=['PUT'])

    def fast_api_utils(self):
        from osbot_fast_api.utils.Fast_API_Utils import Fast_API_Utils
        return Fast_API_Utils(self.app)

    def parse_function_name(self, function_name):                           # added support for routes that have resource ids in the path
        parts = function_name.split('__')
        path_segments = []

        for i, part in enumerate(parts):
            if i == 0:                                                  # First part is always literal
                path_segments.append(part.replace('_', '-'))
            else:
                if '_' in part:                                         # After __, check if it's a parameter or literal
                    subparts = part.split('_', 1)                       # Contains underscore, split into param and literal
                    path_segments.append('{' + subparts[0] + '}')
                    path_segments.append(subparts[1].replace('_', '-'))
                else:
                    path_segments.append('{' + part + '}')              # Just a parameter

        return '/' + '/'.join(path_segments)

    @index_by
    def routes(self):
        return self.fast_api_utils().fastapi_routes(router=self.router)

    def routes_methods(self):
        return list(self.routes(index_by='method_name'))

    def routes_paths(self):
        return list(self.routes(index_by='http_path'))

    def setup(self):
        self.setup_routes()
        self.app.include_router(self.router, prefix=self.prefix, tags=[self.tag])
        return self

    def setup_routes(self):     # overwrite this to add routes to self.router
        pass



    # def routes_list(self):
    #     items = []
    #     for route in self.routes():
    #         for http_methods in route.get('http_methods'):
    #             item = f'{http_methods:4} | {route.get("method_name"):14} | {route.get("http_path")}'
    #             items.append(item)
    #     return items