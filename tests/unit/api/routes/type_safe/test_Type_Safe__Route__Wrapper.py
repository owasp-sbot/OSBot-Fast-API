import inspect
from unittest                                                               import TestCase
from fastapi                                                                import HTTPException
from pydantic                                                               import BaseModel
from osbot_utils.utils.Objects                                              import type_full_name, full_type_name
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Email  import Safe_Str__Email
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                         import Safe_Str
from osbot_utils.type_safe.primitives.core.Safe_Int                         import Safe_Int
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id           import Safe_Id
from osbot_fast_api.api.routes.type_safe.Type_Safe__Route__Analyzer         import Type_Safe__Route__Analyzer
from osbot_fast_api.api.routes.type_safe.Type_Safe__Route__Converter        import Type_Safe__Route__Converter
from osbot_fast_api.api.routes.type_safe.Type_Safe__Route__Wrapper          import Type_Safe__Route__Wrapper
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

            assert wrapper is not simple_endpoint                                   # Passthrough wrapper created to preserve return type
            assert hasattr(wrapper, '__annotations__')                              # Has annotations for OpenAPI
            assert 'return' in wrapper.__annotations__                              # Return type preserved
            assert wrapper.__annotations__['return'] is dict                        # Correct return type

            # Verify it still works correctly
            result = wrapper(name="test")
            assert result == {"name": "test"}

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


    def test__create_wrapper__preserves_original_param_types(self):             # Test that original parameter types are preserved
        def test_function(user: Schema__Test_User) -> dict:                     # Function with Type_Safe parameter
            return {'user_id': user.user_id}

        signature = self.analyzer.analyze_function(test_function)
        signature = self.converter.enrich_signature_with_conversions(signature)
        wrapper   = self.wrapper.create_wrapper(test_function, signature)

        assert hasattr(wrapper, '__original_param_types__')                     # CRITICAL: Verify original types are preserved in metadata
        assert 'user' in wrapper.__original_param_types__
        assert wrapper.__original_param_types__['user'] is Schema__Test_User    # Original Type_Safe class, NOT BaseModel

    def test__create_wrapper__preserves_original_return_type(self):             # Test that original return type is preserved
        def test_function() -> Schema__Test_User:                               # Function with Type_Safe return
            return Schema__Test_User(user_id='USER-123', name='Test', age=25)

        signature = self.analyzer.analyze_function(test_function)
        signature = self.converter.enrich_signature_with_conversions(signature)
        wrapper   = self.wrapper.create_wrapper(test_function, signature)

        # Verify original return type is preserved
        assert hasattr(wrapper, '__original_return_type__')
        assert wrapper.__original_return_type__ is Schema__Test_User  # Original Type_Safe class

    def test__create_wrapper__no_metadata_when_no_conversions(self):  # Test that no metadata added for simple functions
        def simple_function(x: int) -> int:                           # No Type_Safe types
            return x * 2

        signature = self.analyzer.analyze_function(simple_function)
        signature = self.converter.enrich_signature_with_conversions(signature)
        wrapper   = self.wrapper.create_wrapper(simple_function, signature)

        # Should not have metadata for simple types
        assert not hasattr(wrapper, '__original_param_types__')       # No conversions needed

    def test__create_wrapper__multiple_type_safe_params(self):        # Test handling multiple Type_Safe parameters
        class Schema__Order(Type_Safe):
            order_id: Safe_Id

        def multi_param_function(user: Schema__Test_User, order: Schema__Order) -> dict:
            return {'user': user.user_id, 'order': order.order_id}

        signature = self.analyzer.analyze_function(multi_param_function)
        signature = self.converter.enrich_signature_with_conversions(signature)
        wrapper   = self.wrapper.create_wrapper(multi_param_function, signature)

        # All Type_Safe params should be preserved
        assert 'user'  in wrapper.__original_param_types__
        assert 'order' in wrapper.__original_param_types__
        assert wrapper.__original_param_types__['user']  is Schema__Test_User
        assert wrapper.__original_param_types__['order'] is Schema__Order

    def test__create_wrapper__mixed_param_types(self):                # Test mix of Type_Safe and primitive types
        def mixed_function(user: Schema__Test_User, count: int, active: bool) -> dict:
            return {'user': user.user_id, 'count': count, 'active': active}

        signature = self.analyzer.analyze_function(mixed_function)
        signature = self.converter.enrich_signature_with_conversions(signature)
        wrapper   = self.wrapper.create_wrapper(mixed_function, signature)

        # Only Type_Safe params should have metadata
        assert 'user' in wrapper.__original_param_types__
        assert wrapper.__original_param_types__['user'] is Schema__Test_User


    # ===========================================================================================
    # Tests for create_passthrough_wrapper - New functionality for preserving return types
    # ===========================================================================================

    def test__create_passthrough_wrapper__basic_functionality(self):                    # Test basic passthrough wrapper creation
        from starlette.responses import JSONResponse

        def endpoint(name: str) -> JSONResponse:
            return JSONResponse(content={"name": name})

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_passthrough_wrapper(endpoint, signature)

            assert wrapper is not endpoint                                              # New wrapper created
            assert hasattr(wrapper, '__annotations__')                                  # Has annotations
            assert 'return' in wrapper.__annotations__                                  # Return type preserved
            assert wrapper.__annotations__['return'] is JSONResponse                    # Correct return type

    def test__create_passthrough_wrapper__preserves_signature(self):                    # Test signature preservation
        from starlette.responses import HTMLResponse

        def endpoint(user_id: str, active: bool = True) -> HTMLResponse:
            return HTMLResponse(content=f"<p>User {user_id}</p>")

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_passthrough_wrapper(endpoint, signature)

            import inspect
            wrapper_sig  = inspect.signature(wrapper)
            original_sig = inspect.signature(endpoint)

            assert len(wrapper_sig.parameters)   == len(original_sig.parameters)       # Same number of params
            assert 'user_id' in wrapper_sig.parameters                                  # Parameters preserved
            assert 'active' in wrapper_sig.parameters
            assert wrapper_sig.parameters['active'].default is True                     # Defaults preserved

    def test__create_passthrough_wrapper__function_execution(self):                     # Test that wrapper correctly passes through execution
        from starlette.responses import PlainTextResponse

        call_count = []

        def endpoint(message: str) -> PlainTextResponse:
            call_count.append(1)
            return PlainTextResponse(content=f"Message: {message}")

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_passthrough_wrapper(endpoint, signature)
            result  = wrapper(message="test")

            assert len(call_count)     == 1                                             # Original function called
            assert type(result).__name__ == 'PlainTextResponse'                         # Returns correct type
            assert result.body           == b"Message: test"                            # Correct content

    def test__create_passthrough_wrapper__preserves_route_path(self):                   # Test route_path decorator preservation
        from starlette.responses import JSONResponse

        def endpoint() -> JSONResponse:
            return JSONResponse(content={"status": "ok"})

        endpoint.__route_path__ = "/custom/path"                                        # Simulate route_path decorator

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_passthrough_wrapper(endpoint, signature)

            assert hasattr(wrapper, '__route_path__')                                   # Route path preserved
            assert wrapper.__route_path__ == "/custom/path"                             # Correct path

    def test__create_passthrough_wrapper__preserves_original_return_type_metadata(self): # Test metadata preservation
        from starlette.responses import HTMLResponse

        def endpoint() -> HTMLResponse:
            return HTMLResponse(content="<h1>Test</h1>")

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_passthrough_wrapper(endpoint, signature)

            assert hasattr(wrapper, '__original_return_type__')                         # Metadata added
            assert wrapper.__original_return_type__ is HTMLResponse                     # Correct type stored

    def test__create_wrapper__uses_passthrough_for_response_types(self):                # Test that create_wrapper uses passthrough for Response types
        from starlette.responses import JSONResponse

        def endpoint(value: int) -> JSONResponse:
            return JSONResponse(content={"value": value})

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_wrapper(endpoint, signature)

            assert wrapper is not endpoint                                              # Wrapper created (not original)
            assert hasattr(wrapper, '__annotations__')                                  # Has annotations
            assert 'return' in wrapper.__annotations__                                  # Return type preserved
            assert wrapper.__annotations__['return'] is JSONResponse                    # Correct return type for OpenAPI

    def test__create_wrapper__passthrough_with_htmlresponse(self):                      # Test passthrough with HTMLResponse
        from starlette.responses import HTMLResponse

        def render_page(title: str, content: str) -> HTMLResponse:
            html = f"<html><head><title>{title}</title></head><body>{content}</body></html>"
            return HTMLResponse(content=html)

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(render_page)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_wrapper(render_page, signature)

            result = wrapper(title="Test Page", content="Hello World")

            assert type(result).__name__     == 'HTMLResponse'                          # Returns HTMLResponse
            assert b"Test Page" in result.body                                          # Content preserved
            assert b"Hello World" in result.body
            assert 'return' in wrapper.__annotations__                                  # Return annotation preserved
            assert wrapper.__annotations__['return'] is HTMLResponse

    def test__create_wrapper__passthrough_with_plaintextresponse(self):                 # Test passthrough with PlainTextResponse
        from starlette.responses import PlainTextResponse

        def generate_text(lines: int) -> PlainTextResponse:
            text = "\n".join([f"Line {i}" for i in range(lines)])
            return PlainTextResponse(content=text)

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(generate_text)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_wrapper(generate_text, signature)

            result = wrapper(lines=3)

            assert type(result).__name__ == 'PlainTextResponse'                         # Returns PlainTextResponse
            assert result.body           == b"Line 0\nLine 1\nLine 2"                   # Correct content
            assert wrapper.__annotations__['return'] is PlainTextResponse               # Return type preserved

    def test__create_wrapper__passthrough_with_fileresponse(self):                      # Test passthrough with FileResponse
        from starlette.responses import FileResponse
        import tempfile
        import os

        def serve_file() -> FileResponse:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write("Test file content")
                temp_path = f.name

            response = FileResponse(path=temp_path)
            os.unlink(temp_path)                                                        # Clean up immediately
            return response

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(serve_file)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_wrapper(serve_file, signature)

            assert hasattr(wrapper, '__annotations__')                                  # Has annotations
            assert 'return' in wrapper.__annotations__                                  # Return type preserved
            assert wrapper.__annotations__['return'] is FileResponse                    # Correct type for OpenAPI

    def test__create_wrapper__passthrough_preserves_kwargs(self):                       # Test that kwargs are properly passed through
        from starlette.responses import JSONResponse

        def endpoint(**kwargs) -> JSONResponse:
            return JSONResponse(content=kwargs)

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_wrapper(endpoint, signature)
            result  = wrapper(key1="value1", key2="value2", key3=123)

            assert type(result).__name__ == 'JSONResponse'                              # Returns JSONResponse
            content = result.body.decode()
            assert 'key1' in content                                                    # All kwargs passed through
            assert 'key2' in content
            assert 'key3' in content

    def test__create_wrapper__passthrough_preserves_args(self):                         # Test that positional args work with passthrough
        from starlette.responses import PlainTextResponse

        def endpoint(*args) -> PlainTextResponse:
            text = ", ".join(str(arg) for arg in args)
            return PlainTextResponse(content=text)

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_wrapper(endpoint, signature)
            result  = wrapper("arg1", "arg2", "arg3")

            assert type(result).__name__ == 'PlainTextResponse'                         # Returns PlainTextResponse
            assert result.body           == b"arg1, arg2, arg3"                         # All args passed through

    def test__create_wrapper__no_return_type_returns_original(self):                    # Test that functions without return type get original back
        def endpoint(value: int):                                                       # No return type annotation
            return {"value": value}

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_wrapper(endpoint, signature)

            assert wrapper is endpoint                                                  # Original returned (no wrapper needed)

    def test__create_wrapper__dict_return_type_creates_wrapper(self):               # Test that dict return type creates passthrough wrapper for OpenAPI
        def endpoint(name: str) -> dict:
            return {"name": name}

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_wrapper(endpoint, signature)

            assert wrapper is not endpoint                                          # Wrapper created to preserve return type
            assert 'return' in wrapper.__annotations__                              # Return type preserved for OpenAPI
            assert wrapper.__annotations__['return'] is dict                        # Correct return type

            # Verify it still works
            result = wrapper(name="test")
            assert result == {"name": "test"}

    def test__create_passthrough_wrapper__annotation_fallback(self):                    # Test fallback to __annotations__ when get_type_hints fails
        from starlette.responses import JSONResponse

        def endpoint() -> JSONResponse:
            return JSONResponse(content={"test": "data"})

        # Simulate scenario where get_type_hints might fail by removing module
        original_module = endpoint.__module__
        endpoint.__module__ = 'non.existent.module'

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            # Restore module for signature analysis
            endpoint.__module__ = original_module
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_passthrough_wrapper(endpoint, signature)

            assert hasattr(wrapper, '__annotations__')                                  # Still has annotations
            assert 'return' in wrapper.__annotations__                                  # Return type preserved via fallback

    def test__create_wrapper__multiple_response_types_in_same_class(self):              # Test mixing different Response types in methods
        from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse

        class API_Routes(Type_Safe):
            def get_html(self) -> HTMLResponse:
                return HTMLResponse(content="<h1>HTML</h1>")

            def get_json(self) -> JSONResponse:
                return JSONResponse(content={"type": "json"})

            def get_text(self) -> PlainTextResponse:
                return PlainTextResponse(content="plain text")

        routes = API_Routes()

        with self.analyzer as analyzer:
            for method_name, return_type in [('get_html', HTMLResponse),
                                             ('get_json', JSONResponse),
                                             ('get_text', PlainTextResponse)]:
                method    = getattr(routes, method_name)
                signature = analyzer.analyze_function(method)
                signature = self.converter.enrich_signature_with_conversions(signature)

                with self.wrapper as _:
                    wrapper = _.create_wrapper(method, signature)

                    assert wrapper is not method                                        # Wrapper created for each
                    assert 'return' in wrapper.__annotations__                          # Return type preserved
                    assert wrapper.__annotations__['return'] is return_type             # Correct type for each method

    def test__create_passthrough_wrapper__empty_signature(self):                        # Test passthrough with no parameters
        from starlette.responses import JSONResponse

        def endpoint() -> JSONResponse:
            return JSONResponse(content={"message": "no params"})

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_passthrough_wrapper(endpoint, signature)
            result  = wrapper()

            assert type(result).__name__ == 'JSONResponse'                              # Works with no params
            assert b"no params" in result.body                                          # Content correct

    def test__create_wrapper__openapi_schema_compatibility(self):                       # Test that wrapper annotations are compatible with OpenAPI
        from starlette.responses import JSONResponse
        from typing import get_type_hints

        def endpoint(user_id: str, include_details: bool = False) -> JSONResponse:
            return JSONResponse(content={"user_id": user_id, "details": include_details})

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_wrapper(endpoint, signature)

            # Verify wrapper has everything OpenAPI needs
            assert hasattr(wrapper, '__signature__')                                    # FastAPI needs signature
            assert hasattr(wrapper, '__annotations__')                                  # FastAPI needs annotations
            assert 'return' in wrapper.__annotations__                                  # Return type critical for OpenAPI

            # Verify get_type_hints works (used by FastAPI internally)
            type_hints = get_type_hints(wrapper)
            assert 'return' in type_hints                                               # FastAPI can extract return type
            assert type_hints['return'] is JSONResponse                                 # Correct type for schema generation





    def test__create_wrapper__request_and_response_schemas_both_preserved(self):    # Test that both request and response Type_Safe schemas are preserved
        """
        CRITICAL TEST: Validates the bug fix - ensures both request and response
        Type_Safe classes are properly converted and their schemas will appear in OpenAPI.
        This is the exact scenario from Routes__Dict.to__text__nodes()
        """

        def process_data(self, request: Schema__Request) -> Schema__Response:
            return Schema__Response(output_data = Safe_Str("processed")  ,
                                    item_count  = Safe_Int(5)            )

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(process_data)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_wrapper(process_data, signature)

            # Verify wrapper was created (not original returned)
            assert wrapper is not process_data                                          # Wrapper created due to Type_Safe conversions

            # Verify request parameter is converted to BaseModel

            wrapper_sig = inspect.signature(wrapper)
            request_param = wrapper_sig.parameters['request']
            assert request_param.annotation is not Schema__Request                     # Converted from Type_Safe
            assert issubclass(request_param.annotation, BaseModel)


            # Verify response return type is converted to BaseModel
            annotations = wrapper.__annotations__
            assert 'return' in annotations                                             # Has return annotation
            assert annotations['return'] is not Schema__Response                       # Converted from Type_Safe
            assert issubclass(annotations['return'], BaseModel)                        # Converted to BaseModel

            # Verify original types are preserved in metadata for introspection
            assert hasattr(wrapper, '__original_return_type__')                        # Original return type stored
            assert wrapper.__original_return_type__ is Schema__Response                # Original Type_Safe class

            assert hasattr(wrapper, '__original_param_types__')                        # Original param types stored
            assert 'request' in wrapper.__original_param_types__
            assert wrapper.__original_param_types__['request'] is Schema__Request     # Original Type_Safe class

            assert annotations['return'].__name__        == 'Schema__Response__BaseModel'
            assert full_type_name(annotations['return']) == 'osbot_fast_api.api.transformers.Type_Safe__To__BaseModel.Schema__Response__BaseModel'

    def test__create_wrapper__openapi_readiness_both_request_and_response(self):     # Test OpenAPI schema generation readiness
        """
        Validates that the wrapper has everything FastAPI needs to generate
        OpenAPI schemas for both request and response Type_Safe classes.
        """
        class Schema__Input(Type_Safe):
            name  : Safe_Str
            value : Safe_Int

        class Schema__Output(Type_Safe):
            result  : Safe_Str
            success : bool

        def endpoint(input_data: Schema__Input) -> Schema__Output:
            return Schema__Output(result=Safe_Str("ok"), success=True)

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        with self.wrapper as _:
            wrapper = _.create_wrapper(endpoint, signature)

            # FastAPI requires these attributes for OpenAPI generation
            assert hasattr(wrapper, '__signature__')                                   # Required: Function signature
            assert hasattr(wrapper, '__annotations__')                                 # Required: Type annotations

            # Verify FastAPI can extract type information
            from typing import get_type_hints
            type_hints = get_type_hints(wrapper)

            assert 'input_data' in type_hints                                          # Request param extractable
            assert 'return' in type_hints                                              # Response type extractable

            # Both should be BaseModel classes (not original Type_Safe)
            input_type = type_hints['input_data']
            return_type = type_hints['return']

            assert issubclass(input_type, BaseModel)                                   # Request converted to BaseModel
            assert issubclass(return_type, BaseModel)                                  # Response converted to BaseModel

            # Verify the BaseModel classes have the expected fields
            assert hasattr(input_type, 'model_fields')                                 # Pydantic BaseModel feature
            assert hasattr(return_type, 'model_fields')                                # Pydantic BaseModel feature

            # These BaseModel classes will generate schemas in openapi.json
            assert 'name' in input_type.model_fields                                   # Request field present
            assert 'value' in input_type.model_fields
            assert 'result' in return_type.model_fields                                # Response field present
            assert 'success' in return_type.model_fields

    def test__create_wrapper__multiple_endpoints_all_schemas_preserved(self):        # Test multiple endpoints with different schemas
        """
        Simulates a real API with multiple endpoints, each with different
        request/response schemas. Validates all schemas are properly converted.
        """
        class Schema__User__Request(Type_Safe):
            username : Safe_Str
            email    : Safe_Str__Email

        class Schema__User__Response(Type_Safe):
            user_id  : Safe_Id
            username : Safe_Str

        class Schema__Product__Request(Type_Safe):
            name  : Safe_Str
            price : Safe_Int

        class Schema__Product__Response(Type_Safe):
            product_id : Safe_Id
            name       : Safe_Str
            price      : Safe_Int

        def create_user(user_data: Schema__User__Request) -> Schema__User__Response:
            return Schema__User__Response(user_id=Safe_Id("USER-1"), username=user_data.username)

        def create_product(product_data: Schema__Product__Request) -> Schema__Product__Response:
            return Schema__Product__Response(product_id=Safe_Id("PROD-1"), name=product_data.name, price=product_data.price)

        endpoints = [
            (create_user, Schema__User__Request, Schema__User__Response),
            (create_product, Schema__Product__Request, Schema__Product__Response)
        ]

        with self.analyzer as analyzer:
            for endpoint_func, expected_request_type, expected_response_type in endpoints:
                signature = analyzer.analyze_function(endpoint_func)
                signature = self.converter.enrich_signature_with_conversions(signature)

                with self.wrapper as _:
                    wrapper = _.create_wrapper(endpoint_func, signature)

                    # Verify wrapper created
                    assert wrapper is not endpoint_func                                # Wrapper created

                    # Verify original types preserved in metadata
                    assert wrapper.__original_return_type__ is expected_response_type  # Response type preserved

                    param_name = str(list(signature.parameters)[0].name)                    # Get first param name
                    assert wrapper.__original_param_types__[param_name] is expected_request_type  # Request type preserved

                    # Verify both converted to BaseModel for OpenAPI
                    from typing import get_type_hints
                    type_hints = get_type_hints(wrapper)

                    assert issubclass(type_hints[param_name], BaseModel)               # Request is BaseModel
                    assert issubclass(type_hints['return'  ], BaseModel)                # Response is BaseModel


class Schema__Request(Type_Safe):
    input_data : Safe_Str
    max_items  : Safe_Int

class Schema__Response(Type_Safe):
    output_data : Safe_Str
    item_count  : Safe_Int

class Schema__Test_User(Type_Safe):                                  # Test schema for wrapper tests
    user_id : Safe_Id
    name    : str
    age     : int
