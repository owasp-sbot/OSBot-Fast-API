from unittest                                                       import TestCase
from fastapi                                                        import APIRouter
from osbot_fast_api.api.decorators.route_path                       import route_path
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                 import Safe_Str
from osbot_utils.type_safe.primitives.core.Safe_Int                 import Safe_Int
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id   import Safe_Id
from osbot_fast_api.api.routes.Type_Safe__Route__Registration       import Type_Safe__Route__Registration
from osbot_fast_api.api.routes.Type_Safe__Route__Analyzer           import Type_Safe__Route__Analyzer
from osbot_fast_api.api.routes.Type_Safe__Route__Converter          import Type_Safe__Route__Converter
from osbot_fast_api.api.routes.Type_Safe__Route__Wrapper            import Type_Safe__Route__Wrapper
from osbot_fast_api.api.routes.Fast_API__Route__Parser              import Fast_API__Route__Parser


class test_Type_Safe__Route__Registration(TestCase):

    def setUp(self):                                                                # Per-test setup for router
        self.router = APIRouter()

    @classmethod
    def setUpClass(cls):                                                            # Setup expensive resources once
        cls.registration = Type_Safe__Route__Registration()

    def test__init__(self):                                                         # Test registration system initialization
        with Type_Safe__Route__Registration() as _:
            assert type(_)                   is Type_Safe__Route__Registration
            assert type(_.analyzer)          is Type_Safe__Route__Analyzer
            assert type(_.converter)         is Type_Safe__Route__Converter
            assert type(_.wrapper_creator)   is Type_Safe__Route__Wrapper
            assert type(_.route_parser)      is Fast_API__Route__Parser
            assert _.wrapper_creator.converter is _.converter                       # Dependency wired correctly

    def test_register_route__simple_function(self):                                 # Test registering simple function
        def simple_endpoint():
            return {"status": "ok"}

        with self.registration as _:
            _.register_route(self.router, simple_endpoint, ['GET'])

            routes = self.router.routes
            assert len(routes)        == 1
            assert routes[0].path     == '/simple-endpoint'
            assert routes[0].methods  == {'GET'}

    def test_register_route__with_primitive_params(self):                           # Test registering function with Safe primitive params
        def get__user_id(user_id: Safe_Id):
            return {"user_id": str(user_id)}

        with self.registration as _:
            _.register_route(self.router, get__user_id, ['GET'])

            routes = self.router.routes
            assert len(routes)        == 1
            assert routes[0].path     == '/get/{user_id}'
            assert routes[0].methods  == {'GET'}

    def test_register_route__with_type_safe_params(self):                           # Test registering function with Type_Safe params
        class User_Data(Type_Safe):
            name  : Safe_Str
            email : Safe_Str

        def create_user(user_data: User_Data):
            return {"created": True}

        with self.registration as _:
            _.register_route(self.router, create_user, ['POST'])

            routes = self.router.routes
            assert len(routes)        == 1
            assert routes[0].path     == '/create-user'
            assert routes[0].methods  == {'POST'}

    def test_register_route__multiple_methods(self):                                # Test registering route with multiple HTTP methods
        def handle_resource():
            return {"handled": True}

        with self.registration as _:
            _.register_route(self.router, handle_resource, ['GET', 'POST', 'PUT'])

            routes = self.router.routes
            assert len(routes)        == 1
            assert routes[0].methods  == {'GET', 'POST', 'PUT'}

    def test_register_route__path_parsing_with_params(self):                        # Test path parsing with double underscore and params
        def api__v1__user__id(user: str, id: int):
            return {"user": user, "id": id}

        with self.registration as _:
            _.register_route(self.router, api__v1__user__id, ['GET'])

            routes = self.router.routes
            assert len(routes)    == 1
            assert routes[0].path == '/api/v1/{user}/{id}'

    def test_register_route__mixed_params(self):                                    # Test function with path and body parameters
        class Order_Data(Type_Safe):
            items    : list
            quantity : Safe_Int

        def update__order_id(order_id: Safe_Id, data: Order_Data):
            return {"order_id": str(order_id), "updated": True}

        with self.registration as _:
            _.register_route(self.router, update__order_id, ['PUT'])

            routes = self.router.routes
            assert len(routes)    == 1
            assert routes[0].path == '/update/{order_id}'

    def test_register_route_any__default_path(self):                                # Test ANY method registration with default path
        def catch_all():
            return {"method": "any"}

        with self.registration as _:
            _.register_route_any(self.router, catch_all)

            routes = self.router.routes
            assert len(routes)    == 1
            assert routes[0].path == '/catch-all'
            assert routes[0].methods == {'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT'}

    def test_register_route_any__explicit_path(self):                               # Test ANY method registration with explicit path
        def proxy(path: str):
            return {"proxied": path}

        with self.registration as _:
            _.register_route_any(self.router, proxy, "/{path:path}")

            routes = self.router.routes
            assert len(routes)    == 1
            assert routes[0].path == '/{path:path}'
            assert routes[0].methods == {'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT'}

    def test_register_route__with_return_type(self):                                # Test registering function with Type_Safe return
        class Response_Data(Type_Safe):
            message : Safe_Str
            code    : Safe_Int

        def get_status() -> Response_Data:
            return Response_Data(message=Safe_Str("ok"), code=Safe_Int(200))

        with self.registration as _:
            _.register_route(self.router, get_status, ['GET'])

            routes = self.router.routes
            assert len(routes)        == 1
            assert routes[0].path     == '/get-status'

    def test_register_route__multiple_routes(self):                                 # Test registering multiple routes on same router
        def endpoint_1():
            return {"endpoint": 1}

        def endpoint_2():
            return {"endpoint": 2}

        def endpoint_3():
            return {"endpoint": 3}

        with self.registration as _:
            _.register_route(self.router, endpoint_1, ['GET' ])
            _.register_route(self.router, endpoint_2, ['POST'])
            _.register_route(self.router, endpoint_3, ['PUT' ])

            routes = self.router.routes
            assert len(routes)        == 3
            assert routes[0].path     == '/endpoint-1'
            assert routes[1].path     == '/endpoint-2'
            assert routes[2].path     == '/endpoint-3'

    def test_register_route__complex_scenario(self):                                # Test complex registration with all features
        class Product_Data(Type_Safe):
            name     : Safe_Str
            price    : Safe_Int
            category : Safe_Id

        class Product_Response(Type_Safe):
            product_id : Safe_Id
            name       : Safe_Str
            status     : Safe_Str

        @route_path('/create/{store_id}')
        def create_product(store_id     : Safe_Id       ,
                           product_data  : Product_Data
                      ) -> Product_Response:
            return Product_Response(product_id = Safe_Id("PROD-123") ,
                                    name       = product_data.name   ,
                                    status     = Safe_Str("created") )

        with self.registration as _:
            _.register_route(self.router, create_product, ['POST'])

            routes = self.router.routes
            assert len(routes)        == 1
            assert routes[0].path     == '/create/{store_id}'
            assert routes[0].methods  == {'POST'}

    def test_register_route__preserves_function_metadata(self):                     # Test that function name and metadata preserved
        def well_documented_endpoint():
            """This endpoint is well documented."""
            return {"documented": True}

        with self.registration as _:
            _.register_route(self.router, well_documented_endpoint, ['GET'])

            routes = self.router.routes
            assert len(routes) == 1

    def test_register_route_any__integration_with_analyzer(self):                   # Test ANY route integration with analyzer
        class Request_Data(Type_Safe):
            action : Safe_Str
            params : dict

        def handle_any(data: Request_Data):
            return {"action": str(data.action)}

        with self.registration as _:
            _.register_route_any(self.router, handle_any, "/api/{path:path}")

            routes = self.router.routes
            assert len(routes)    == 1
            assert routes[0].path == '/api/{path:path}'

    def test_register_route__underscores_to_hyphens(self):                          # Test path generation converts underscores to hyphens
        def user_profile_settings():
            return {"settings": True}

        with self.registration as _:
            _.register_route(self.router, user_profile_settings, ['GET'])

            routes = self.router.routes
            assert len(routes)    == 1
            assert routes[0].path == '/user-profile-settings'

    def test_register_route__double_underscore_segments(self):                      # Test double underscore creates path segments
        def api__v1__users():
            return {"users": []}

        with self.registration as _:
            _.register_route(self.router, api__v1__users, ['GET'])

            routes = self.router.routes
            assert len(routes)    == 1
            assert routes[0].path == '/api/v1/users'

    def test_register_route__path_params_detection(self):                           # Test automatic path parameter detection
        def get__user_id__profile(user_id: str):
            return {"user_id": user_id}

        with self.registration as _:
            _.register_route(self.router, get__user_id__profile, ['GET'])

            routes = self.router.routes
            assert len(routes)    == 1
            assert routes[0].path == '/get/{user_id}/profile'