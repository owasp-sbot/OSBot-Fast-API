from unittest                                                                   import TestCase
from fastapi                                                                    import HTTPException

from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes
from osbot_fast_api.api.schemas.Schema__Fast_API__Config import Schema__Fast_API__Config
from osbot_fast_api.client.schemas.Schema__Endpoint__Param                      import Schema__Endpoint__Param
from osbot_fast_api.api.schemas.Schema__Fast_API__Tag__Classes_And_Routes       import Schema__Fast_API__Tag__Classes_And_Routes
from osbot_fast_api.api.schemas.Schema__Fast_API__Tags__Classes_And_Routes      import Schema__Fast__API_Tags__Classes_And_Routes
from osbot_fast_api.api.schemas.routes.Schema__Fast_API__Route                  import Schema__Fast_API__Route
from osbot_fast_api.client.Fast_API__Contract__Extractor                        import Fast_API__Contract__Extractor
from osbot_fast_api.utils.Version                                               import version__osbot_fast_api
from osbot_utils.type_safe.primitives.domains.http.enums.Enum__Http__Method     import Enum__Http__Method
from osbot_utils.testing.__                                                     import __, __SKIP__
from osbot_utils.utils.Objects                                                  import base_classes
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_fast_api.api.Fast_API                                                import Fast_API
from osbot_fast_api.client.schemas.Schema__Endpoint__Contract                   import Schema__Endpoint__Contract
from osbot_fast_api.client.schemas.Schema__Service__Contract                    import Schema__Service__Contract
from osbot_fast_api.client.testing.Test__Fast_API__With_Routes                  import Test__Fast_API__With_Routes

class test_Fast_API__Contract__Extractor(TestCase):

    @classmethod
    def setUpClass(cls):                                                            # ONE-TIME expensive setup
        cls.fast_api  = Test__Fast_API__With_Routes().setup()
        cls.extractor = Fast_API__Contract__Extractor(fast_api=cls.fast_api)

    def test__init__(self):                                                         # Test Type_Safe inheritance and initialization
        with Fast_API__Contract__Extractor() as _:
            assert type(_) is Fast_API__Contract__Extractor
            assert base_classes(_) == [Type_Safe, object]
            assert type(_.fast_api) is Fast_API                                     # Type_Safe will create a default instance of Fast_API

        with Fast_API__Contract__Extractor(fast_api=self.fast_api) as _:
            assert type(_.fast_api) is Test__Fast_API__With_Routes
            assert _.fast_api       is self.fast_api                                # Same instance

    def test_extract_contract__check(self):                                                # Test contract extraction from Fast_API
        with self.extractor as _:
            contract = _.extract_contract()

            assert type(contract)             is Schema__Service__Contract

            assert contract.service_name      == 'Test__Fast_API__With_Routes'
            assert contract.version           == version__osbot_fast_api
            assert contract.base_path         == '/'
            assert contract.service_version   == version__osbot_fast_api
            assert len(contract.modules)      >= 2                                  # At least users and products modules
            assert len(contract.endpoints)    >= 5                                  # At least 5 endpoints total

            # Verify contract structure with .obj()
            contract_obj = contract.obj()
            assert contract_obj.service_name    == 'Test__Fast_API__With_Routes'
            assert contract_obj.version         == version__osbot_fast_api
            assert type(contract_obj.modules)   is list
            assert type(contract_obj.endpoints) is list

    def test__organize_routes_by_module(self):                                      # Test route organization by module
        with self.extractor as _:
            all_routes       = _.fast_api__all_routes()
            routes_by_module = _.organize_routes__by_tag(all_routes)
            assert type(routes_by_module) is Schema__Fast__API_Tags__Classes_And_Routes
            assert 'users' in routes_by_module.by_tag                         # Users module detected
            assert 'products' in routes_by_module.by_tag                      # Products module detected

            # Check users module structure
            users_module = routes_by_module.by_tag['users']
            assert type(users_module) is Schema__Fast_API__Tag__Classes_And_Routes
            assert 'Routes__Users'    in users_module.classes

            assert len(users_module.routes) == 2                                 # get and create

    def test__extract_endpoint_contracts(self):                                      # Test endpoint contract extraction
        with self.extractor as _:
            route_data = Schema__Fast_API__Route.from_json({ 'method_name' : 'get_user__user_id'  ,         # Create sample route data
                                                             'http_path'   : '/users/{user_id}'   ,
                                                             'http_methods': ['GET']              })

            contracts = _.extract_endpoint_contracts(route_data)
            assert len(contracts) == 1
            contract = contracts[0]

            assert type(contract) is Schema__Endpoint__Contract
            assert contract.obj() == __(request_schema  = None                     ,
                                        response_schema = None                     ,
                                        operation_id    = 'get__get_user__user_id' ,
                                        method          = 'GET'                    ,
                                        path_pattern    = '/users/{user_id}'       ,
                                        route_class     = 'Routes__Users'          ,
                                        route_method    = 'get_user__user_id'      ,
                                        route_module    = ''                       ,
                                        path_params     = []                       ,
                                        query_params    = []                       ,
                                        header_params   = []                       ,
                                        error_codes     = []                       )

    def test__enhance_with_signature(self):                                         # Test signature enhancement
        with self.extractor as _:
            endpoint = Schema__Endpoint__Contract(operation_id = 'test_method'                                   ,
                                                  path_pattern = '/test/{id}'                                    ,
                                                  method       = Enum__Http__Method.GET                          ,
                                                  query_params = [Schema__Endpoint__Param(name      = 'name'    ,
                                                                                          required  = False     ,
                                                                                          default   = 'default' )])

            # Create test function with signature
            def test_func(self, id: int, name: str = "default"):
                pass

            _._enhance_with_signature(endpoint, test_func)

            # Check path param was enhanced with type
            assert len(endpoint.path_params) == 0                                   # Not added by signature

            # Check query params were added
            assert len(endpoint.query_params) >= 1
            query_param_names = [p.name for p in endpoint.query_params]
            assert 'name' in query_param_names                                      # Added as query param

            # Find the name param and check its properties
            name_param = next(p for p in endpoint.query_params if p.name == 'name')
            assert name_param.required == False                                     # Has default
            assert name_param.default  == "default"                                 # Default value captured

    def test__is_type_safe_class(self):                                            # Test Type_Safe class detection
        with self.extractor as _:
            # Test with Type_Safe class
            class TestSchema(Type_Safe):
                name: str

            assert _._is_type_safe_class(TestSchema) is True

            # Test with regular class
            class RegularClass:
                pass

            assert _._is_type_safe_class(RegularClass) is False

            # Test with None
            assert _._is_type_safe_class(None) is False

            # Test with non-class
            assert _._is_type_safe_class("string") is False
            assert _._is_type_safe_class(123)      is False

    def test__type_to_string(self):                                                # Test type hint to string conversion
        with self.extractor as _:
            assert _._type_to_string(None)     == 'None'
            assert _._type_to_string(str)      == 'str'
            assert _._type_to_string(int)      == 'int'
            assert _._type_to_string(dict)     == 'dict'

            # Test with typing module types
            from typing import List, Dict, Optional
            type_str = _._type_to_string(List[str])
            assert 'List' in type_str or 'list' in type_str

            type_str = _._type_to_string(Dict[str, int])
            assert 'Dict' in type_str or 'dict' in type_str

    def test_extract_contract__comprehensive(self):                                 # Test comprehensive contract extraction
        with self.extractor as _:
            contract = _.extract_contract()

            # Find users module
            users_module = next((m for m in contract.modules if m.module_name == 'users'), None)
            assert users_module is not None
            assert len(users_module.endpoints) >= 2
            assert 'Routes__Users' in users_module.route_classes

            # Find a specific endpoint
            get_user_endpoint = next((e for e in contract.endpoints if 'get_user' in e.operation_id), None)
            assert get_user_endpoint is not None
            assert get_user_endpoint.method == Enum__Http__Method.GET
            assert '{user_id}' in get_user_endpoint.path_pattern

            # Test serialization round-trip
            json_data = contract.json()
            restored  = Schema__Service__Contract.from_json(json_data)
            assert restored.service_name == contract.service_name
            assert len(restored.endpoints) == len(contract.endpoints)

    def test__bug__enhance_with_ast_analysis(self):                                      # Test AST analysis for error codes
        with self.extractor as _:
            endpoint = Schema__Endpoint__Contract(operation_id = 'test_method'         ,
                                                  path_pattern = '/test'               ,
                                                  method       = Enum__Http__Method.GET)

            def test_func_with_error():                                                 # Function with HTTPException
                if True:
                    raise HTTPException(status_code=404, detail="Not found")            # we should had detected this
                return {}

            _._enhance_with_ast_analysis(endpoint, test_func_with_error)

            # Note: AST analysis is basic in current implementation
            # It may or may not detect the 404 depending on implementation
            # This test documents current behavior

            assert 404 not in endpoint.error_codes                                      # BUG

    def test_extract_contract__with_empty_fast_api(self):                          # Test with empty Fast_API
        with Fast_API() as empty_api:
            empty_api.setup()
            extractor = Fast_API__Contract__Extractor(fast_api=empty_api)
            contract  = extractor.extract_contract()

            assert type(contract)        is Schema__Service__Contract
            assert contract.service_name == 'Fast_API'                              # Default name
            assert len(contract.modules) >= 0                                       # May have default routes

            assert contract.service_version == version__osbot_fast_api
            assert contract.client_version  == ''


            assert contract.obj() == __(service_name    = 'Fast_API'           ,
                                        version          = __SKIP__            ,     # Version varies
                                        base_path        = '/'                 ,
                                        service_version  = __SKIP__            ,     # Version varies
                                        modules          = __SKIP__            ,     # Modules vary
                                        endpoints        = __SKIP__            ,     # Endpoints vary
                                        generated_at     = __SKIP__            ,
                                        client_version   = __SKIP__            )




    def test_extract_contract__check_obj(self):                                        # Check the full object extracted from current routes
            with self.extractor as _:
                contract = _.extract_contract()
                assert contract.obj() == __(   service_name='Test__Fast_API__With_Routes',
                                               version=version__osbot_fast_api,
                                               base_path='/',
                                               modules=[ __(module_name='root',
                                                            route_classes=['Fast_API'],
                                                            endpoints=[ __(request_schema=None,
                                                                           response_schema=None,
                                                                           operation_id='get__redirect_to_docs',
                                                                           method='GET',
                                                                           path_pattern='/',
                                                                           route_class='Fast_API',
                                                                           route_method='redirect_to_docs',
                                                                           route_module='root',
                                                                           path_params=[],
                                                                           query_params=[],
                                                                           header_params=[],
                                                                           error_codes=[])]),
                                                         __(module_name='config',
                                                            route_classes=['Routes__Config'],
                                                            endpoints=[ __(request_schema=None,
                                                                           response_schema=None,
                                                                           operation_id='get__info',
                                                                           method='GET',
                                                                           path_pattern='/config/info',
                                                                           route_class='Routes__Config',
                                                                           route_method='info',
                                                                           route_module='config',
                                                                           path_params=[],
                                                                           query_params=[],
                                                                           header_params=[],
                                                                           error_codes=[]),
                                                                        __(request_schema=None,
                                                                           response_schema=None,
                                                                           operation_id='get__status',
                                                                           method='GET',
                                                                           path_pattern='/config/status',
                                                                           route_class='Routes__Config',
                                                                           route_method='status',
                                                                           route_module='config',
                                                                           path_params=[],
                                                                           query_params=[],
                                                                           header_params=[],
                                                                           error_codes=[]),
                                                                        __(request_schema=None,
                                                                           response_schema=None,
                                                                           operation_id='get__version',
                                                                           method='GET',
                                                                           path_pattern='/config/version',
                                                                           route_class='Routes__Config',
                                                                           route_method='version',
                                                                           route_module='config',
                                                                           path_params=[],
                                                                           query_params=[],
                                                                           header_params=[],
                                                                           error_codes=[]),
                                                                        __(request_schema=None,
                                                                           response_schema=None,
                                                                           operation_id='get__openapi_python',
                                                                           method='GET',
                                                                           path_pattern='/config/openapi.py',
                                                                           route_class='Routes__Config',
                                                                           route_method='openapi_python',
                                                                           route_module='config',
                                                                           path_params=[],
                                                                           query_params=[],
                                                                           header_params=[],
                                                                           error_codes=[])]),
                                                         __(module_name='auth',
                                                            route_classes=['Routes__Set_Cookie'],
                                                            endpoints=[ __(request_schema=None,
                                                                           response_schema=None,
                                                                           operation_id='get__set_cookie_form',
                                                                           method='GET',
                                                                           path_pattern='/auth/set-cookie-form',
                                                                           route_class='Routes__Set_Cookie',
                                                                           route_method='set_cookie_form',
                                                                           route_module='auth',
                                                                           path_params=[],
                                                                           query_params=[],
                                                                           header_params=[],
                                                                           error_codes=[]),
                                                                        __(request_schema=None,
                                                                           response_schema=None,
                                                                           operation_id='post__set_auth_cookie',
                                                                           method='POST',
                                                                           path_pattern='/auth/set-auth-cookie',
                                                                           route_class='Routes__Set_Cookie',
                                                                           route_method='set_auth_cookie',
                                                                           route_module='auth',
                                                                           path_params=[],
                                                                           query_params=[],
                                                                           header_params=[],
                                                                           error_codes=[])]),
                                                         __(module_name='users',
                                                            route_classes=['Routes__Users'],
                                                            endpoints=[ __(request_schema=None,
                                                                           response_schema=None,
                                                                           operation_id='get__get_user__user_id',
                                                                           method='GET',
                                                                           path_pattern='/users/get-user/{user_id}',
                                                                           route_class='Routes__Users',
                                                                           route_method='get_user__user_id',
                                                                           route_module='users',
                                                                           path_params=[ __(default=None,
                                                                                            location=None,
                                                                                            description=None,
                                                                                            required=True,
                                                                                            name='user_id',
                                                                                            param_type='builtins.int')],
                                                                           query_params=[],
                                                                           header_params=[],
                                                                           error_codes=[]),
                                                                        __(request_schema=None,
                                                                           response_schema=None,
                                                                           operation_id='post__create_user',
                                                                           method='POST',
                                                                           path_pattern='/users/create-user',
                                                                           route_class='Routes__Users',
                                                                           route_method='create_user',
                                                                           route_module='users',
                                                                           path_params=[],
                                                                           query_params=[],
                                                                           header_params=[],
                                                                           error_codes=[])]),
                                                         __(module_name='products',
                                                            route_classes=['Routes__Products'],
                                                            endpoints=[ __(request_schema=None,
                                                                           response_schema=None,
                                                                           operation_id='get__get_product__product_id',
                                                                           method='GET',
                                                                           path_pattern='/products/get-product/{product_id}',
                                                                           route_class='Routes__Products',
                                                                           route_method='get_product__product_id',
                                                                           route_module='products',
                                                                           path_params=[ __(default=None,
                                                                                            location=None,
                                                                                            description=None,
                                                                                            required=True,
                                                                                            name='product_id',
                                                                                            param_type='builtins.int')],
                                                                           query_params=[],
                                                                           header_params=[],
                                                                           error_codes=[]),
                                                                        __(request_schema=None,
                                                                           response_schema=None,
                                                                           operation_id='get__list_products',
                                                                           method='GET',
                                                                           path_pattern='/products/list-products',
                                                                           route_class='Routes__Products',
                                                                           route_method='list_products',
                                                                           route_module='products',
                                                                           path_params=[],
                                                                           query_params=[ __(default=10,
                                                                                             location=None,
                                                                                             description=None,
                                                                                             required=False,
                                                                                             name='limit',
                                                                                             param_type='builtins.int'),
                                                                                          __(default=0,
                                                                                             location=None,
                                                                                             description=None,
                                                                                             required=False,
                                                                                             name='offset',
                                                                                             param_type='builtins.int')],
                                                                           header_params=[],
                                                                           error_codes=[]),
                                                                        __(request_schema=None,
                                                                           response_schema=None,
                                                                           operation_id='put__update_product__product_id',
                                                                           method='PUT',
                                                                           path_pattern='/products/update-product/{product_id}',
                                                                           route_class='Routes__Products',
                                                                           route_method='update_product__product_id',
                                                                           route_module='products',
                                                                           path_params=[ __(default=None,
                                                                                            location=None,
                                                                                            description=None,
                                                                                            required=True,
                                                                                            name='product_id',
                                                                                            param_type='builtins.int')],
                                                                           query_params=[],
                                                                           header_params=[],
                                                                           error_codes=[])])],
                                               endpoints=[ __(request_schema=None,
                                                              response_schema=None,
                                                              operation_id='get__redirect_to_docs',
                                                              method='GET',
                                                              path_pattern='/',
                                                              route_class='Fast_API',
                                                              route_method='redirect_to_docs',
                                                              route_module='root',
                                                              path_params=[],
                                                              query_params=[],
                                                              header_params=[],
                                                              error_codes=[]),
                                                           __(request_schema=None,
                                                              response_schema=None,
                                                              operation_id='get__info',
                                                              method='GET',
                                                              path_pattern='/config/info',
                                                              route_class='Routes__Config',
                                                              route_method='info',
                                                              route_module='config',
                                                              path_params=[],
                                                              query_params=[],
                                                              header_params=[],
                                                              error_codes=[]),
                                                           __(request_schema=None,
                                                              response_schema=None,
                                                              operation_id='get__status',
                                                              method='GET',
                                                              path_pattern='/config/status',
                                                              route_class='Routes__Config',
                                                              route_method='status',
                                                              route_module='config',
                                                              path_params=[],
                                                              query_params=[],
                                                              header_params=[],
                                                              error_codes=[]),
                                                           __(request_schema=None,
                                                              response_schema=None,
                                                              operation_id='get__version',
                                                              method='GET',
                                                              path_pattern='/config/version',
                                                              route_class='Routes__Config',
                                                              route_method='version',
                                                              route_module='config',
                                                              path_params=[],
                                                              query_params=[],
                                                              header_params=[],
                                                              error_codes=[]),
                                                           __(request_schema=None,
                                                              response_schema=None,
                                                              operation_id='get__openapi_python',
                                                              method='GET',
                                                              path_pattern='/config/openapi.py',
                                                              route_class='Routes__Config',
                                                              route_method='openapi_python',
                                                              route_module='config',
                                                              path_params=[],
                                                              query_params=[],
                                                              header_params=[],
                                                              error_codes=[]),
                                                           __(request_schema=None,
                                                              response_schema=None,
                                                              operation_id='get__set_cookie_form',
                                                              method='GET',
                                                              path_pattern='/auth/set-cookie-form',
                                                              route_class='Routes__Set_Cookie',
                                                              route_method='set_cookie_form',
                                                              route_module='auth',
                                                              path_params=[],
                                                              query_params=[],
                                                              header_params=[],
                                                              error_codes=[]),
                                                           __(request_schema=None,
                                                              response_schema=None,
                                                              operation_id='post__set_auth_cookie',
                                                              method='POST',
                                                              path_pattern='/auth/set-auth-cookie',
                                                              route_class='Routes__Set_Cookie',
                                                              route_method='set_auth_cookie',
                                                              route_module='auth',
                                                              path_params=[],
                                                              query_params=[],
                                                              header_params=[],
                                                              error_codes=[]),
                                                           __(request_schema=None,
                                                              response_schema=None,
                                                              operation_id='get__get_user__user_id',
                                                              method='GET',
                                                              path_pattern='/users/get-user/{user_id}',
                                                              route_class='Routes__Users',
                                                              route_method='get_user__user_id',
                                                              route_module='users',
                                                              path_params=[ __(default=None,
                                                                               location=None,
                                                                               description=None,
                                                                               required=True,
                                                                               name='user_id',
                                                                               param_type='builtins.int')],
                                                              query_params=[],
                                                              header_params=[],
                                                              error_codes=[]),
                                                           __(request_schema=None,
                                                              response_schema=None,
                                                              operation_id='post__create_user',
                                                              method='POST',
                                                              path_pattern='/users/create-user',
                                                              route_class='Routes__Users',
                                                              route_method='create_user',
                                                              route_module='users',
                                                              path_params=[],
                                                              query_params=[],
                                                              header_params=[],
                                                              error_codes=[]),
                                                           __(request_schema=None,
                                                              response_schema=None,
                                                              operation_id='get__get_product__product_id',
                                                              method='GET',
                                                              path_pattern='/products/get-product/{product_id}',
                                                              route_class='Routes__Products',
                                                              route_method='get_product__product_id',
                                                              route_module='products',
                                                              path_params=[ __(default=None,
                                                                               location=None,
                                                                               description=None,
                                                                               required=True,
                                                                               name='product_id',
                                                                               param_type='builtins.int')],
                                                              query_params=[],
                                                              header_params=[],
                                                              error_codes=[]),
                                                           __(request_schema=None,
                                                              response_schema=None,
                                                              operation_id='get__list_products',
                                                              method='GET',
                                                              path_pattern='/products/list-products',
                                                              route_class='Routes__Products',
                                                              route_method='list_products',
                                                              route_module='products',
                                                              path_params=[],
                                                              query_params=[ __(default=10,
                                                                                location=None,
                                                                                description=None,
                                                                                required=False,
                                                                                name='limit',
                                                                                param_type='builtins.int'),
                                                                             __(default=0,
                                                                                location=None,
                                                                                description=None,
                                                                                required=False,
                                                                                name='offset',
                                                                                param_type='builtins.int')],
                                                              header_params=[],
                                                              error_codes=[]),
                                                           __(request_schema=None,
                                                              response_schema=None,
                                                              operation_id='put__update_product__product_id',
                                                              method='PUT',
                                                              path_pattern='/products/update-product/{product_id}',
                                                              route_class='Routes__Products',
                                                              route_method='update_product__product_id',
                                                              route_module='products',
                                                              path_params=[ __(default=None,
                                                                               location=None,
                                                                               description=None,
                                                                               required=True,
                                                                               name='product_id',
                                                                               param_type='builtins.int')],
                                                              query_params=[],
                                                              header_params=[],
                                                              error_codes=[])],
                                               generated_at=__SKIP__,
                                               service_version=version__osbot_fast_api,
                                               client_version='')
