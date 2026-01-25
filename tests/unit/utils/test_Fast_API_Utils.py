import tempfile
from unittest                                           import TestCase
from fastapi                                            import FastAPI
from fastapi.routing                                    import APIRouter, APIWebSocketRoute
from starlette.routing                                  import Mount
from starlette.staticfiles                              import StaticFiles
from osbot_fast_api.api.Fast_API                        import Fast_API
from osbot_fast_api.api.schemas.consts.consts__Fast_API import ROUTES__CONFIG, ROUTE_REDIRECT_TO_DOCS
from osbot_fast_api.utils.Fast_API_Utils                import Fast_API_Utils


class test_Fast_API_Utils(TestCase):

    def setUp(self):
        self.fast_api       = Fast_API().setup()
        self.fast_api_utils = self.fast_api.fast_api_utils()

    def test_fastapi_routes(self):
        routes  = self.fast_api_utils.fastapi_routes(include_default=False)
        assert routes == [ROUTE_REDIRECT_TO_DOCS] + ROUTES__CONFIG

    def test_fastapi_routes__include_default(self):
        routes          = self.fast_api_utils.fastapi_routes(include_default=True )                     # include default routes
        routes_filtered = self.fast_api_utils.fastapi_routes(include_default=False)                     # exclude default routes
        assert len(routes) > len(routes_filtered)                                                       # default routes exist

    def test_fastapi_routes__with_static_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:                                                 # create temp dir for static files
            app = FastAPI()
            app.mount('/static', StaticFiles(directory=temp_dir), name='static')                        # mount static files
            fast_api_utils = Fast_API_Utils(app)
            routes         = fast_api_utils.fastapi_routes(include_default=True)
            static_route   = next((r for r in routes if r['http_path'] == '/static'), None)
            assert static_route is not None                                                             # static mount found
            assert static_route['http_methods'] == ['GET', 'HEAD']                                      # static files support GET and HEAD

    def test_fastapi_routes__with_websocket(self):
        app = FastAPI()

        @app.websocket('/ws')
        async def websocket_endpoint(websocket):                                                        # websocket route
            pass

        fast_api_utils = Fast_API_Utils(app)
        routes         = fast_api_utils.fastapi_routes(include_default=True)
        ws_route       = next((r for r in routes if r['http_path'] == '/ws'), None)
        assert ws_route is not None                                                                     # websocket route found
        assert ws_route['http_methods'] == []                                                           # websocket has no HTTP methods

    def test_fastapi_routes__with_expand_mounts(self):
        app        = FastAPI()
        sub_router = APIRouter()

        @sub_router.get('/items')
        def get_items():                                                                                # sub-route
            return []

        sub_app = FastAPI()
        sub_app.include_router(sub_router)
        app.mount('/api/v1', sub_app)                                                                   # mount sub-app

        fast_api_utils    = Fast_API_Utils(app)
        routes_collapsed  = fast_api_utils.fastapi_routes(expand_mounts=False, include_default=True)
        routes_expanded   = fast_api_utils.fastapi_routes(expand_mounts=True , include_default=True)

        mount_in_collapsed = any(r['http_path'] == '/api/v1' for r in routes_collapsed)
        items_in_expanded  = any(r['http_path'] == '/api/v1/items' for r in routes_expanded)

        assert mount_in_collapsed is False                                                              # mount skipped when not expanding
        assert items_in_expanded  is True                                                               # sub-route visible when expanded