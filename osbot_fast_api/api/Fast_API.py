from osbot_utils.type_safe.primitives.safe_str.identifiers.Random_Guid import Random_Guid
from osbot_fast_api.api.Fast_API__Http_Events                          import Fast_API__Http_Events
from osbot_utils.type_safe.Type_Safe                                   import Type_Safe
from osbot_utils.decorators.lists.index_by                             import index_by
from osbot_utils.decorators.methods.cache_on_self                      import cache_on_self


DEFAULT_ROUTES_PATHS                    = ['/', '/config/status', '/config/version']
DEFAULT__NAME__FAST_API                 = 'Fast_API'
ENV_VAR__FAST_API__AUTH__API_KEY__NAME  = 'FAST_API__AUTH__API_KEY__NAME'
ENV_VAR__FAST_API__AUTH__API_KEY__VALUE = 'FAST_API__AUTH__API_KEY__VALUE'

class Fast_API(Type_Safe):
    base_path      : str  = '/'
    enable_cors    : bool = False
    enable_api_key : bool = False
    default_routes : bool = True
    name           : str  = None
    http_events    : Fast_API__Http_Events
    server_id      : Random_Guid

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name                      = self.__class__.__name__
        self.http_events.fast_api_name = self.name

    def add_global_exception_handlers(self):      # todo: move to Fast_API
        import traceback
        from fastapi                import Request, HTTPException
        from fastapi.exceptions     import RequestValidationError
        from starlette.responses    import JSONResponse

        app = self.app()
        @app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            stack_trace = traceback.format_exc()
            content = { "detail"      : "An unexpected error occurred." ,
                        "error"       : str(exc)                        ,
                        "stack_trace" : stack_trace                     }
            return JSONResponse( status_code=500, content=content)

        @app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return JSONResponse( status_code=exc.status_code, content={"detail": exc.detail})

        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            return JSONResponse( status_code=400, content={"detail": exc.errors()} )


    def add_flask_app(self, path, flask_app):
        from starlette.middleware.wsgi import WSGIMiddleware  # todo replace this with a2wsgi

        self.app().mount(path, WSGIMiddleware(flask_app))
        return self

    def add_shell_server(self):
        from osbot_fast_api.utils.http_shell.Http_Shell__Server import Model__Shell_Command, Http_Shell__Server
        def shell_server(shell_command: Model__Shell_Command):
            return Http_Shell__Server().invoke(shell_command)
        self.add_route_post(shell_server)

    def add_route(self,function, methods):
        path = '/' + function.__name__.replace('_', '-')
        self.app().add_api_route(path=path, endpoint=function, methods=methods)
        return self

    def add_route_get(self, function):
        return self.add_route(function=function, methods=['GET'])

    def add_route_post(self, function):
        return self.add_route(function=function, methods=['POST'])

    def add_routes(self, class_routes):
        class_routes(app=self.app()).setup()
        return self

    @cache_on_self
    def app(self, **kwargs):
        from fastapi import FastAPI
        return FastAPI(**kwargs)

    def app_router(self):
        return self.app().router

    def client(self):
        from starlette.testclient import TestClient             # moved here for performance reasons
        return TestClient(self.app())

    def fast_api_utils(self):
        from osbot_fast_api.utils.Fast_API_Utils import Fast_API_Utils

        return Fast_API_Utils(self.app())

    def path_static_folder(self):        # override this to add support for serving static files from this directory
        return None

    def mount(self, parent_app):
        parent_app.mount(self.base_path, self.app())

    def setup(self):
        self.add_global_exception_handlers()
        self.setup_middlewares            ()        # overwrite to add middlewares
        self.setup_default_routes         ()
        self.setup_static_routes          ()
        self.setup_routes                 ()        # overwrite to add routes
        return self

    @index_by
    def routes(self, include_default=False, expand_mounts=False):
        return self.fast_api_utils().fastapi_routes(include_default=include_default, expand_mounts=expand_mounts)

    def route_remove(self, path):
        for route in self.app().routes:
            if getattr(route, 'path', '') == path:
                self.app().routes.remove(route)
                print(f'removed route: {path} : {route}')
                return True
        return False

    def routes_methods(self):
        from osbot_utils.utils.Misc import list_set

        return list_set(self.routes(index_by='method_name'))


    def routes_paths(self, include_default=False, expand_mounts=False):
        from osbot_utils.utils.Lists import list_index_by
        from osbot_utils.utils.Misc  import list_set

        routes_paths = self.routes(include_default=include_default, expand_mounts=expand_mounts)
        return list_set(list_index_by(routes_paths, 'http_path'))

    def routes_paths_all(self):
        return self.routes_paths(include_default=True, expand_mounts=True)

    def setup_middlewares(self):                 # overwrite to add more middlewares
        self.setup_middleware__detect_disconnect()
        self.setup_middleware__http_events      ()
        self.setup_middleware__cors             ()
        self.setup_middleware__api_key_check    ()
        return self

    def setup_routes     (self): return self     # overwrite to add rules


    def setup_default_routes(self):
        from osbot_fast_api.api.routes.Routes_Config import Routes_Config

        if self.default_routes:
            self.setup_add_root_route()
            self.add_routes(Routes_Config)

    def setup_add_root_route(self):
        from starlette.responses import RedirectResponse

        def redirect_to_docs():
            return RedirectResponse(url="/docs")
        self.app_router().get("/")(redirect_to_docs)


    def setup_static_routes(self):
        from starlette.staticfiles import StaticFiles

        path_static_folder = self.path_static_folder()
        if path_static_folder:
            path_static        = "/static"
            path_name          = "static"
            self.app().mount(path_static, StaticFiles(directory=path_static_folder), name=path_name)

    def setup_middleware__api_key_check(self, env_var__api_key_name:str=ENV_VAR__FAST_API__AUTH__API_KEY__NAME, env_var__api_key_value:str=ENV_VAR__FAST_API__AUTH__API_KEY__VALUE):
        from osbot_fast_api.api.middlewares.Middleware__Check_API_Key import Middleware__Check_API_Key
        if self.enable_api_key:
            self.app().add_middleware(Middleware__Check_API_Key, env_var__api_key__name=env_var__api_key_name, env_var__api_key__value=env_var__api_key_value)
        return self

    def setup_middleware__cors(self):               # todo: double check that this is working see bug test
        from starlette.middleware.cors import CORSMiddleware

        if self.enable_cors:
            self.app().add_middleware(CORSMiddleware,
                                      allow_origins     = ["*"]                         ,
                                      allow_credentials = True                          ,
                                      allow_methods     = ["GET", "POST", "HEAD"]       ,
                                      allow_headers     = ["Content-Type", "X-Requested-With", "Origin", "Accept", "Authorization"],
                                      expose_headers    = ["Content-Type", "X-Requested-With", "Origin", "Accept", "Authorization"])

    def setup_middleware__detect_disconnect(self):
        from osbot_fast_api.api.middlewares.Middleware__Detect_Disconnect import Middleware__Detect_Disconnect

        self.app().add_middleware(Middleware__Detect_Disconnect)

    def setup_middleware__http_events(self):
        from osbot_fast_api.api.middlewares.Middleware__Http_Request import Middleware__Http_Request

        self.app().add_middleware(Middleware__Http_Request , http_events=self.http_events)
        return self


    def user_middlewares(self):
        import types

        middlewares = []
        data = self.app().user_middleware
        for item in data:
                type_name = item.cls.__name__
                options   = item.kwargs
                if isinstance(options.get('dispatch'),types.FunctionType):
                    function_name = options.get('dispatch').__name__
                    del options['dispatch']
                else:
                    function_name = None
                middleware = { 'type'         : type_name     ,
                               'function_name': function_name ,
                               'params'       : options       }
                middlewares.append(middleware)
        return middlewares

    def version__fast_api_server(self):
        from osbot_fast_api.utils.Version import Version
        return Version().value()

    # def run_in_lambda(self):
    #     lambda_host = '127.0.0.1'
    #     lambda_port = 8080
    #     kwargs = dict(app  =  self.app(),
    #                   host = lambda_host,
    #                   port = lambda_port)
    #     uvicorn.run(**kwargs)