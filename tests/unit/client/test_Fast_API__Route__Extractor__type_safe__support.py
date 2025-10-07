from unittest                                                               import TestCase
from osbot_fast_api.client.Fast_API__Route__Extractor                       import Fast_API__Route__Extractor
from osbot_fast_api.client.testing.Test__Fast_API__With_Routes              import Test__Fast_API__With_Routes, Schema__User, Schema__Product
from osbot_fast_api.api.schemas.routes.Schema__Fast_API__Routes__Collection import Schema__Fast_API__Routes__Collection


class test_Fast_API__Route__Extractor__type_safe__support(TestCase):

    @classmethod
    def setUpClass(cls):                                                  # ONE-TIME expensive setup
        cls.fast_api   = Test__Fast_API__With_Routes().setup()            # Create test FastAPI app
        cls.app        = cls.fast_api.app()
        cls.extractor  = Fast_API__Route__Extractor(app=cls.app, include_default=False)

    def test__init__(self):                                               # Test auto-initialization
        with Fast_API__Route__Extractor(app=self.app) as _:
            assert _.app             is self.app
            assert _.include_default is False                             # Default value
            assert _.expand_mounts   is False                             # Default value

    def test__extract__body_params__uses_original_types(self):           # CRITICAL: Test that body params use original Type_Safe types
        collection = self.extractor.extract_routes()

        # Find the create_user route which has Schema__User as body param
        create_user_route = None
        for route in collection.routes:
            if route.method_name == 'create_user':
                create_user_route = route
                break

        assert create_user_route is not None                             # Route exists

        # Verify body params are captured
        assert len(create_user_route.body_params) == 1
        body_param = create_user_route.body_params[0]

        # CRITICAL: Should be original Type_Safe class, NOT __BaseModel variant
        assert body_param.param_type is Schema__User                     # Original class
        assert body_param.param_type.__name__ == 'Schema__User'          # Not 'Schema__User__BaseModel'
        assert body_param.name == 'user'                                 # Parameter name preserved

    def test__extract__query_params__uses_original_types(self):          # Test that query params use original types
        collection = self.extractor.extract_routes()

        # Find the list_products route which has query params
        list_products_route = None
        for route in collection.routes:
            if route.method_name == 'list_products':
                list_products_route = route
                break

        assert list_products_route is not None

        # Verify query params are captured correctly
        assert len(list_products_route.query_params) >= 2

        # Check limit parameter
        limit_param = next(p for p in list_products_route.query_params if p.name == 'limit')
        assert limit_param.param_type is int                             # Original primitive type
        assert limit_param.default == 10                                 # Default preserved

    def test__extract__path_params__uses_original_types(self):           # Test that path params use original types
        collection = self.extractor.extract_routes()

        # Find route with path parameter
        get_user_route = None
        for route in collection.routes:
            if route.method_name == 'get_user__user_id':
                get_user_route = route
                break

        assert get_user_route is not None

        # Verify path params are captured
        assert len(get_user_route.path_params) == 1
        path_param = get_user_route.path_params[0]

        assert path_param.name == 'user_id'
        assert path_param.param_type is int                              # Original type

    def test__extract__return_type__uses_original_types(self):           # Test that return types use original Type_Safe types
        collection = self.extractor.extract_routes()

        # Find route with Type_Safe return type
        get_product_route = None
        for route in collection.routes:
            if route.method_name == 'get_product__product_id':
                get_product_route = route
                break

        assert get_product_route is not None

        # CRITICAL: Return type should be original Type_Safe class
        assert get_product_route.return_type is Schema__Product          # Original class
        assert get_product_route.return_type.__name__ == 'Schema__Product'  # Not '__BaseModel' variant

    def test__regression__serialization_of_extracted_routes(self):       # Test that extracted routes serialize properly
        collection = self.extractor.extract_routes()

        # Serialize to JSON
        json_data = collection.json()

        # Verify structure
        assert 'routes'       in json_data
        assert 'total_routes' in json_data
        assert json_data['total_routes'] == len(json_data['routes'])

        # CRITICAL: Deserialize back - should work now with original types
        restored = Schema__Fast_API__Routes__Collection.from_json(json_data)
        assert collection.obj() == restored.obj()                        # Confirm they are the same

        # Compare specific routes
        original_paths = {str(r.http_path) for r in collection.routes}
        restored_paths = {str(r.http_path) for r in restored.routes}
        assert original_paths == restored_paths

    def test__no_basemodel_types_in_serialized_data(self):               # Verify no __BaseModel types appear in serialization
        collection = self.extractor.extract_routes()
        json_data  = collection.json()

        # Convert to string and check for __BaseModel references
        json_str = str(json_data)
        assert '__BaseModel' not in json_str                             # Should not appear anywhere

        # Check specific param types in JSON
        for route_data in json_data['routes']:
            if route_data.get('body_params'):
                for param in route_data['body_params']:
                    param_type = param.get('param_type', '')
                    assert '__BaseModel' not in param_type               # Original types only

            if route_data.get('return_type'):
                return_type = str(route_data['return_type'])
                assert '__BaseModel' not in return_type                  # Original types only