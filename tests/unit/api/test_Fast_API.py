import re
import pytest
from unittest.mock                                                              import MagicMock
from unittest                                                                   import TestCase
from fastapi                                                                    import FastAPI, HTTPException
from fastapi.exceptions                                                         import RequestValidationError
from osbot_fast_api.schemas.Schema__Fast_API__Config                            import Schema__Fast_API__Config
from osbot_utils.testing.Temp_Folder                                            import Temp_Folder
from osbot_utils.testing.Temp_Env_Vars                                          import Temp_Env_Vars
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Version import Safe_Str__Version
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text    import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid           import Random_Guid
from osbot_utils.utils.Files                                                    import parent_folder
from osbot_utils.utils.Objects                                                  import base_classes
from osbot_utils.utils.Threads                                                  import invoke_async
from starlette.requests                                                         import Request
from starlette.responses                                                        import JSONResponse
from starlette.testclient                                                       import TestClient
from osbot_fast_api.api.Fast_API                                                import Fast_API
from osbot_fast_api.schemas.safe_str.Safe_Str__Fast_API__Name                   import Safe_Str__Fast_API__Name
from osbot_fast_api.schemas.safe_str.Safe_Str__Fast_API__Route__Prefix          import Safe_Str__Fast_API__Route__Prefix
from osbot_fast_api.schemas.consts.consts__Fast_API                             import EXPECTED_ROUTES_PATHS, EXPECTED_ROUTES_METHODS, EXPECTED_DEFAULT_ROUTES, ROUTES__CONFIG, ROUTES__STATIC_DOCS, FAST_API_DEFAULT_ROUTES, ENV_VAR__FAST_API__AUTH__API_KEY__NAME, ENV_VAR__FAST_API__AUTH__API_KEY__VALUE
from osbot_fast_api.utils.Fast_API_Utils                                        import Fast_API_Utils
from osbot_fast_api.utils.Version                                               import version__osbot_fast_api
from tests.unit.fast_api__for_tests                                             import fast_api, fast_api_client


class test_Fast_API(TestCase):

    def setUp(self):
        self.fast_api = fast_api        # Fast_API().setup()
        self.client   = fast_api_client # self.fast_api.client()

    def test__init__(self):
        assert type(self.fast_api.app()) is FastAPI

    @pytest.mark.skip(reason="started failing in GH Actions")  # see why and fix side effects or running this test
    def test_add_flask_app(self):
        flask = pytest.importorskip("flask", reason="Flask is not installed")       # noqa
        from flask import Flask                                                     # noqa
        path      = '/flask-app'
        flask_app = Flask(__name__)

        @flask_app.route('/flask-route')
        def hello_flask():
            return "Hello from Flask!"

        with self.fast_api as _:
            _.add_flask_app(path, flask_app)
            assert _.routes_paths(expand_mounts=True) == EXPECTED_ROUTES_PATHS + ['/flask-app']
            assert _.client().get('/flask-app/flask-route').text == 'Hello from Flask!'
            assert _.route_remove('/flask-app') is True
            assert _.route_remove('/flask-app') is False
            assert _.routes_paths(expand_mounts=True) == EXPECTED_ROUTES_PATHS

    def test_app(self):
        app = self.fast_api.app()
        assert type(app) == FastAPI
        assert app.openapi_version      == '3.1.0'
        assert app.debug                is False
        #assert app.docs_url             == '/docs'
        assert app.dependency_overrides == {}
        assert app.openapi_url          == '/openapi.json'
        assert app.title                == 'Fast_API'
        assert app.version              == version__osbot_fast_api

        assert self.fast_api.config.enable_cors is False

    def test_client(self):
        assert type(self.client) is TestClient

    def test_fast_api_utils(self):
        fast_api_utils = self.fast_api.fast_api_utils()
        assert type(fast_api_utils)    is Fast_API_Utils
        assert fast_api_utils.app      == self.fast_api.app()

    def test_path_static_folder(self):
        assert self.fast_api.path_static_folder() is None

    def test_route__root(self):
        response = self.client.get('/', follow_redirects=False)
        assert response.status_code             == 307
        assert response.headers.get('location') == '/docs'
        fast_api_request_id = response.headers.get('fast-api-request-id')
        assert dict(response.headers) == {'content-length': '0', 'location': '/docs', 'fast-api-request-id': fast_api_request_id}

    def test_routes(self):
        expected_routes = FAST_API_DEFAULT_ROUTES + ROUTES__CONFIG + ROUTES__STATIC_DOCS
        routes          = self.fast_api.routes(include_default=True)
        assert routes == expected_routes

    def test_routes_methods(self):
        routes_methods         = self.fast_api.routes_methods()
        assert routes_methods == EXPECTED_ROUTES_METHODS

    def test_routes_paths(self):
        assert self.fast_api.routes_paths(                     ) == sorted(EXPECTED_ROUTES_PATHS)
        assert self.fast_api.routes_paths(include_default=False) == sorted(EXPECTED_ROUTES_PATHS)
        assert self.fast_api.routes_paths(include_default=True ) == sorted(EXPECTED_ROUTES_PATHS + EXPECTED_DEFAULT_ROUTES)

    def test_setup_routes(self):
        assert self.fast_api.setup_routes() == self.fast_api

    def test_user_middleware(self):
        assert self.fast_api.user_middlewares() == [{'function_name': None, 'params': {}, 'type': 'Middleware__Request_ID'       },
                                                    {'function_name': None, 'params': {}, 'type': 'Middleware__Detect_Disconnect'}]

    def test__verify__title_description_version(self):
        app = self.fast_api.app()
        assert type(app) is FastAPI
        assert app.title       == 'Fast_API'
        assert app.version     == version__osbot_fast_api
        assert app.description == ''

        kwargs = dict(name        = 'An Fast API !!',
                      version     = 'v0.1.0'        ,
                      description = 'now with more available charts to talk about Fast API !! @£$%^&*()')
        config = Schema__Fast_API__Config(**kwargs)

        with Fast_API(config=config) as _:
            assert _.config.name              == 'An Fast API __'                                                         # note the chars sanitization
            assert _.config.version           ==  'v0.1.0'
            assert _.config.description       == 'now with more available charts to talk about Fast API __ ______*()'    # note the chars sanitization

            assert type(_.config.name       ) is Safe_Str__Fast_API__Name
            assert type(_.config.version    ) is Safe_Str__Version
            assert type(_.config.description) is Safe_Str__Text

            app = _.app()
            assert type(app) is FastAPI
            assert app.title         == Safe_Str__Fast_API__Name('An Fast API __')
            assert app.version       == Safe_Str__Version        ('v0.1.0')
            assert app.description   == Safe_Str__Text('now with more available charts to talk about Fast API __ ______*()')

        error_message = 'in Safe_Str__Version, value does not match required pattern: ^v(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})$'
        with pytest.raises(ValueError, match=re.escape(error_message)):
            Schema__Fast_API__Config(version="0.1.1")                                       # confirm validation provided by Safe_Str__Version




    # Core initialization and Type_Safe inheritance tests

    def test__init__with_type_safety(self):                                        # Test Type_Safe inheritance and auto-initialization
        with Fast_API() as _:
            assert type(_)         is Fast_API
            assert base_classes(_) == [Type_Safe, object]                          # Verify Type_Safe inheritance

            # Verify all attributes are properly typed
            assert type(_.config.base_path)      is Safe_Str__Fast_API__Route__Prefix
            assert type(_.config.add_admin_ui)   is bool
            assert type(_.config.docs_offline)   is bool
            assert type(_.config.enable_cors)    is bool
            assert type(_.config.enable_api_key) is bool
            assert type(_.config.default_routes) is bool
            assert type(_.config.name)           is Safe_Str__Fast_API__Name
            assert type(_.config.version)        is Safe_Str__Version
            assert type(_.config.description)    is type(None)                           # None by default

            assert type(_.server_id)             is Random_Guid

            # Verify defaults
            assert _.config.base_path      == '/'
            assert _.config.add_admin_ui   is False
            assert _.config.docs_offline   is True
            assert _.config.enable_cors    is False
            assert _.config.enable_api_key is False
            assert _.config.default_routes is True
            assert _.config.version        == version__osbot_fast_api
            assert _.config.description    is None

    def test__init__with_custom_name(self):                                        # Test custom name initialization
        config = Schema__Fast_API__Config(name = "My API Service!")
        with Fast_API(config=config) as _:
            assert _.config.name               == "My API Service_"                # Sanitized by Safe_Str__Fast_API__Name

    def test__init__without_name(self):                                            # Test auto-name from class
        with Fast_API() as _:
            assert _.config.name               == "Fast_API"                       # Uses class name

    def test__init__with_all_parameters(self):                                     # Test comprehensive initialization
        kwargs = dict(base_path      = '/api/v1'               ,
                      add_admin_ui   = True                    ,
                      docs_offline   = False                   ,
                      enable_cors    = True                    ,
                      enable_api_key = True                    ,
                      default_routes = False                   ,
                      name           = 'Test API'              ,
                      version        = 'v1.2.3'                ,
                      description    = 'Test description'      )

        config = Schema__Fast_API__Config(**kwargs)
        with Fast_API(config=config) as _:
            # Direct attribute verification (avoiding .obj() due to deque serialization issue)
            assert _.config.base_path      == '/api/v1'
            assert _.config.add_admin_ui   is True
            assert _.config.docs_offline   is False
            assert _.config.enable_cors    is True
            assert _.config.enable_api_key is True
            assert _.config.default_routes is False
            assert _.config.name           == 'Test API'
            assert _.config.version        == 'v1.2.3'
            assert _.config.description    == 'Test description'

    # Exception handler tests

    def test_add_global_exception_handlers(self):                                  # Test exception handler registration
        with Fast_API() as _:
            _.add_global_exception_handlers()
            app = _.app()

            # Verify handlers are registered
            assert len(app.exception_handlers) >= 3                                # At least 3 handlers
            assert Exception in app.exception_handlers
            assert HTTPException in app.exception_handlers
            assert RequestValidationError in app.exception_handlers


    def test_global_exception_handler(self):                                 # Test generic exception handling
        with Fast_API() as _:
            _.add_global_exception_handlers()
            app = _.app()

            handler = app.exception_handlers[Exception]                         # Get the handler

            error_message = "Test error!!"                                      # Create mock request and exception
            mock_request = MagicMock(spec=Request)
            test_exception = ValueError(error_message)

            response = invoke_async(handler(mock_request, test_exception))      # Call handler

            assert type(response) is JSONResponse
            assert response.status_code           == 500
            content = response.body.decode()
            assert content == ('{"detail":"An unexpected error occurred.",'
                                '"error":"'+ error_message +
                                '","stack_trace":"NoneType: None\\n"}')


    def test_http_exception_handler(self):                                   # Test HTTP exception handling
        with Fast_API() as _:
            _.add_global_exception_handlers()
            app = _.app()

            handler = app.exception_handlers[HTTPException]
            mock_request = MagicMock(spec=Request)
            http_exc = HTTPException(status_code=404, detail="Not found")

            response = invoke_async(handler(mock_request, http_exc))

            assert response.status_code == 404
            assert b'"detail":"Not found"' in response.body

    def test_validation_exception_handler(self):                             # Test validation exception handling
        with Fast_API() as _:
            _.add_global_exception_handlers()
            app = _.app()

            handler = app.exception_handlers[RequestValidationError]
            mock_request = MagicMock(spec=Request)

            # Create validation error
            validation_exc = RequestValidationError([])
            validation_exc.errors = lambda: [{"loc": ["body", "field"], "msg": "field required"}]

            response = invoke_async(handler(mock_request, validation_exc))

            assert response.status_code == 400
            assert b'"detail"' in response.body

    # Route management tests

    def test_add_route_get(self):                                                  # Test GET route addition
        with Fast_API() as _:
            def test_endpoint():
                return {"message": "test"}

            _.add_route_get(test_endpoint)

            assert '/test-endpoint' in _.routes_paths()

            # Test the route works
            client = _.client()
            response = client.get('/test-endpoint')
            assert response.status_code == 200
            assert response.json() == {"message": "test"}

    def test_add_route_post(self):                                                 # Test POST route addition
        with Fast_API() as _:
            def submit_data(data: dict):
                return {"received": data}

            _.add_route_post(submit_data)

            assert '/submit-data' in _.routes_paths()

            # Test the route works
            client = _.client()
            test_data = {"key": "value"}
            response = client.post('/submit-data', json=test_data)
            assert response.status_code == 200
            assert response.json() == {"received": test_data}

    def test_add_route_with_custom_methods(self):                                  # Test custom HTTP methods
        with Fast_API() as _:
            def custom_endpoint():
                return {"message": "custom"}

            _.add_route(custom_endpoint, methods=['PUT', 'PATCH'])

            client = _.client()

            # Test PUT works
            response = client.put('/custom-endpoint')
            assert response.status_code == 200

            # Test PATCH works
            response = client.patch('/custom-endpoint')
            assert response.status_code == 200

            # Test GET doesn't work
            response = client.get('/custom-endpoint')
            assert response.status_code == 405                                     # Method not allowed

    def test_add_routes_with_class(self):                                          # Test adding route class
        from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes

        class Test_Routes(Fast_API__Routes):
            tag = 'test'

            def test_method(self):
                return {"result": "test"}

            def setup_routes(self):
                self.add_route_get(self.test_method)

        with Fast_API() as _:
            _.add_routes(Test_Routes)

            assert '/test/test-method' in _.routes_paths()

    # App configuration tests

    def test_app_kwargs_with_defaults(self):                                       # Test default app kwargs
        with Fast_API() as _:
            kwargs = _.app_kwargs()

            assert kwargs['docs_url']  is None                                     # Disabled for custom docs
            assert kwargs['redoc_url'] is None                                     # Disabled for custom docs
            assert kwargs['title']      == 'Fast_API'
            assert kwargs['version']    == version__osbot_fast_api
            assert 'description' not in kwargs                                     # Not set when None

    def test_app_kwargs_with_custom_values(self):                                  # Test custom app kwargs
        config = Schema__Fast_API__Config(name="Custom", version="v2.0.0", description="Test")
        with Fast_API(config=config) as _:
            kwargs = _.app_kwargs()

            assert kwargs['title']       == 'Custom'
            assert kwargs['version']     == 'v2.0.0'
            assert kwargs['description'] == 'Test'

    def test_app_kwargs_with_default_routes_false(self):                           # Test with default routes disabled
        config   = Schema__Fast_API__Config(default_routes=False)
        with Fast_API(config=config) as _:
            kwargs = _.app_kwargs()

            assert 'docs_url' not in kwargs                                        # Not overridden
            assert 'redoc_url' not in kwargs                                       # Not overridden

    def test_app_router(self):                                                     # Test router access
        with Fast_API() as _:
            router = _.app_router()
            app = _.app()

            assert router is app.router                                            # Same object

    def test_open_api_json(self):                                                  # Test OpenAPI JSON generation
        with Fast_API() as _:
            _.setup()
            openapi = _.open_api_json()

            assert type(openapi) is dict
            assert openapi['openapi'] == '3.1.0'
            assert openapi['info']['title'] == 'Fast_API'
            assert openapi['info']['version'] == version__osbot_fast_api

    # Mounting tests

    def test_mount_on_parent_app(self):                                            # Test mounting on parent app
        config_parent = Schema__Fast_API__Config(name="Parent")
        config_child  = Schema__Fast_API__Config(name="Child", base_path="/child")
        parent = Fast_API(config=config_parent).setup()
        child = Fast_API (config=config_child ).setup()

        child.mount(parent.app())

        parent_client = parent.client()                                             # Verify child routes accessible via parent
        response = parent_client.get('/child/docs', follow_redirects=False)
        assert response.status_code == 200

    def test_mount_fast_api_class(self):                                            # Test mounting another Fast_API class
        with Fast_API() as main:
            main.setup()

            class Child_API(Fast_API):                                              # Create child class
                def setup_routes(self):
                    def child_route():
                        return {"source": "child"}
                    self.add_route_get(child_route)
                    return self

            main.mount_fast_api(Child_API, base_path="/api/child")

            client   = main.client()                                                # Test child route accessible
            response = client.get('/api/child/child-route')
            assert response.status_code == 200
            assert response.json() == {"source": "child"}

    # Setup methods tests

    def test_setup_chain(self):                                                    # Test full setup chain
        with Fast_API() as _:
            result = _.setup()

            assert result is _                                                     # Returns self for chaining

            # Verify all setup methods were called
            assert len(_.routes_paths()) > 0                                       # Routes added
            assert _.user_middlewares() != []                                      # Middlewares added

    def test_setup_static_routes_with_path(self):                                  # Test static route setup
        with Fast_API() as _:
            _.path_static_folder = lambda: parent_folder(__file__)                  # Override to provide static path
            _.setup_static_routes()

            # Check static mount exists
            mounts = [route for route in _.app().routes if hasattr(route, 'path') and route.path == '/static']
            assert len(mounts) == 1

    def test_setup_without_default_routes(self):                                    # Test setup without default routes
        config   = Schema__Fast_API__Config(default_routes=False)
        with Fast_API(config=config) as _:
            _.setup()

            assert '/'       not in _.routes_paths()                                # Should not have default routes
            assert '/docs'   not in _.routes_paths()
            assert '/config' not in _.routes_paths()

    # Middleware tests

    def test_setup_middleware_cors_enabled(self):                                   # Test CORS middleware
        config = Schema__Fast_API__Config(enable_cors=True)
        with Fast_API(config=config) as _:
            _.setup_middleware__cors()

            # Make request to verify CORS headers
            client = _.client()
            response = client.options('/', headers={'Origin': 'http://example.com'})

            assert 'access-control-allow-origin' in response.headers
            assert response.headers['access-control-allow-origin'] == '*'

    def test_setup_middleware_api_key_enabled(self):                               # Test API key middleware
        temp_env_vars = { ENV_VAR__FAST_API__AUTH__API_KEY__NAME  : 'X-API-Key',
                          ENV_VAR__FAST_API__AUTH__API_KEY__VALUE : 'test-key-123'}
        config        = Schema__Fast_API__Config(enable_api_key=True)
        with Temp_Env_Vars(env_vars=temp_env_vars):
            with Fast_API(config=config).setup() as _:
                client                 = _.client()
                path_that_doesnt_exist = '/config'
                path_that_exists       = '/config/info'
                headers                = {'X-API-Key': 'test-key-123'}                          # Request with auth headers should succeed

                assert client.get(path_that_doesnt_exist).status_code == 401                    # Request without key should fail
                assert client.get(path_that_exists      ).status_code == 401                    # we get 401 on both cases


                assert client.get(path_that_doesnt_exist, headers=headers).status_code == 404   # get 404, if path doesn't exist
                assert client.get(path_that_exists      , headers=headers).status_code == 200   # get 200, if path exists

    def test_setup_middleware_detect_disconnect(self):                             # Test disconnect detection middleware
        with Fast_API() as _:
            _.setup_middleware__detect_disconnect()

            middlewares = _.user_middlewares()
            middleware_types = [m['type'] for m in middlewares]

            assert 'Middleware__Detect_Disconnect' in middleware_types


    # Route removal tests

    def test_route_remove_existing(self):                                          # Test removing existing route
        with Fast_API() as _:
            def test_route():
                return {}

            _.add_route_get(test_route)
            assert '/test-route' in _.routes_paths()

            # Remove route
            result = _.route_remove('/test-route')
            assert result is True
            assert '/test-route' not in _.routes_paths()

    def test_route_remove_nonexistent(self):                                       # Test removing nonexistent route
        with Fast_API() as _:
            result = _.route_remove('/nonexistent')
            assert result is False

    # Utility method tests

    def test_routes_methods_unique(self):                                          # Test unique route methods
        with Fast_API() as _:
            _.setup()

            def custom_get():
                return {}

            def custom_post():
                return {}

            _.add_route_get(custom_get)
            _.add_route_post(custom_post)

            methods = _.routes_methods()
            assert 'custom_get' in methods
            assert 'custom_post' in methods
            # Should be unique (no duplicates)
            assert len(methods) == len(set(methods))

    def test_routes_paths_all(self):                                               # Test all routes paths
        with Fast_API() as _:
            _.setup()

            all_paths = _.routes_paths_all()

            # Should include defaults and expanded mounts
            assert type(all_paths) is list
            assert len(all_paths) > 0

    def test_user_middlewares_with_params(self):                                   # Test middleware listing with params
        with Fast_API() as _:
            _.setup()

            middlewares = _.user_middlewares(include_params=True)

            for middleware in middlewares:
                assert 'type' in middleware
                assert 'function_name' in middleware
                assert 'params' in middleware

    def test_user_middlewares_without_params(self):                                # Test middleware listing without params
        with Fast_API() as _:
            _.setup()

            middlewares = _.user_middlewares(include_params=False)

            for middleware in middlewares:
                assert 'type'               in middleware
                assert 'function_name'      in middleware
                assert 'params'         not in middleware

    def test_version__fast_api_server(self):                                       # Test version method
        with Fast_API() as _:
            version = _.version__fast_api_server()

            assert type(version) is str
            assert version == version__osbot_fast_api

    # Edge cases and error scenarios

    def test_invalid_version_format(self):                                         # Test invalid version validation
        error_message = 'in Safe_Str__Version, value does not match required pattern: ^v(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})$'
        with pytest.raises(ValueError, match=re.escape(error_message)):
            Schema__Fast_API__Config(version="not-version")

    def test_special_characters_in_name(self):                                     # Test name sanitization
        config = Schema__Fast_API__Config(name="Test@API#2024!")
        with Fast_API(config=config) as _:
            assert _.config.name == "Test_API_2024_"                                      # Special chars replaced

    def test_special_characters_in_description(self):                              # Test description sanitization
        config = Schema__Fast_API__Config(description="API with @#$ special chars!")
        with Fast_API(config=config) as _:
            assert _.config.description == "API with ___ special chars_"                  # Sanitized

    def test_base_path_sanitization(self):                                         # Test base path validation
        config = Schema__Fast_API__Config(base_path="/api/v1/")
        with Fast_API(config=config) as _:
            assert _.config.base_path == "/api/v1"                                       # Preserved

    def test_from_json_deserialization(self):                                      # Test Type_Safe deserialization
        json_data = {'config': { 'name'          : 'RestoredAPI',
                                 'version'       : 'v2.0.0'     ,
                                 'enable_cors'   : True         ,
                                 'enable_api_key': True         }}

        restored = Fast_API.from_json(json_data)

        assert type(restored) is Fast_API
        assert restored.config.name == 'RestoredAPI'
        assert restored.config.version == 'v2.0.0'
        assert restored.config.enable_cors is True
        assert restored.config.enable_api_key is True

    # Integration tests

    def test_full_lifecycle(self):                                                 # Test complete API lifecycle
        config = Schema__Fast_API__Config(name="FullTest")
        with Fast_API(config=config) as api:
            # Setup
            api.setup()

            # Add custom route
            def health_check():
                return {"status": "healthy"}
            api.add_route_get(health_check)

            # Test client
            client = api.client()

            # Test default redirect
            response = client.get('/', follow_redirects=False)
            assert response.status_code == 307

            # Test custom route
            response = client.get('/health-check')
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}

            # Test config endpoint
            response = client.get('/config/info')
            assert response.status_code == 200

            # Remove route
            assert api.route_remove('/health-check') is True

            # Verify removal
            response = client.get('/health-check')
            assert response.status_code == 404

    def test_multiple_fast_api_instances(self):                                    # Test multiple instances don't interfere
        config_api1 = Schema__Fast_API__Config(name="API1")
        config_api2 = Schema__Fast_API__Config(name="API2")
        api1 = Fast_API(config=config_api1).setup()
        api2 = Fast_API(config=config_api2).setup()

        # Each should have its own state
        assert api1.config.name != api2.config.name
        assert api1.server_id   != api2.server_id
        assert api1.app()       is not api2.app()

        # Add route to api1 only
        def api1_route():
            return {"api": "1"}
        api1.add_route_get(api1_route)

        # Should only exist in api1
        assert '/api1-route' in api1.routes_paths()
        assert '/api1-route' not in api2.routes_paths()


    def test_server_id_persistence(self):                                             # Test server_id uniqueness
        api1 = Fast_API()
        api2 = Fast_API()

        assert api1.server_id != api2.server_id                                       # Each instance unique
        assert type(api1.server_id) is Random_Guid
        assert type(api2.server_id) is Random_Guid

    def test_path_static_folder_override(self):                                       # Test static folder configuration
        with Temp_Folder() as temp_folder:

            class Custom_Fast_API(Fast_API):
                def path_static_folder(self):
                    return temp_folder.full_path


            with Custom_Fast_API() as _:
                _.setup()
                assert _.path_static_folder() == temp_folder.full_path

                # Verify static mount created
                static_mounts = [r for r in _.app().routes if hasattr(r, 'path') and r.path == '/static']
                assert len(static_mounts) == 1

    def test__regression__serialization_round_trip__doesnt_work_due_to_deque_use(self):
        config = Schema__Fast_API__Config(name="TestAPI", version="v1.0.0", enable_cors=True)
        with Fast_API(config=config) as original:
            # error_message = "Type <class 'collections.deque'> not serializable"
            # with pytest.raises(TypeError, match=re.escape(error_message)):
            #     original.json()                                                           # BUG: should had not raised exception

            # Serialize to JSON
            json_data = original.json()

            # Deserialize back
            with Fast_API.from_json(json_data) as restored:
                # Must be perfect round-trip
                assert restored.config.name         == original.config.name
                assert restored.config.version      == original.config.version
                assert restored.config.enable_cors  == original.config.enable_cors

                # Verify type preservation
                assert type(restored.config.name     ) is Safe_Str__Fast_API__Name
                assert type(restored.config.version  ) is Safe_Str__Version
                assert type(restored.server_id       ) is Random_Guid