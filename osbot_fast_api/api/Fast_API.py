import traceback
import types

from fastapi                                                                import FastAPI, Request, HTTPException
from fastapi.exceptions                                                     import RequestValidationError
from starlette.middleware.wsgi                                              import WSGIMiddleware       # todo replace this with a2wsgi
from osbot_fast_api.api.Fast_API__Http_Events                               import Fast_API__Http_Events
from osbot_fast_api.api.middlewares.Middleware__Http_Request                import Middleware__Http_Request
from osbot_fast_api.api.middlewares.Middleware__Http_Request__Trace_Calls   import Middleware__Http_Request__Trace_Calls
from osbot_fast_api.utils.Version                                           import Version
from osbot_utils.base_classes.Type_Safe                                     import Type_Safe
from starlette.middleware.cors                                              import CORSMiddleware
from starlette.responses                                                    import RedirectResponse, JSONResponse
from starlette.staticfiles                                                  import StaticFiles
from osbot_utils.utils.Lists                                                import list_index_by
from osbot_utils.utils.Misc                                                 import list_set
from osbot_utils.decorators.lists.index_by                                  import index_by
from osbot_utils.decorators.methods.cache_on_self                           import cache_on_self
from starlette.testclient                                                   import TestClient
from osbot_fast_api.api.routes.Routes_Config                                import Routes_Config
from osbot_fast_api.utils.http_shell.Http_Shell__Server                     import Model__Shell_Command, Http_Shell__Server
from osbot_fast_api.utils.Fast_API_Utils                                    import Fast_API_Utils

DEFAULT_ROUTES_PATHS    = ['/', '/config/status', '/config/version']
DEFAULT__NAME__FAST_API = 'Fast_API'

class Fast_API(Type_Safe):
    base_path      : str  = '/'
    enable_cors    : bool = False
    default_routes : bool = True
    name           : str  = None
    http_events    : Fast_API__Http_Events

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name                      = self.__class__.__name__
        self.http_events.fast_api_name = self.name

    def add_global_exception_handlers(self):      # todo: move to Fast_API
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
        self.app().mount(path, WSGIMiddleware(flask_app))
        return self

    def add_shell_server(self):
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
        return FastAPI(**kwargs)

    def app_router(self):
        return self.app().router

    def client(self):
        return TestClient(self.app())

    def fast_api_utils(self):
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
        return list_set(self.routes(index_by='method_name'))


    def routes_paths(self, include_default=False, expand_mounts=False):
        routes_paths = self.routes(include_default=include_default, expand_mounts=expand_mounts)
        return list_set(list_index_by(routes_paths, 'http_path'))
        # paths = list_set(self.routes(index_by='http_path'))
        # if include_default:
        #     return paths
        # return list_minus_list(list_a=paths, list_b=DEFAULT_ROUTES_PATHS)

    def setup_middlewares(self):                 # overwrite to add more middlewares
        self.setup_middleware__http_events()
        if self.enable_cors:
            self.setup_middleware__cors()
        return self

    def setup_routes     (self): return self     # overwrite to add rules


    def setup_default_routes(self):
        if self.default_routes:
            self.setup_add_root_route()
            self.add_routes(Routes_Config)

    def setup_add_root_route(self):
        def redirect_to_docs():
            return RedirectResponse(url="/docs")
        self.app_router().get("/")(redirect_to_docs)


    def setup_static_routes(self):
        path_static_folder = self.path_static_folder()
        if path_static_folder:
            path_static        = "/static"
            path_name          = "static"
            self.app().mount(path_static, StaticFiles(directory=path_static_folder), name=path_name)

    def setup_middleware__cors(self):               # todo: double check that this is working see bug test
        self.app().add_middleware(CORSMiddleware,
                                  allow_origins     = ["*"]                         ,
                                  allow_credentials = True                          ,
                                  allow_methods     = ["GET", "POST", "HEAD"]       ,
                                  allow_headers     = ["Content-Type", "X-Requested-With", "Origin", "Accept", "Authorization"],
                                  expose_headers    = ["Content-Type", "X-Requested-With", "Origin", "Accept", "Authorization"])

    def setup_middleware__http_events(self, ):
        # note the invocation order is the reverse of the order they are added
        self.app().add_middleware(Middleware__Http_Request__Trace_Calls, http_events=self.http_events)
        self.app().add_middleware(Middleware__Http_Request             , http_events=self.http_events)
        return self

    def user_middlewares(self):
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
        return Version().value()

    # def run_in_lambda(self):
    #     lambda_host = '127.0.0.1'
    #     lambda_port = 8080
    #     kwargs = dict(app  =  self.app(),
    #                   host = lambda_host,
    #                   port = lambda_port)
    #     uvicorn.run(**kwargs)