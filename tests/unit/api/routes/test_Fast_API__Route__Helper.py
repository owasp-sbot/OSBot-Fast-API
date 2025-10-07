from unittest                                                                      import TestCase
from fastapi                                                                       import FastAPI, APIRouter
from osbot_utils.utils.Dev import pprint

from osbot_utils.utils.Objects import obj

from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                                import Safe_Str
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                  import Safe_Id
from osbot_fast_api.api.routes.Fast_API__Route__Helper                             import Fast_API__Route__Helper
from osbot_fast_api.api.routes.Type_Safe__Route__Registration                      import Type_Safe__Route__Registration


class test_Fast_API__Route__Helper(TestCase):

    def setUp(self):                                                                # Per-test setup for app
        self.fastapi_kwargs = dict(docs_url    = None,       # disables Swagger UI (/docs)
                                   redoc_url   = None,       # disables ReDoc (/redoc)
                                   openapi_url = None)       # disables OpenAPI schema (/openapi.json)

        self.app    = FastAPI(**self.fastapi_kwargs)
        self.helper = Fast_API__Route__Helper()

    def test__init__(self):                                                         # Test helper initialization
        with Fast_API__Route__Helper() as _:
            assert type(_)                    is Fast_API__Route__Helper
            assert type(_.route_registration) is Type_Safe__Route__Registration

    def test_add_route__with_get_method(self):                                      # Test adding route with GET method
        def test_endpoint():
            return {"status": "ok"}

        self.helper.add_route(self.app, test_endpoint, methods=['GET'])

        routes = self.app.routes
        assert type(routes) is list

        assert len(routes)        == 1
        assert routes[0].path     == '/test-endpoint'
        assert routes[0].methods  == {'GET'}

    def test_add_route__with_post_method(self):                                     # Test adding route with POST method
        def create_item():
            return {"created": True}

        self.helper.add_route(self.app, create_item, methods=['POST'])

        routes = self.app.routes
        assert len(routes)        == 1
        assert routes[0].path     == '/create-item'
        assert routes[0].methods  == {'POST'}

    def test_add_route__with_multiple_methods(self):                                # Test adding route with multiple HTTP methods
        def handle_resource():
            return {"handled": True}

        self.helper.add_route(self.app, handle_resource, methods=['GET', 'POST', 'PUT'])

        routes = self.app.routes
        assert len(routes)        == 1
        assert routes[0].methods  == {'GET', 'POST', 'PUT'}

    def test_add_route_get(self):                                                   # Test convenience method for GET routes
        def get_data():
            return {"data": [1, 2, 3]}

        self.helper.add_route_get(self.app, get_data)

        routes = self.app.routes
        assert len(routes)        == 1
        assert routes[0].path     == '/get-data'
        assert routes[0].methods  == {'GET'}

    def test_add_route_post(self):                                                  # Test convenience method for POST routes
        def create_user():
            return {"created": True}

        self.helper.add_route_post(self.app, create_user)

        routes = self.app.routes
        assert len(routes)        == 1
        assert routes[0].path     == '/create-user'
        assert routes[0].methods  == {'POST'}

    def test_add_route_put(self):                                                   # Test convenience method for PUT routes
        def update_item():
            return {"updated": True}

        self.helper.add_route_put(self.app, update_item)

        routes = self.app.routes
        assert len(routes)        == 1
        assert routes[0].path     == '/update-item'
        assert routes[0].methods  == {'PUT'}

    def test_add_route_delete(self):                                                # Test convenience method for DELETE routes
        def delete_item():
            return {"deleted": True}

        self.helper.add_route_delete(self.app, delete_item)

        routes = self.app.routes
        assert len(routes)        == 1
        assert routes[0].path     == '/delete-item'
        assert routes[0].methods  == {'DELETE'}

    def test_add_route_any__default_path(self):                                     # Test ANY method with default path parsing
        def catch_all():
            return {"method": "any"}

        self.helper.add_route_any(self.app, catch_all)

        routes = self.app.routes
        assert len(routes)    == 1
        assert routes[0].path == '/catch-all'
        assert routes[0].methods == {'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT'}

    def test_add_route_any__explicit_path(self):                                    # Test ANY method with explicit path
        def proxy(path: str):
            return {"proxied": path}

        self.helper.add_route_any(self.app, proxy, path="/{path:path}")

        routes = self.app.routes
        assert len(routes)    == 1
        assert routes[0].path == '/{path:path}'
        assert routes[0].methods == {'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT'}

    def test_add_route__with_type_safe_params(self):                                # Test route with Type_Safe parameters
        class User_Data(Type_Safe):
            name  : Safe_Str
            email : Safe_Str

        def create_user(user_data: User_Data):
            return {"created": True}

        self.helper.add_route(self.app, create_user, methods=['POST'])

        routes = self.app.routes
        assert len(routes)        == 1
        assert routes[0].path     == '/create-user'
        assert routes[0].methods  == {'POST'}

    def test_add_route__with_path_params(self):                                     # Test route with path parameters
        def get__user_id(user_id: Safe_Id):
            return {"user_id": str(user_id)}

        self.helper.add_route_get(self.app, get__user_id)

        routes = self.app.routes
        assert len(routes)    == 1
        assert routes[0].path == '/get/{user_id}'

    def test_add_multiple_routes(self):                                             # Test adding multiple routes to same app
        def endpoint_1():
            pass

        def endpoint_2():
            pass

        def endpoint_3():
            pass

        self.helper.add_route_get(self.app, endpoint_1)
        self.helper.add_route_post(self.app, endpoint_2)
        self.helper.add_route_put(self.app, endpoint_3)

        routes = self.app.routes
        assert len(routes)        == 3
        assert routes[0].path     == '/endpoint-1'
        assert routes[1].path     == '/endpoint-2'
        assert routes[2].path     == '/endpoint-3'
        assert routes[0].methods  == {'GET'}
        assert routes[1].methods  == {'POST'}
        assert routes[2].methods  == {'PUT'}

    def test_add_route__integration_with_analyzer_and_converter(self):              # Test full integration with Type_Safe system
        class Order_Data(Type_Safe):
            items    : list
            quantity : Safe_Id

        def create__order_id(order_id: Safe_Id, data: Order_Data):
            return {"order_id": str(order_id), "created": True}

        self.helper.add_route_post(self.app, create__order_id)

        routes = self.app.routes
        assert len(routes)    == 1
        assert routes[0].path == '/create/{order_id}'

    def test_add_route_any__no_explicit_path(self):                                 # Test ANY without explicit path uses parser
        def handle_request():
            return {"handled": True}

        self.helper.add_route_any(self.app, handle_request, path=None)

        routes = self.app.routes
        assert len(routes)    == 1
        assert routes[0].path == '/handle-request'