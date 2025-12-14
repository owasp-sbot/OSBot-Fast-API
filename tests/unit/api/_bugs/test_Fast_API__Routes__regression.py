from typing                                                     import Union
from unittest                                                   import TestCase
from osbot_fast_api.client.Fast_API__Route__Extractor           import Fast_API__Route__Extractor
from osbot_utils.type_safe.Type_Safe                            import Type_Safe
from osbot_fast_api.api.Fast_API                                import Fast_API
from osbot_fast_api.api.routes.Fast_API__Routes                 import Fast_API__Routes
from osbot_fast_api.api.schemas.Schema__Fast_API__Config        import Schema__Fast_API__Config
from osbot_fast_api.api.transformers.Type_Safe__To__BaseModel   import Type_Safe__To__BaseModel
from osbot_utils.type_safe.primitives.core.Safe_Str             import Safe_Str


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

    def test__regression__fast_api__response__base_model__not_handing__none_values__in_type_safe_primitives(self):
        from osbot_fast_api.api.Fast_API import Fast_API

        class An_Response_Class(Type_Safe):
            an_str : Safe_Str = None

        class Routes__ABC(Fast_API__Routes):
            def an_post__fails(self) -> An_Response_Class:
                return An_Response_Class()

            def an_post__ok_1(self) -> An_Response_Class:
                return An_Response_Class(an_str='')

            def an_post__ok_2(self) -> An_Response_Class:
                return An_Response_Class(an_str='ok')

            def setup_routes(self):
                self.add_routes_post(self.an_post__fails,
                                     self.an_post__ok_1 ,
                                     self.an_post__ok_2 )

        config  = Schema__Fast_API__Config(default_routes=False)
        class Fast_API__Abc(Fast_API):
            def setup_routes(self):
                self.add_routes(Routes__ABC)
                return self

        fast_api_abc = Fast_API__Abc(config=config).setup()
        assert fast_api_abc.routes_paths() == ['/an-post/fails',
                                               '/an-post/ok-1',
                                               '/an-post/ok-2']

        with fast_api_abc.client() as _:
            # error_message = "1 validation error for An_Response_Class__BaseModel\nan_str\n  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]\n    For further information visit https://errors.pydantic.dev/2.12/v/string_type"
            # with pytest.raises(ValueError, match=re.escape(error_message)):
            #     _.post(url='/an-post/fails')                                # BUG: should have worked

            assert _.post(url='/an-post/fails').json() == {'an_str': None}

            assert _.post(url='/an-post/ok-1').json() == {'an_str': ''  }
            assert _.post(url='/an-post/ok-2').json() == {'an_str': 'ok'}

    def test__regression__type_safe_to_basemodel__converter__handle__none_return_values__no_optional(self):

        class An_Class(Type_Safe):
            #an_str : Safe_Str = None
            an_str : str = None             # when we make this optional , it fails


        # error_message = ("1 validation error for An_Class__BaseModel\nan_str\n  "
        #                  "Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]\n    "
        #                  "For further information visit https://errors.pydantic.dev/2.12/v/string_type")
        # with pytest.raises(ValueError, match=re.escape(error_message)):
        #     result = Type_Safe__To__BaseModel().convert_instance(An_Class())              # BUG

        result = Type_Safe__To__BaseModel().convert_instance(An_Class())                    # FIXED
        assert result.model_json_schema() == {'properties': {'an_str': {'anyOf': [{'type': 'string'},
                                                                                  {'type': 'null'}],
                                                                        'default': None,
                                                                        'title': 'An Str'}},
                                              'title': 'An_Class__BaseModel',
                                              'type': 'object'}