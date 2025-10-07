from unittest                                            import TestCase
from osbot_fast_api.api.routes.Fast_API__Route__Parser   import Fast_API__Route__Parser


class test_Fast_API__Route__Parser(TestCase):

    @classmethod
    def setUpClass(cls):                                                            # Setup expensive resources once
        cls.route_parser = Fast_API__Route__Parser()

    def test__init__(self):                                                         # Test parser initialization
        with Fast_API__Route__Parser() as _:
            assert type(_) is Fast_API__Route__Parser

    def test_extract_param_names(self):                                             # Test parameter name extraction from function signatures
        def function_no_params(self):
            pass

        def function_with_params(self, user_id, name):
            pass

        def function_no_self(user_id, name):
            pass

        with self.route_parser as _:
            assert _.extract_param_names(function_no_params)   == set()
            assert _.extract_param_names(function_with_params) == {'user_id', 'name'}
            assert _.extract_param_names(function_no_self)     == {'user_id', 'name'}

    def test_convert_to_literal_segment(self):                                      # Test underscore to hyphen conversion
        with self.route_parser as _:
            assert _.convert_to_literal_segment('hello_world')  == 'hello-world'
            assert _.convert_to_literal_segment('api_v1_data')  == 'api-v1-data'
            assert _.convert_to_literal_segment('simple')       == 'simple'
            assert _.convert_to_literal_segment('')             == ''

    def test_create_param_segment(self):                                            # Test parameter segment creation
        with self.route_parser as _:
            assert _.create_param_segment('id')       == '{id}'
            assert _.create_param_segment('user_id')  == '{user_id}'
            assert _.create_param_segment('name')     == '{name}'

    def test_parse_simple_part(self):                                               # Test simple part parsing without underscores
        param_names = {'user', 'id', 'name'}

        with self.route_parser as _:
            assert _.parse_simple_part('user', param_names)    == ['{user}' ]
            assert _.parse_simple_part('id', param_names)      == ['{id}'   ]
            assert _.parse_simple_part('profile', param_names) == ['profile']
            assert _.parse_simple_part('data', param_names)    == ['data'   ]
            assert _.parse_simple_part('name', set())          == ['name'   ]

    def test_parse_part_with_underscore__param_followed_by_literal(self):           # Test parsing param_literal pattern
        param_names = {'user', 'id', 'models'}

        with self.route_parser as _:
            assert _.parse_part_with_underscore('user_profile', param_names) == ['{user}', 'profile']
            assert _.parse_part_with_underscore('id_details', param_names)   == ['{id}', 'details']
            assert _.parse_part_with_underscore('user_', param_names)        == ['{user}']

    def test_parse_part_with_underscore__literal_conversion(self):                  # Test non-param parts become literals
        param_names = {'user', 'id', 'models'}

        with self.route_parser as _:
            assert _.parse_part_with_underscore('api_version', param_names)  == ['api-version']
            assert _.parse_part_with_underscore('test_data', param_names)    == ['test-data']

    def test_parse_part_with_underscore__multiple_underscores(self):                # Test handling multiple underscores in literal
        param_names = {'user', 'id'}

        with self.route_parser as _:
            assert _.parse_part_with_underscore('user_profile_data', param_names) == ['{user}', 'profile-data']

    def test_parse_part_with_underscore__exact_match_with_underscores(self):        # Test CRITICAL: exact match takes precedence
        param_names = {'user_id', 'user_profile_id'}

        with self.route_parser as _:
            assert _.parse_part_with_underscore('user_id', param_names)         == ['{user_id}']
            assert _.parse_part_with_underscore('user_profile_id', param_names) == ['{user_profile_id}']

    def test_parse_part_with_params(self):                                          # Test part parsing dispatcher
        param_names = {'user', 'id', 'models'}

        with self.route_parser as _:
            assert _.parse_part_with_params('user', param_names)          == ['{user}']
            assert _.parse_part_with_params('profile', param_names)       == ['profile']
            assert _.parse_part_with_params('user_profile', param_names)  == ['{user}', 'profile']
            assert _.parse_part_with_params('api_data', param_names)      == ['api-data']

    def test_parse_function_name_segments__no_double_underscore(self):              # Test basic function name without segments
        with self.route_parser as _:
            assert _.parse_function_name_segments('get_users', set()) == ['get-users']

    def test_parse_function_name_segments__with_segments(self):                     # Test double underscore creates segments
        with self.route_parser as _:
            assert _.parse_function_name_segments('v1__models_raw', set())  == ['v1', 'models-raw']
            assert _.parse_function_name_segments('api__data', set())       == ['api', 'data']

    def test_parse_function_name_segments__with_params(self):                       # Test segments with parameter detection
        param_names = {'models'}
        with self.route_parser as _:
            assert _.parse_function_name_segments('v1__models_raw', param_names) == ['v1', '{models}', 'raw']
            assert _.parse_function_name_segments('v1__models', param_names)     == ['v1', '{models}']

    def test_parse_function_name_segments__multiple_params(self):                   # Test multiple parameters in segments
        param_names = {'user', 'id'}
        with self.route_parser as _:
            assert _.parse_function_name_segments('get__user__id', param_names)         == ['get', '{user}', '{id}']
            assert _.parse_function_name_segments('api__user_profile__id', param_names) == ['api', '{user}', 'profile', '{id}']

    def test_parse_function_name_segments__complex_case(self):                      # Test complex scenario with mixed patterns
        param_names = {'user', 'post'}
        with self.route_parser as _:
            result = _.parse_function_name_segments('api_v2__user_profile__post_details', param_names)
            assert result == ['api-v2', '{user}', 'profile', '{post}', 'details']

    def test_parse_route_path__simple_functions(self):                              # Test complete path generation for simple functions
        def v1__models_raw(self, models):
            pass

        def v1__models_raw_no_param(self):
            pass

        def get__user_profile(self, user):
            pass

        with self.route_parser as _:
            assert _.parse_route_path(v1__models_raw)           == '/v1/{models}/raw'
            assert _.parse_route_path(v1__models_raw_no_param)  == '/v1/models-raw-no-param'
            assert _.parse_route_path(get__user_profile)        == '/get/{user}/profile'

    def test_parse_route_path__complex_functions(self):                             # Test path generation for complex functions
        def api_v2__data(self):
            pass

        def complex__user_id__post_details(self, user, post):
            pass

        with self.route_parser as _:
            assert _.parse_route_path(api_v2__data)                      == '/api-v2/data'
            assert _.parse_route_path(complex__user_id__post_details)    == '/complex/{user}/id/{post}/details'

    def test_parse_route_path__edge_cases(self):                                    # Test edge cases with empty segments
        def empty_name__(self):
            pass

        def __start_with_double(self):
            pass

        def multiple____underscores(self):
            pass

        def trailing__(self):
            pass

        with self.route_parser as _:
            assert _.parse_route_path(empty_name__)            == '/empty-name'
            assert _.parse_route_path(__start_with_double)     == '/start-with-double'
            assert _.parse_route_path(multiple____underscores) == '/multiple/underscores'
            assert _.parse_route_path(trailing__)              == '/trailing'

    def test_parse_route_path__real_world_patterns(self):                           # Test actual FastAPI route patterns
        def status(self):
            pass

        def get_user(self):
            pass

        def api_v1__users(self):
            pass

        def api__resource_id(self, resource):
            pass

        with self.route_parser as _:
            assert _.parse_route_path(status)           == '/status'
            assert _.parse_route_path(get_user)         == '/get-user'
            assert _.parse_route_path(api_v1__users)    == '/api-v1/users'
            assert _.parse_route_path(api__resource_id) == '/api/{resource}/id'

    def test_parameter_detection_rules__single_underscore(self):                    # Test RULE: single underscore enables auto-detection
        def fetch__user_id       (user         ): pass
        def fetch__order_status  (order        ): pass
        def fetch__item_count    (item         ): pass

        with self.route_parser as _:
            assert _.parse_route_path(fetch__user_id)      == '/fetch/{user}/id'
            assert _.parse_route_path(fetch__order_status) == '/fetch/{order}/status'
            assert _.parse_route_path(fetch__item_count)   == '/fetch/{item}/count'

    def test_parameter_detection_rules__exact_match(self):                          # Test RULE: exact match always works
        def get__user_id_profile (user_id_profile): pass
        def process__long_param_name(long_param_name): pass

        with self.route_parser as _:
            assert _.parse_route_path(get__user_id_profile)      == '/get/{user_id_profile}'
            assert _.parse_route_path(process__long_param_name)  == '/process/{long_param_name}'

    def test_parameter_detection_rules__double_underscore_separator(self):          # Test RULE: __ creates explicit boundaries
        def get__user_id__profile(user_id): pass
        def fetch__company__dept_id_mgr(company): pass

        with self.route_parser as _:
            assert _.parse_route_path(get__user_id__profile)       == '/get/{user_id}/profile'
            assert _.parse_route_path(fetch__company__dept_id_mgr) == '/fetch/{company}/dept-id-mgr'

    def test_confusing_cases__documentation(self):                                  # Test confusing cases with clear documentation
        def get__id                      (id             ): pass
        def get__id_user                 (id             ): pass
        def get__id__user                (id             ): pass
        def fetch__user_id_profile       (user_id        ): pass
        def fetch__user_id__profile      (user_id        ): pass
        def update__user_profile_id_data (user_profile_id): pass
        def update__user_profile_id__data(user_profile_id): pass

        with self.route_parser as _:
            assert _.parse_route_path(get__id)                        == '/get/{id}'
            assert _.parse_route_path(get__id_user)                   == '/get/{id}/user'
            assert _.parse_route_path(get__id__user)                  == '/get/{id}/user'
            assert _.parse_route_path(fetch__user_id_profile)         == '/fetch/user-id-profile'
            assert _.parse_route_path(fetch__user_id__profile)        == '/fetch/{user_id}/profile'
            assert _.parse_route_path(update__user_profile_id_data)   == '/update/user-profile-id-data'
            assert _.parse_route_path(update__user_profile_id__data)  == '/update/{user_profile_id}/data'