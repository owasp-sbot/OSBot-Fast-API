import uvicorn
from fastapi                                        import FastAPI
from starlette.middleware.cors                      import CORSMiddleware
from starlette.responses                            import RedirectResponse
from starlette.staticfiles                          import StaticFiles
from osbot_utils.utils.Files                        import path_combine
from osbot_utils.utils.Misc                         import list_set
from osbot_utils.decorators.lists.index_by          import index_by
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from starlette.testclient import TestClient

from osbot_fast_api.api.routers.Router_Status import Router_Status
#from osbot_fast_api.Fast_API_Utils import fastapi_routes

from osbot_fast_api.utils.Fast_API_Utils import Fast_API_Utils


class Fast_API:

    def __init__(self, enable_cors=False):
        self.enable_cors = enable_cors          # todo: refactor to config class
        self.fast_api_setup()

    @cache_on_self
    def app(self):
        return FastAPI()

    def app_router(self):
        return self.app().router

    def client(self):
        return TestClient(self.app())

    def fast_api_utils(self):
        return Fast_API_Utils(self)

    def path_static_folder(self):        # override this to add support for serving static files from this directory
        return None

    def fast_api_setup(self):

        self.setup_middleware    ()        # todo: add support for only adding this when running in Localhost
        self.setup_default_routes()
        self.setup_static_routes ()
        self.setup_routes        ()
        return self

    @index_by
    def routes(self, include_default=False):
        return self.fast_api_utils().fastapi_routes(include_default=include_default)
        #return fastapi_routes(self.app(),include_default=include_default)

    def setup_default_routes(self):
        self.setup_add_root_route()

    def setup_add_root_route(self):
        def redirect_to_docs():
            return RedirectResponse(url="/docs")
        self.app_router().get("/")(redirect_to_docs)

    def setup_routes(self):
        Router_Status(self.app())
        return self

    def setup_static_routes(self):
        path_static_folder = self.path_static_folder()
        if path_static_folder:
            path_static        = "/static"
            path_name          = "static"
            self.app().mount(path_static, StaticFiles(directory=path_static_folder), name=path_name)

    def setup_middleware(self):
        if self.enable_cors:
            self.setup_middleware__cors()

    def setup_middleware__cors(self):               # todo: double check that this is working see bug test
        self.app().add_middleware(CORSMiddleware,
                                  allow_origins     = ["*"]                         ,
                                  allow_credentials = True                          ,
                                  allow_methods     = ["GET", "POST", "HEAD"]       ,
                                  allow_headers     = ["Content-Type", "X-Requested-With", "Origin", "Accept", "Authorization"],
                                  expose_headers    = ["Content-Type", "X-Requested-With", "Origin", "Accept", "Authorization"])


    def user_middleware(self):
        return self.app().user_middleware

    # def run_in_lambda(self):
    #     lambda_host = '127.0.0.1'
    #     lambda_port = 8080
    #     kwargs = dict(app  =  self.app(),
    #                   host = lambda_host,
    #                   port = lambda_port)
    #     uvicorn.run(**kwargs)