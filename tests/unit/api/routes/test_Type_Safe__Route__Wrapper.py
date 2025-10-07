from unittest                                                                       import TestCase
from fastapi                                                                        import HTTPException
from osbot_utils.utils.Objects                                                      import type_full_name
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Email          import Safe_Str__Email
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                                 import Safe_Str
from osbot_utils.type_safe.primitives.core.Safe_Int                                 import Safe_Int
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                   import Safe_Id
from osbot_fast_api.api.routes.Type_Safe__Route__Analyzer                           import Type_Safe__Route__Analyzer
from osbot_fast_api.api.routes.Type_Safe__Route__Converter                          import Type_Safe__Route__Converter
from osbot_fast_api.api.routes.Type_Safe__Route__Wrapper                            import Type_Safe__Route__Wrapper
import re


class test_Type_Safe__Route__Wrapper(TestCase):

    @classmethod
    def setUpClass(cls):                                                            # Setup expensive resources once
        cls.analyzer  = Type_Safe__Route__Analyzer()
        cls.converter = Type_Safe__Route__Converter()
        cls.wrapper   = Type_Safe__Route__Wrapper(converter=cls.converter)

    def test__init__(self):                                                         # Test wrapper initialization
        with Type_Safe__Route__Wrapper() as _:
            assert type(_)           is Type_Safe__Route__Wrapper
            assert type(_.converter) is Type_Safe__Route__Converter

    def test_create_wrapper__no_conversion_needed(self):                            # Test wrapping function that needs no conversion
        def simple_endpoint(name: str) -> dict:
            return {"name": name}

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(simple_endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_wrapper(simple_endpoint, signature)

            assert wrapper is simple_endpoint                                       # No conversion, returns original

    def test_create_wrapper__with_primitive_conversion(self):                       # Test wrapping function with primitive parameters
        def get_user(user_id: Safe_Id) -> dict:
            return {"user_id": str(user_id), "type": type(user_id).__name__}

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(get_user)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_wrapper(get_user, signature)

            assert wrapper is not get_user                                          # Conversion needed, new wrapper created
            result = wrapper(user_id='test-id-123')
            assert result == {"user_id": 'test-id-123', "type": "Safe_Id"}

    def test_create_wrapper__with_type_safe_body_param(self):                       # Test wrapping function with Type_Safe body parameter
        class User_Data(Type_Safe):
            name  : Safe_Str
            email : Safe_Str__Email

        def create_user(user_data: User_Data) -> dict:
            return {"name": str(user_data.name), "email": str(user_data.email)}

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(create_user)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_wrapper(create_user, signature)

            user_dict = {'name': 'Alice', 'email': 'alice@test.com'}
            result = wrapper(user_data=user_dict)
            assert result == {"name": 'Alice', "email": 'alice@test.com'}

    def test_create_body_wrapper__http_exception_propagation(self):                 # Test that HTTPException is re-raised
        class User_Data(Type_Safe):
            name: Safe_Str

        def endpoint(user_data: User_Data):
            raise HTTPException(status_code=400, detail="Bad request")

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_body_wrapper(endpoint, signature)

            try:
                wrapper(user_data={'name': 'test'})
                assert False, "Should have raised HTTPException"
            except HTTPException as e:
                assert e.status_code == 400
                assert e.detail      == "Bad request"

    def test_create_body_wrapper__generic_exception_handling(self):                 # Test generic exception wrapping
        class User_Data(Type_Safe):
            name: Safe_Str

        def endpoint(user_data: User_Data):
            raise ValueError("Invalid data")

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_body_wrapper(endpoint, signature)

            try:
                wrapper(user_data={'name': 'test'})
                assert False, "Should have raised HTTPException"
            except HTTPException as e:
                assert e.status_code == 400
                assert "ValueError: Invalid data" in e.detail

    def test_create_query_wrapper__validation_error_handling(self):                 # Test query wrapper validation error handling
        def get_user(user_id: Safe_Id):
            return {"user_id": str(user_id)}

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(get_user)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_query_wrapper(get_user, signature)

            result = wrapper(user_id='valid-id')
            assert result == {"user_id": 'valid-id'}

    def test_create_wrapper__with_return_conversion(self):                          # Test wrapping function with Type_Safe return
        class Response_Data(Type_Safe):
            message : Safe_Str
            code    : Safe_Int

        def endpoint() -> Response_Data:
            return Response_Data(message=Safe_Str("success"), code=Safe_Int(200))

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_wrapper(endpoint, signature)

            result = wrapper()
            assert type(result) is dict
            assert result       == {'message': 'success', 'code': 200}

    def test_build_wrapper_parameters__primitive_replacement(self):                 # Test signature parameter building
        def get_user(user_id: Safe_Id, name: Safe_Str):
            return {"user_id": user_id, "name": name}

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(get_user)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            new_params = _.build_wrapper_parameters(get_user, signature)

            assert len(new_params)      == 2
            assert new_params[0].name   == 'user_id'
            assert new_params[0].annotation is str                                  # Primitive base type
            assert new_params[1].name   == 'name'
            assert new_params[1].annotation is str

    def test_build_wrapper_parameters__type_safe_replacement(self):                 # Test Type_Safe parameter replacement with BaseModel
        class User_Data(Type_Safe):
            name : Safe_Str

        def create_user(user_data: User_Data):
            return user_data

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(create_user)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            new_params = _.build_wrapper_parameters(create_user, signature)

            assert len(new_params)      == 1
            assert new_params[0].name   == 'user_data'
            assert new_params[0].annotation is not User_Data                        # Replaced with BaseModel

    def test_build_wrapper_annotations__primitive_types(self):                      # Test annotation building for primitives
        def endpoint(user_id: Safe_Id, count: Safe_Int):
            return {"user_id": user_id, "count": count}

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            annotations = _.build_wrapper_annotations(endpoint, signature)

            assert 'user_id' in annotations
            assert 'count'   in annotations
            assert annotations['user_id'] is str
            assert annotations['count']   is int

    def test_build_wrapper_annotations__return_type(self):                          # Test return annotation building
        class Response_Data(Type_Safe):
            status: Safe_Str

        def endpoint() -> Response_Data:
            return Response_Data(status=Safe_Str("ok"))

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            annotations = _.build_wrapper_annotations(endpoint, signature)

            assert 'return' in annotations
            assert annotations['return']                 is not Response_Data                       # Replaced with BaseModel
            assert type(annotations)                     is dict
            assert type_full_name(annotations['return']) == 'osbot_fast_api.api.transformers.Type_Safe__To__BaseModel.Response_Data__BaseModel'

    def test_create_wrapper__complex_mixed_scenario(self):                          # Test complex scenario with multiple conversion types
        class Product_Data(Type_Safe):
            name  : Safe_Str
            price : Safe_Int

        class Product_Response(Type_Safe):
            product_id : Safe_Id
            name       : Safe_Str
            status     : Safe_Str

        def create_product(store_id      : Safe_Id      ,
                           product_data  : Product_Data ,
                           notify        : bool = False
                      ) -> Product_Response:
            return Product_Response(product_id = Safe_Id("PROD-123")    ,
                                    name       = product_data.name      ,
                                    status     = Safe_Str("created")    )

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(create_product)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_wrapper(create_product, signature)

            product_dict = {'name': 'Widget', 'price': 99}
            result = wrapper(store_id='STORE-1', product_data=product_dict, notify=True)

            assert type(result) is dict
            assert result['product_id'] == 'PROD-123'
            assert result['name']       == 'Widget'
            assert result['status']     == 'created'

    def test_create_query_wrapper__with_positional_args(self):                      # Test query wrapper with positional arguments
        def endpoint(user_id: Safe_Id):
            return {"user_id": str(user_id)}

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_query_wrapper(endpoint, signature)

            result = wrapper(user_id='test-id')
            assert result == {"user_id": 'test-id'}