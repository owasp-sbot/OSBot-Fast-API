from typing                                           import Union
from unittest                                         import TestCase
from osbot_fast_api.client.Fast_API__Route__Extractor import Fast_API__Route__Extractor
from osbot_utils.type_safe.Type_Safe                  import Type_Safe
from osbot_fast_api.api.Fast_API                      import Fast_API


class test_Fast_API__Routes__regression(TestCase):

    def test__regression__error_with_union_return_type(self):           # Test that Union return types are handled gracefully (no error, but return_type not set)
        
        def an_union_return_type() -> Union[str, int]:
            return "test"
        
        with Fast_API() as fast_api:
            fast_api.add_route_get(an_union_return_type)                # Should not raise an error anymore

            routes = fast_api.routes()                                  # Verify the route was added successfully
            assert len(routes) > 0

            our_route = None                                            # Find our route
            for route in routes:
                if route.get('method_name') == 'an_union_return_type':
                    our_route = route
                    break
            
            assert our_route is not None, "Route should be registered"

            # Verify that return_type is None (Union types are skipped)
            assert our_route.get('return_type') is None, "Union return types should be skipped, resulting in None return_type"

            client = fast_api.client()                                  # Verify the route still works
            response = client.get('/an-union-return-type')
            assert response.status_code == 200

    def test__regression__concrete_return_type_works(self):                         # Test that concrete return types still work correctly

        class Schema__Response(Type_Safe):
            message: str

        def concrete_return_type() -> Schema__Response:
            return Schema__Response(message="test")

        with Fast_API() as fast_api:
            fast_api.add_route_get(concrete_return_type)

            extractor = Fast_API__Route__Extractor(app=fast_api.app(), include_default=False)       # Use Fast_API__Route__Extractor to get full route schemas
            routes_collection = extractor.extract_routes()

            our_route = None                                                                        # Find our route
            for route in routes_collection.routes:
                if route.method_name == 'concrete_return_type':
                    our_route = route
                    break

            assert our_route is not None, "Route should be registered"

            assert our_route.http_path == '/concrete-return-type'                                   # Verify the route structure
            assert 'GET' in [m.value for m in our_route.http_methods]

            assert our_route.return_type is not None, "Concrete return types should be captured"    # Verify that return_type IS set for concrete types
            assert our_route.return_type == Schema__Response, "Return type should match the Type_Safe class"

            client = fast_api.client()                                                              # Verify the route works
            response = client.get('/concrete-return-type')
            assert response.status_code == 200
            assert response.json() == {"message": "test"}