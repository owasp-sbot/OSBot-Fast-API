from unittest                                                   import TestCase
from osbot_fast_api.api.Fast_API                                import Fast_API, ENV_VAR__FAST_API__AUTH__API_KEY__NAME, ENV_VAR__FAST_API__AUTH__API_KEY__VALUE
from osbot_fast_api.api.middlewares.Middleware__Check_API_Key   import ERROR_MESSAGE__NO_KEY_NAME_SETUP, ERROR_MESSAGE__NO_KEY_VALUE_SETUP, ERROR_MESSAGE__API_KEY_MISSING
from osbot_fast_api.api.schemas.consts.consts__Fast_API             import AUTH__EXCLUDED_PATHS
from osbot_fast_api.utils.Fast_API__Server_Info                 import fast_api__server_info
from osbot_utils.testing.Temp_Env_Vars                          import Temp_Env_Vars
from osbot_utils.utils.Status                                   import status_error


class With_API_Key(Fast_API):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config.enable_api_key = True


class test_Middleware__Check_API_Key(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env_name__api_key_name  = 'admin-key-name'
        cls.env_name__api_key_value = 'admin-key-value'
        cls.temp_env_vars = { ENV_VAR__FAST_API__AUTH__API_KEY__NAME : cls.env_name__api_key_name  ,
                              ENV_VAR__FAST_API__AUTH__API_KEY__VALUE: cls.env_name__api_key_value }
        cls.admin_fastapi = With_API_Key().setup()

    def setUp(self):
        self.client        = self.admin_fastapi.client()

    def test__init__(self):
        expected_middleware = { 'function_name': None                                                          ,
                                'params'       : { 'allow_cors'             : False                            ,
                                                   'env_var__api_key__name' : 'FAST_API__AUTH__API_KEY__NAME'  ,
                                                   'env_var__api_key__value': 'FAST_API__AUTH__API_KEY__VALUE'},
                                 'type'        : 'Middleware__Check_API_Key'}
        with self.admin_fastapi  as _:
            assert expected_middleware in _.user_middlewares()

    def test_no_env_vars(self):
        with With_API_Key().setup() as _:
            response_1 = _.client().get('/')
            assert response_1.status_code == 401
            assert response_1.json()      == status_error(ERROR_MESSAGE__NO_KEY_NAME_SETUP)

        temp_env_vars = {ENV_VAR__FAST_API__AUTH__API_KEY__NAME: self.env_name__api_key_name}
        with Temp_Env_Vars(env_vars=temp_env_vars):
            with With_API_Key().setup() as _:
                response_2 = _.client().get('/')
                assert response_2.status_code == 401
                assert response_2.json()      == status_error(ERROR_MESSAGE__NO_KEY_VALUE_SETUP)

    def test_client__config__info(self):
        auth_headers = {self.env_name__api_key_name: 'AAAAAA'}
        with Temp_Env_Vars(env_vars=self.temp_env_vars):
            with self.client as _:
                response_1 = _.get('config/info')
                assert response_1.status_code == 401
                assert response_1.json()      == status_error(ERROR_MESSAGE__API_KEY_MISSING)

                response_2 = _.get('config/info', headers=auth_headers)
                assert response_2.status_code == 401

                auth_headers[self.env_name__api_key_name] = self.env_name__api_key_value

                response_3 = _.get('config/info', headers=auth_headers)
                assert response_3.status_code == 200
                assert response_3.json()      == fast_api__server_info.json()

    def test_api_key_in_cookie(self):                                                 # Test cookie-based auth
        with Temp_Env_Vars(env_vars=self.temp_env_vars):
            with With_API_Key().setup() as _:
                client = _.client()

                # Set cookie
                client.cookies.set(self.env_name__api_key_name, self.env_name__api_key_value)

                response = client.get('/config/info')
                assert response.status_code == 200

    def test_invalid_api_key_formats(self):                                          # Test various invalid formats
        with Temp_Env_Vars(env_vars=self.temp_env_vars):
            with With_API_Key().setup() as _:
                client = _.client()

                # Empty string
                headers = {self.env_name__api_key_name: ''}
                assert client.get('/config/info', headers=headers).status_code == 401

                # Whitespace
                headers = {self.env_name__api_key_name: '   '}
                assert client.get('/config/info', headers=headers).status_code == 401

                # Special characters
                headers = {self.env_name__api_key_name: '!@#$%^&*()'}
                assert client.get('/config/info', headers=headers).status_code == 401

    def test_excluded_paths_comprehensive(self):                                      # Test all excluded paths

        with Temp_Env_Vars(env_vars=self.temp_env_vars):
            with With_API_Key().setup() as _:
                client = _.client()

                for path in AUTH__EXCLUDED_PATHS:
                    if path in ['/auth/set-cookie-form', '/docs', '/openapi.json']:  # Existing paths
                        response = client.get(path)
                        assert response.status_code in [200, 307]                    # Should be accessible