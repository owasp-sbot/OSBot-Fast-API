from unittest                                   import TestCase
from osbot_fast_api.api.routes.Fast_API__Route__Parser import Fast_API__Route__Parser


class test_Fast_API__Route__Parser(TestCase):

    def setUp(self):
        self.route_parser = Fast_API__Route__Parser()

    # Test basic initialization
    def test__init__(self):
        assert type(self.route_parser) is Fast_API__Route__Parser

    # Test extract_param_names
    def test_extract_param_names(self):
        def function_no_params(self):                                                   # Function with no params
            pass

        def function_with_params(self, user_id, name):                                  # Function with params
            pass

        def function_no_self(user_id, name):                                           # Function without self
            pass

        with self.route_parser as _:
            assert _.extract_param_names(function_no_params)   == set()                 # No params except self
            assert _.extract_param_names(function_with_params) == {'user_id', 'name'}   # Two params
            assert _.extract_param_names(function_no_self)     == {'user_id', 'name'}   # Self not in signature

    # Test convert_to_literal_segment
    def test_convert_to_literal_segment(self):
        with self.route_parser as _:
            assert _.convert_to_literal_segment('hello_world')  == 'hello-world'        # Underscore to hyphen
            assert _.convert_to_literal_segment('api_v1_data')  == 'api-v1-data'        # Multiple underscores
            assert _.convert_to_literal_segment('simple')       == 'simple'             # No underscores
            assert _.convert_to_literal_segment('')             == ''                   # Empty string

    # Test create_param_segment
    def test_create_param_segment(self):
        with self.route_parser as _:
            assert _.create_param_segment('id')       == '{id}'                         # Simple param
            assert _.create_param_segment('user_id')  == '{user_id}'                    # Param with underscore
            assert _.create_param_segment('name')     == '{name}'                       # Another param

    # Test parse_simple_part
    def test_parse_simple_part(self):
        param_names = {'user', 'id', 'name'}                                           # Set of known params

        with self.route_parser as _:
            assert _.parse_simple_part('user', param_names)    == ['{user}']           # Is a parameter
            assert _.parse_simple_part('id', param_names)      == ['{id}']             # Is a parameter
            assert _.parse_simple_part('profile', param_names) == ['profile']          # Not a parameter
            assert _.parse_simple_part('data', param_names)    == ['data']             # Not a parameter
            assert _.parse_simple_part('name', set())          == ['name']             # No params defined

    # Test parse_part_with_underscore
    def test_parse_part_with_underscore(self):
        param_names = {'user', 'id', 'models'}                                         # Set of known params

        with self.route_parser as _:
            # Parameter followed by literal
            assert _.parse_part_with_underscore('user_profile', param_names) == ['{user}', 'profile']
            assert _.parse_part_with_underscore('id_details', param_names)   == ['{id}', 'details']

            # Not a parameter (whole thing becomes literal)
            assert _.parse_part_with_underscore('api_version', param_names)  == ['api-version']
            assert _.parse_part_with_underscore('test_data', param_names)    == ['test-data']

            # Parameter with multiple underscores in literal part
            assert _.parse_part_with_underscore('user_profile_data', param_names) == ['{user}', 'profile-data']

            # Edge case: underscore but empty remaining
            assert _.parse_part_with_underscore('user_', param_names)        == ['{user}']

    # Test parse_part_with_params
    def test_parse_part_with_params(self):
        param_names = {'user', 'id', 'models'}                                         # Set of known params

        with self.route_parser as _:
            # Simple parts (no underscore)
            assert _.parse_part_with_params('user', param_names)     == ['{user}']      # Is parameter
            assert _.parse_part_with_params('profile', param_names)  == ['profile']     # Not parameter

            # Parts with underscore
            assert _.parse_part_with_params('user_profile', param_names) == ['{user}', 'profile']
            assert _.parse_part_with_params('api_data', param_names)     == ['api-data']

    # Test parse_function_name_segments
    def test_parse_function_name_segments(self):
        with self.route_parser as _:
            # Basic function name (no double underscore)
            assert _.parse_function_name_segments('get_users', set()) == ['get-users']

            # With double underscore but no params
            assert _.parse_function_name_segments('v1__models_raw', set()) == ['v1', 'models-raw']
            assert _.parse_function_name_segments('api__data', set())      == ['api', 'data']

            # With double underscore and params
            param_names = {'models'}
            assert _.parse_function_name_segments('v1__models_raw', param_names) == ['v1', '{models}', 'raw']
            assert _.parse_function_name_segments('v1__models', param_names)     == ['v1', '{models}']

            # Multiple double underscores
            param_names = {'user', 'id'}
            assert _.parse_function_name_segments('get__user__id', param_names)         == ['get', '{user}', '{id}']
            assert _.parse_function_name_segments('api__user_profile__id', param_names) == ['api', '{user}', 'profile', '{id}']

            # Complex case
            param_names = {'user', 'post'}
            result = _.parse_function_name_segments('api_v2__user_profile__post_details', param_names)
            assert result == ['api-v2', '{user}', 'profile', '{post}', 'details']

    # Test parse_route_path (main method)
    def test_parse_route_path(self):
        # Test with actual functions
        def v1__models_raw(self, models):                                              # Function with models param
            pass

        def v1__models_raw_no_param(self):                                             # Function without models param
            pass

        def get__user_profile(self, user):                                             # Function with user param
            pass

        def api_v2__data(self):                                                        # Simple function
            pass

        def complex__user_id__post_details(self, user, post):                          # Multiple params
            pass

        with self.route_parser as _:
            assert _.parse_route_path(v1__models_raw)           == '/v1/{models}/raw'
            assert _.parse_route_path(v1__models_raw_no_param)  == '/v1/models-raw-no-param'
            assert _.parse_route_path(get__user_profile)        == '/get/{user}/profile'
            assert _.parse_route_path(api_v2__data)             == '/api-v2/data'
            assert _.parse_route_path(complex__user_id__post_details) == '/complex/{user}/id/{post}/details'

    # Test edge cases
    def test_edge_cases(self):
        def empty_name__(self):                                                        # Empty segment after __
            pass

        def __start_with_double(self):                                                 # Start with __
            pass

        def multiple____underscores(self):                                             # Multiple consecutive __
            pass

        def trailing__(self):                                                          # Trailing __
            pass

        with self.route_parser as _:
            assert _.parse_route_path(empty_name__)            == '/empty-name'
            assert _.parse_route_path(__start_with_double)     == '/start-with-double'
            assert _.parse_route_path(multiple____underscores) == '/multiple/underscores'
            assert _.parse_route_path(trailing__)              == '/trailing'

    # Test real-world examples from your use case
    def test_real_world_examples(self):
        # Your actual use cases
        def v1__models_raw(self):                                                      # No param
            pass

        def v1__models_raw_with_param(self, models):                                   # With param
            pass

        def v1__models__raw(self):                                                     # Multiple segments
            pass

        def get__user_id__profile(self, user):                                         # Mixed param and literal
            pass

        def get__user__id__profile_full(self, user, id):                                # Multiple params
            pass

        with self.route_parser as _:
            assert _.parse_route_path(v1__models_raw)            == '/v1/models-raw'
            assert _.parse_route_path(v1__models_raw_with_param) == '/v1/{models}/raw-with-param'
            assert _.parse_route_path(v1__models__raw)           == '/v1/models/raw'
            assert _.parse_route_path(get__user_id__profile)     == '/get/{user}/id/profile'
            assert _.parse_route_path(get__user__id__profile_full) == '/get/{user}/{id}/profile-full'

    # Test integration with Fast_API__Routes patterns
    def test_fast_api_routes_patterns(self):
        # Test patterns that would be used in Fast_API__Routes
        def status(self):                                                              # Simple route
            pass

        def get_user(self):                                                            # Single underscore
            pass

        def api_v1__users(self):                                                       # Version prefix
            pass

        def api__resource_id(self, resource):                                          # Resource with ID
            pass

        with self.route_parser as _:
            assert _.parse_route_path(status)           == '/status'
            assert _.parse_route_path(get_user)         == '/get-user'
            assert _.parse_route_path(api_v1__users)    == '/api-v1/users'
            assert _.parse_route_path(api__resource_id) == '/api/{resource}/id'