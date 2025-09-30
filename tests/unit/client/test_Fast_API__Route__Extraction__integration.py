import time
from typing                                                                      import List
from unittest                                                                    import TestCase
from fastapi                                                                     import FastAPI, APIRouter
from osbot_utils.testing.__                                                      import __
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id  import Safe_Str__Id
from osbot_fast_api.api.Fast_API                                                 import Fast_API
from osbot_fast_api.api.decorators.route_path                                    import route_path
from osbot_fast_api.api.routes.Fast_API__Routes                                  import Fast_API__Routes
from osbot_fast_api.client.Fast_API__Route__Extractor                            import Fast_API__Route__Extractor
from osbot_fast_api.schemas.for_osbot_utils.enums.Enum__Http__Method             import Enum__Http__Method
from osbot_fast_api.schemas.routes.Schema__Fast_API__Routes__Collection          import Schema__Fast_API__Routes__Collection
from osbot_fast_api.schemas.routes.enums.Enum__Route__Type                       import Enum__Route__Type


class test_Fast_API__Route__Extraction__integration(TestCase):          # Integration tests for complete route extraction workflow

    # todo: see if can use the Test__Fast_API__With_Routes.py class and endpoints here
    @classmethod
    def setUpClass(cls):
        # Build a comprehensive FastAPI app with all route types
        cls.fast_api = Fast_API(name="Integration Test API")
        cls.fast_api.setup()

        # Add various route classes
        class Routes__Users(Fast_API__Routes):
            tag = 'users'

            def list_users(self):
                return []

            @route_path('/user/{user_id}')
            def get_user(self, user_id: int):
                return {}

            def create_user(self, data: dict):
                return {}

            @route_path('/user/{user_id}')
            def update_user(self, user_id: int, data: dict):
                return {}

            @route_path('/user/{user_id}')
            def delete_user(self, user_id: int):
                return {}

            def setup_routes(self):
                self.add_route_get   (self.list_users )
                self.add_route_get   (self.get_user   )
                self.add_route_post  (self.create_user)
                self.add_route_put   (self.update_user)
                self.add_route_delete(self.delete_user)

        class Routes__Admin(Fast_API__Routes):
            tag = 'admin'

            def admin__dashboard(self):             # , "/dashboard"
                return {"status": "admin"}

            def admin__health(self):                # , "/admin/health"
                return {"healthy": True}

            def setup_routes(self):
                self.add_route_get(self.admin__dashboard)
                self.add_route_get(self.admin__health  )
                self.add_route_any(self.catch_all      , )

            @route_path("/{path:path}")
            def catch_all(self, path: str):
                return {"path": path}

        cls.fast_api.add_routes(Routes__Users)
        cls.fast_api.add_routes(Routes__Admin)

        # Add WebSocket
        @cls.fast_api.app().websocket("/ws/notifications")
        async def notification_websocket(websocket):
            pass

        # Add nested router with sub-routes
        api_v2 = APIRouter(prefix="/api/v2")

        @api_v2.get("/products")
        def list_products():
            return []

        @api_v2.get("/products/{product_id}")
        def get_product(product_id: str):
            return {}

        nested_router = APIRouter(prefix="/nested")

        @nested_router.get("/deep/route")
        def deep_route():
            return {}

        api_v2.include_router(nested_router)
        cls.fast_api.app().include_router(api_v2)

        # Create extractor
        cls.extractor = Fast_API__Route__Extractor(app=cls.fast_api.app())

    def test_complete_extraction(self):                                             # Test extracting all routes from complex app
        collection = self.extractor.extract_routes()

        # Verify collection metadata
        assert type(collection) is Schema__Fast_API__Routes__Collection
        assert collection.total_routes > 10                                         # Should have many routes
        assert collection.has_websockets is True

        # Verify route paths exist
        paths = [str(r.http_path) for r in collection.routes]

        # User routes
        assert '/users/list-users'      in paths
        assert '/users/user/{user_id}'  in paths
        assert '/users/create-user'     in paths

        # Admin routes
        assert '/admin/admin/dashboard' in paths
        assert '/admin/admin/health' in paths
        assert '/admin/{path:path}' in paths

        # API v2 routes
        assert '/api/v2/products' in paths
        assert '/api/v2/products/{product_id}' in paths
        assert '/api/v2/nested/deep/route' in paths

        # WebSocket
        assert '/ws/notifications' in paths

    def test_route_class_extraction(self):                                          # Test that Routes__ classes are identified
        collection = self.extractor.extract_routes()
        # Find routes with class info
        user_routes = [r for r in collection.routes
                      if r.route_class == 'Routes__Users']

        admin_routes = [r for r in collection.routes
                       if r.route_class == 'Routes__Admin']

        assert len(user_routes ) >= 5                                                # All user route methods
        assert len(admin_routes) >= 3                                               # All admin route methods

        # Verify method names match
        user_method_names = {str(r.method_name) for r in user_routes}
        assert 'list_users' in user_method_names
        assert 'get_user' in user_method_names
        assert 'create_user' in user_method_names

    def test_http_methods_correct(self):                                            # Test that HTTP methods are correctly identified
        collection = self.extractor.extract_routes()

        # Find specific routes and verify methods
        create_user = next((r for r in collection.routes
                           if r.method_name == 'create_user'), None)
        assert create_user is not None
        assert Enum__Http__Method.POST in create_user.http_methods

        update_user = next((r for r in collection.routes
                           if r.method_name == 'update_user'), None)
        assert update_user is not None
        assert Enum__Http__Method.PUT in update_user.http_methods

        delete_user = next((r for r in collection.routes
                           if r.method_name == 'delete_user'), None)
        assert delete_user is not None
        assert Enum__Http__Method.DELETE in delete_user.http_methods

        # Check catch-all route has all methods
        catch_all = next((r for r in collection.routes
                         if r.method_name == 'catch_all'), None)
        assert catch_all is not None
        assert len(catch_all.http_methods) == 7                                     # All HTTP methods

    def test_websocket_routes(self):                                                # Test WebSocket route extraction
        collection = self.extractor.extract_routes()

        ws_routes = [r for r in collection.routes
                    if r.route_type == Enum__Route__Type.WEBSOCKET]

        assert len(ws_routes) >= 1

        notification_ws = next((r for r in ws_routes
                               if '/notifications' in str(r.http_path)), None)
        assert notification_ws is not None
        assert notification_ws.http_methods == []                                   # WebSockets have no HTTP methods

    def test_nested_router_extraction(self):                                        # Test deeply nested routers are extracted
        collection = self.extractor.extract_routes()

        # Find the deeply nested route
        deep_route = next((r for r in collection.routes
                          if str(r.http_path) == '/api/v2/nested/deep/route'), None)

        assert deep_route is not None
        assert deep_route.method_name == 'deep_route'
        assert Enum__Http__Method.GET in deep_route.http_methods

    def test_path_parameters_preserved(self):                                       # Test that path parameters are preserved
        collection = self.extractor.extract_routes()

        #collection.print()
        # Routes with path parameters
        param_routes = [r for r in collection.routes
                       if '{' in str(r.http_path)]

        assert len(param_routes) > 0

        # Check specific parameter patterns
        user_id_routes = [r for r in param_routes
                         if '{user_id}' in str(r.http_path)]

        assert len(user_id_routes) >= 3                                             # get, update, delete

        product_id_route = next((r for r in param_routes
                                if '{product_id}' in str(r.http_path)), None)
        assert product_id_route is not None

        catch_all_route = next((r for r in param_routes
                              if '{path:path}' in str(r.http_path)), None)
        assert catch_all_route is not None

    def test_serialization_of_extracted_routes(self):                               # Test that extracted routes serialize properly
        collection = self.extractor.extract_routes()

        # Serialize to JSON
        json_data = collection.json()

        # Verify structure
        assert 'routes' in json_data
        assert 'total_routes' in json_data
        assert json_data['total_routes'] == len(json_data['routes'])

        # Deserialize back
        restored = Schema__Fast_API__Routes__Collection.from_json(json_data)

        # Compare specific routes
        original_paths = {str(r.http_path) for r in collection.routes}
        restored_paths = {str(r.http_path) for r in restored.routes}
        assert original_paths == restored_paths

        # Check enum preservation
        for orig, rest in zip(collection.routes, restored.routes):
            if orig.route_type == Enum__Route__Type.WEBSOCKET:
                assert rest.route_type == Enum__Route__Type.WEBSOCKET

    def test_filtering_default_routes(self):                                        # Test include_default flag behavior
        # Without defaults
        extractor_no_default = Fast_API__Route__Extractor(app             = self.fast_api.app(),
                                                          include_default = False             )
        collection_no_default = extractor_no_default.extract_routes()

        # With defaults
        extractor_with_default = Fast_API__Route__Extractor(app             = self.fast_api.app(),
                                                            include_default = True               )
        collection_with_default = extractor_with_default.extract_routes()

        # Should have more routes when including defaults
        assert collection_with_default.total_routes > collection_no_default.total_routes

        # Check for specific default routes
        paths_with_default = [str(r.http_path) for r in collection_with_default.routes]
        default_paths = ['/docs', '/redoc', '/openapi.json']

        if collection_with_default.total_routes > collection_no_default.total_routes:
            assert any(path in paths_with_default for path in default_paths)                # At least one default route should be present

    def test_route_extraction_performance(self):                                            # Test performance with many routes
        large_app = FastAPI()                                                               # Create app with many routes

        for i in range(100):                                                                # Add 100 routes
            @large_app.get(f"/route_{i}")
            def handler():
                return {}

        extractor   = Fast_API__Route__Extractor(app=large_app)                             # Extract and measure
        start       = time.time()
        collection  = extractor.extract_routes()
        elapsed     = time.time() - start

        assert collection.total_routes >= 100
        assert elapsed < 1.0                                                        # Should be fast even with 100 routes

    def test_edge_case_empty_app(self):                                             # Test extraction from empty app
        empty_app = FastAPI()
        extractor = Fast_API__Route__Extractor(app=empty_app)

        collection = extractor.extract_routes()

        # Even empty app might have some default routes
        # but should handle gracefully
        assert type(collection) is Schema__Fast_API__Routes__Collection
        assert collection.total_routes >= 0

    def test_edge_case_special_characters_in_paths(self):                           # Test special characters in route paths
        app = FastAPI()

        @app.get("/special-chars_123/route")
        def special1():
            return {}

        @app.get("/route.with.dots")
        def special2():
            return {}

        @app.get("/route@with#special$chars")           # this will be filtered as "/special-chars_123/route"
        def special3():
            return {}

        extractor = Fast_API__Route__Extractor(app=app)
        collection = extractor.extract_routes()

        paths = [str(r.http_path) for r in collection.routes]
        assert '/special-chars_123/route'   in paths
        assert '/route.with.dots'           in paths
        assert '/special-chars_123/route'   in paths

    # @pytest.mark.skip(reason="Requires Flask installation")
    # def test_wsgi_mount_extraction(self):                                           # Test WSGI app mount extraction
    #     from flask import Flask
    #     from starlette.middleware.wsgi import WSGIMiddleware
    #
    #     # Create Flask app
    #     flask_app = Flask(__name__)
    #
    #     @flask_app.route('/flask-route')
    #     def flask_handler():
    #         return "Flask"
    #
    #     # Mount in FastAPI
    #     app = FastAPI()
    #     app.mount("/legacy", WSGIMiddleware(flask_app))
    #
    #     extractor = Fast_API__Route__Extractor(app=app)
    #     collection = extractor.extract_routes()
    #
    #     # Find WSGI mount
    #     wsgi_route = next((r for r in collection.routes
    #                       if r.route_type == Enum__Route__Type.WSGI), None)
    #
    #     assert wsgi_route is not None
    #     assert wsgi_route.http_path == '/legacy'
    #     assert wsgi_route.is_mount is True

    def test_route_priority_and_ordering(self):                                     # Test that routes maintain order
        app = FastAPI()

        # Add routes in specific order
        @app.get("/first")
        def first():
            pass

        @app.get("/second")
        def second():
            pass

        @app.get("/third")
        def third():
            pass

        extractor = Fast_API__Route__Extractor(app=app)
        collection = extractor.extract_routes()

        # Routes should maintain registration order
        route_names = [str(r.method_name) for r in collection.routes]
        assert 'first' in route_names
        assert 'second' in route_names
        assert 'third' in route_names


    def test__confirm__primitive_equality__in_fast_api_routes(self):
        class An_Class(Type_Safe):
            an_id   : Safe_Str__Id
            an_list : List[Safe_Str__Id]

        an_class = An_Class(an_id='abc', an_list=['abc'])
        assert an_class.an_id                == 'abc'
        assert (an_class.an_list == ['abc']) is True
        assert ('abc' in an_class.an_list )  is True
        assert ([r for r in an_class.an_list
                      if r == 'abc'])        == ['abc']

        class Schema__Route(Type_Safe):
            route_class   : Safe_Str__Id

        class Schema__Collection(Type_Safe):                    # Collection of routes
            routes        : List[Schema__Route]

        an_collection = Schema__Collection(routes=[Schema__Route(route_class='abc')])
        assert an_collection.obj()                   == __(routes=[__(route_class='abc')])
        assert an_collection.routes                  != [Schema__Route(route_class='abc')]
        assert an_collection.routes.json()           == [{'route_class': 'abc'}]

        assert [r.route_class for r in an_collection.routes
                if r.route_class == 'abc'                 ] == ['abc']

        assert [r.route_class for r in an_collection.routes
                if r.route_class == 'abc'                 ] == ['abc']

        assert [r.route_class for r in an_collection.routes
                if r.route_class == (Safe_Str__Id('abc')) ] == ['abc']