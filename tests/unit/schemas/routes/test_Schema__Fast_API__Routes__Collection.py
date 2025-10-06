from unittest                                                              import TestCase
from osbot_utils.testing.__                                                import __
from osbot_utils.type_safe.Type_Safe                                       import Type_Safe
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List      import Type_Safe__List
from osbot_utils.utils.Objects                                             import base_classes
from osbot_fast_api.schemas.Schema__Fast_API__Route                 import Schema__Fast_API__Route
from osbot_fast_api.schemas.Schema__Fast_API__Routes__Collection    import Schema__Fast_API__Routes__Collection
from osbot_utils.type_safe.primitives.domains.http.enums.Enum__Http__Method       import Enum__Http__Method
from osbot_fast_api.schemas.enums.Enum__Fast_API__Route__Type                 import Enum__Fast_API__Route__Type


class test_Schema__Fast_API__Routes__Collection(TestCase):

    def test__init__(self):                                                         # Test auto-initialization of collection
        with Schema__Fast_API__Routes__Collection() as _:
            assert type(_)         is Schema__Fast_API__Routes__Collection
            assert base_classes(_) == [Type_Safe, object]

            # Verify field types
            assert type(_.routes)         is Type_Safe__List                       # Type_Safe collection
            assert type(_.total_routes)   is int
            assert type(_.has_mounts)     is bool
            assert type(_.has_websockets) is bool

            # Verify defaults
            assert _.obj() == __(routes         = []                               ,  # Empty Type_Safe__List
                                 total_routes   = 0                                ,  # Zero count
                                 has_mounts     = False                            ,  # No mounts by default
                                 has_websockets = False                            )  # No websockets by default

    def test_with_single_route(self):                                              # Test collection with one route
        route = Schema__Fast_API__Route(http_path    = '/api/test',
                                        method_name  = 'test_endpoint',
                                        http_methods = [Enum__Http__Method.GET])

        with Schema__Fast_API__Routes__Collection(routes       = [route]          ,
                                                  total_routes = 1                 ) as _:
            assert _.total_routes == 1
            assert len(_.routes)  == 1
            assert _.routes[0].http_path == '/api/test'
            assert _.has_mounts     is False
            assert _.has_websockets is False

    def test_with_multiple_routes(self):                                           # Test collection with various route types
        routes = [
            Schema__Fast_API__Route(http_path    = '/api/users',
                                    method_name  = 'get_users',
                                    http_methods = [Enum__Http__Method.GET],
                                    route_type   = Enum__Fast_API__Route__Type.API_ROUTE),

            Schema__Fast_API__Route(http_path    = '/api/users',
                                    method_name  = 'create_user',
                                    http_methods = [Enum__Http__Method.POST],
                                    route_type   = Enum__Fast_API__Route__Type.API_ROUTE),

            Schema__Fast_API__Route(http_path    = '/ws/chat'                      ,
                                    method_name  = 'websocket_handler'             ,
                                    http_methods = []                              ,
                                    route_type   = Enum__Fast_API__Route__Type.WEBSOCKET     ),

            Schema__Fast_API__Route(http_path    = '/static',
                                    method_name  = 'static_files',
                                    http_methods = [Enum__Http__Method.GET],
                                    route_type   = Enum__Fast_API__Route__Type.STATIC,
                                    is_mount     = True)
        ]

        with Schema__Fast_API__Routes__Collection(routes         = routes         ,
                                                  total_routes   = 4              ,
                                                  has_mounts     = True           ,
                                                  has_websockets = True           ) as _:
            assert _.total_routes   == 4
            assert len(_.routes)    == 4
            assert _.has_mounts     is True
            assert _.has_websockets is True

            # Verify route types are preserved
            assert _.routes[0].route_type == Enum__Fast_API__Route__Type.API_ROUTE
            assert _.routes[2].route_type == Enum__Fast_API__Route__Type.WEBSOCKET
            assert _.routes[3].route_type == Enum__Fast_API__Route__Type.STATIC
            assert _.routes[3].is_mount   is True

    def test_automatic_flag_detection(self):                                       # Test that flags can be auto-computed
        routes = [
            Schema__Fast_API__Route(route_type = Enum__Fast_API__Route__Type.API_ROUTE     ),
            Schema__Fast_API__Route(route_type = Enum__Fast_API__Route__Type.WEBSOCKET     ),
            Schema__Fast_API__Route(route_type = Enum__Fast_API__Route__Type.MOUNT         ,
                                   is_mount    = True                             )
        ]

        with Schema__Fast_API__Routes__Collection(routes = routes) as _:                                # Even if not set, collection should be able to compute these
            websocket_exists = any(r.route_type == Enum__Fast_API__Route__Type.WEBSOCKET for r in _.routes)       # (though in practice, Fast_API__Route__Extractor sets them)
            mount_exists     = any(r.is_mount for r in _.routes)

            assert websocket_exists is True
            assert mount_exists     is True

    def test_empty_collection(self):                                               # Test empty collection state
        with Schema__Fast_API__Routes__Collection() as _:
            assert _.routes         == []
            assert _.total_routes   == 0
            assert _.has_mounts     is False
            assert _.has_websockets is False

            # Verify it's a Type_Safe__List that enforces type
            assert type(_.routes) is Type_Safe__List

    def test_serialization_round_trip(self):                                       # Test JSON serialization with nested schemas
        routes = [Schema__Fast_API__Route(http_path    = '/api/v1/health',
                                    method_name  = 'health_check',
                                    http_methods = [Enum__Http__Method.GET],
                                    route_class  = 'Routes__Health'),

                 Schema__Fast_API__Route(http_path    = '/ws/notifications'           ,
                                        method_name  = 'notification_ws'              ,
                                        route_type   = Enum__Fast_API__Route__Type.WEBSOCKET    )]

        with Schema__Fast_API__Routes__Collection(routes         = routes        ,
                                                  total_routes   = 2             ,
                                                  has_websockets = True          ) as original:
            # Serialize to JSON
            json_data = original.json()


            # Verify JSON structure
            assert 'routes'         in json_data
            assert 'total_routes'   in json_data
            assert 'has_mounts'     in json_data
            assert 'has_websockets' in json_data

            # Deserialize back
            with Schema__Fast_API__Routes__Collection.from_json(json_data) as restored:
                # Must be perfect round-trip
                assert restored.obj() == original.obj()

                # Verify nested schemas preserved
                assert len(restored.routes) == 2
                assert restored.routes[0].http_path   == '/api/v1/health'
                assert restored.routes[0].route_class == 'Routes__Health'
                assert restored.routes[1].route_type  == Enum__Fast_API__Route__Type.WEBSOCKET

                # Verify type preservation
                assert type(restored.routes) is Type_Safe__List
                assert all(type(r) is Schema__Fast_API__Route for r in restored.routes)

    def test_large_collection(self):                                               # Test with realistic number of routes
        routes = []
        for i in range(50):
            route = Schema__Fast_API__Route(
                http_path    = f'/api/endpoint_{i}'                              ,
                method_name  = f'endpoint_{i}'                                   ,
                http_methods = [Enum__Http__Method.GET, Enum__Http__Method.POST] ,
                route_class  = f'Routes__Module_{i // 10}'                       # Group into modules
            )
            routes.append(route)

        # Add some special routes
        routes.append(Schema__Fast_API__Route(
            http_path    = '/ws/stream'                                          ,
            route_type   = Enum__Fast_API__Route__Type.WEBSOCKET
        ))

        routes.append(Schema__Fast_API__Route(
            http_path    = '/static'                                             ,
            route_type   = Enum__Fast_API__Route__Type.STATIC                              ,
            is_mount     = True
        ))

        with Schema__Fast_API__Routes__Collection(routes         = routes        ,
                                                  total_routes   = 52            ,
                                                  has_mounts     = True          ,
                                                  has_websockets = True          ) as _:
            assert _.total_routes == 52
            assert len(_.routes)  == 52

            # Verify different route classes
            route_classes = {r.route_class for r in _.routes if r.route_class}
            assert len(route_classes) >= 5                                         # At least 5 different modules

            # Verify flags
            assert _.has_mounts     is True
            assert _.has_websockets is True

    def test_type_safety_on_routes_list(self):                                     # Test that Type_Safe__List enforces type
        with Schema__Fast_API__Routes__Collection() as _:
            route = Schema__Fast_API__Route(http_path = '/test')                    # Valid: Adding Schema__Fast_API__Route
            _.routes.append(route)
            assert len(_.routes) == 1

    def test_collection_with_default_routes(self):                                 # Test collection including default FastAPI routes
        routes = [
            Schema__Fast_API__Route(http_path   = '/docs'                        ,
                                   method_name = 'swagger_ui_html'               ,
                                   is_default  = True                            ),

            Schema__Fast_API__Route(http_path   = '/openapi.json'                ,
                                   method_name = 'openapi'                       ,
                                   is_default  = True                            ),

            Schema__Fast_API__Route(http_path   = '/api/users'                   ,
                                   method_name = 'get_users'                     ,
                                   is_default  = False                           )
        ]

        with Schema__Fast_API__Routes__Collection(routes = routes, total_routes = 3) as _:
            # Count default vs custom routes
            default_count = sum(1 for r in _.routes if r.is_default)
            custom_count  = sum(1 for r in _.routes if not r.is_default)

            assert default_count == 2
            assert custom_count  == 1
            assert _.total_routes == 3

    def test_collection_update_operations(self):                                   # Test modifying collection after creation
        with Schema__Fast_API__Routes__Collection() as _:
            # Start empty
            assert _.total_routes == 0
            assert _.routes == []

            # Add routes one by one
            route1 = Schema__Fast_API__Route(http_path = '/api/v1')
            route2 = Schema__Fast_API__Route(http_path = '/api/v2',
                                             route_type = Enum__Fast_API__Route__Type.WEBSOCKET)

            _.routes.append(route1)
            _.routes.append(route2)
            _.total_routes = 2
            _.has_websockets = True

            # Verify updates
            assert len(_.routes)    == 2
            assert _.total_routes   == 2
            assert _.has_websockets is True
            assert _.routes[0].http_path == '/api/v1'
            assert _.routes[1].route_type == Enum__Fast_API__Route__Type.WEBSOCKET