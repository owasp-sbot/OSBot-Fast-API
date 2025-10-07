from unittest                                                                      import TestCase
from osbot_fast_api.api.routes.Fast_API__Routes                                    import Fast_API__Routes
from osbot_fast_api.api.routes.Fast_API__Route__Parser                             import Fast_API__Route__Parser


class test_Fast_API__Routes__path_parsing__unit(TestCase):                          # Unit tests using parser directly

    @classmethod
    def setUpClass(cls):                                                            # Setup expensive resources once
        cls.parser = Fast_API__Route__Parser()

    def setUp(self):
        self.routes = Fast_API__Routes()

    def test_add_routes__simple_examples(self):                                     # Test simple route path generation
        def no_params():
            pass

        def no__vars():
            pass

        def an__var(var):
            pass

        def an_post(abc: dict):
            pass

        def an__user_id(user_id, abc: dict):
            pass

        def an__user__id(user, abc: dict):
            pass

        with self.routes as _:
            _.add_routes_get(no_params, no__vars, an__var)
            _.add_routes_post(an_post, an__user_id, an__user__id)

            assert _.routes_paths() == sorted(['/no-params'   ,
                                               '/no/vars'     ,
                                               '/an/{var}'    ,
                                               '/an-post'     ,
                                               '/an/{user_id}',
                                               '/an/{user}/id'])

    def test_edge_cases__underscores_and_hyphens(self):                             # Test underscore to hyphen conversion
        def api_v1__data(self):
            pass

        def api_v2__user_profile(self):
            pass

        def get__user_id(user_id):
            pass

        def get__user_profile_id(user_profile_id):
            pass

        def fetch__user_profile_id(user):
            pass

        def update__profile_user_id(profile_user_id, data: dict):
            pass

        with self.routes as _:
            _.add_routes_get(api_v1__data            ,
                             api_v2__user_profile    ,
                             get__user_id            ,
                             get__user_profile_id    ,
                             fetch__user_profile_id  )
            _.add_route_post(update__profile_user_id)

            assert _.routes_paths() == sorted(['/api-v1/data'               ,
                                               '/api-v2/user-profile'       ,
                                               '/get/{user_id}'             ,
                                               '/get/{user_profile_id}'     ,
                                               '/fetch/{user}/profile-id'   ,
                                               '/update/{profile_user_id}'  ])

    def test_multiple_path_segments(self):                                          # Test multiple segment paths
        def api__v1__users(self):
            pass

        def api__v1__user(user):
            pass

        def api__v1__user__posts(user):
            pass

        def api__v1__user__post(user, post):
            pass

        def api__user_profile__post_details(user, post):
            pass

        def get__user_id__profile__settings(user_id):
            pass

        with self.routes as _:
            _.add_routes_get(api__v1__users                    ,
                             api__v1__user                     ,
                             api__v1__user__posts              ,
                             api__v1__user__post               ,
                             api__user_profile__post_details   ,
                             get__user_id__profile__settings   )

            assert _.routes_paths() == sorted(['/api/v1/users'                         ,
                                               '/api/v1/{user}'                        ,
                                               '/api/v1/{user}/posts'                  ,
                                               '/api/v1/{user}/{post}'                 ,
                                               '/api/{user}/profile/{post}/details'    ,
                                               '/get/{user_id}/profile/settings'       ])

    def test_confusing_parameter_names(self):                                       # Test confusing parameter name patterns
        def get__id(id):
            pass

        def get__id_user(id):
            pass

        def get__id__user(id):
            pass

        def fetch__user_id_profile(user_id):
            pass

        def fetch__user_id__profile(user_id):
            pass

        def update__user_profile_id_data(user_profile_id):
            pass

        def update__user_profile_id__data(user_profile_id):
            pass

        with self.routes as _:
            _.add_routes_get(get__id                        ,
                             get__id_user                   ,
                             get__id__user                  ,
                             fetch__user_id_profile         ,
                             fetch__user_id__profile        )
            _.add_routes_post(update__user_profile_id_data  ,
                              update__user_profile_id__data )

            assert _.routes_paths() == sorted(['/get/{id}'                       ,
                                               '/get/{id}/user'                  ,
                                               '/fetch/user-id-profile'          ,
                                               '/fetch/{user_id}/profile'        ,
                                               '/update/user-profile-id-data'    ,
                                               '/update/{user_profile_id}/data'  ])

    def test_empty_and_special_cases(self):                                         # Test edge cases with empty segments
        def __(self):
            pass

        def a__(self):
            pass

        def __b(self):
            pass

        def a____b(self):
            pass

        def api__(self):
            pass

        def __user__(user):
            pass

        with self.routes as _:
            _.add_routes_get(__, a__, __b, a____b, api__, __user__)

            assert _.routes_paths() == sorted(['/'       ,
                                               '/a'      ,
                                               '/b'      ,
                                               '/a/b'    ,
                                               '/api'    ,
                                               '/{user}' ])


