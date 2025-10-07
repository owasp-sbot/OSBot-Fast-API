from unittest                                                                      import TestCase
from osbot_fast_api.api.Fast_API                                                   import Fast_API
from osbot_fast_api.api.routes.Fast_API__Routes                                    import Fast_API__Routes
from osbot_fast_api.api.schemas.Schema__Fast_API__Config                           import Schema__Fast_API__Config
from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                                import Safe_Str
from osbot_utils.type_safe.primitives.core.Safe_Int                                import Safe_Int
from osbot_utils.type_safe.primitives.core.Safe_Float                              import Safe_Float
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid              import Random_Guid
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                  import Safe_Id
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url           import Safe_Str__Url

class test_Fast_API__Routes__path_parsing__integration(TestCase):                   # Integration tests with full FastAPI

    @classmethod
    def setUpClass(cls):                                                            # Setup expensive FastAPI infrastructure once
        cls.config   = Schema__Fast_API__Config(default_routes=False)
        cls.fast_api = None                                                         # Will be set per test class

    def test_with_fast_api_client__get_routes(self):                                # Test GET routes with actual HTTP calls
        class Test_Routes(Fast_API__Routes):
            tag = 'test'

            def users(self):
                return {'users': ['alice', 'bob']}

            def user__id(self, id: str):
                return {'user_id': id}

            def user_profile__profile_name(self, profile_name: str):
                return {'profile': profile_name}

            def api__v1__resource_id(self, resource_id: str):
                return {'resource': resource_id, 'version': 'v1'}

            def setup_routes(self):
                self.add_routes_get(self.users                       ,
                                    self.user__id                    ,
                                    self.user_profile__profile_name  ,
                                    self.api__v1__resource_id        )

        class Test_Fast_API(Fast_API):
            def setup_routes(self):
                self.add_routes(Test_Routes)

        fast_api = Test_Fast_API(config=self.config).setup()
        client   = fast_api.client()

        assert fast_api.routes_paths() == sorted(['/test/users'                       ,
                                                   '/test/user/{id}'                   ,
                                                   '/test/user-profile/{profile_name}' ,
                                                   '/test/api/v1/{resource_id}'        ])

        assert client.get('/test/users'                 ).json() == {'users': ['alice', 'bob']}
        assert client.get('/test/user/123'              ).json() == {'user_id': '123'}
        assert client.get('/test/user-profile/john-doe' ).json() == {'profile': 'john-doe'}
        assert client.get('/test/api/v1/resource-99'    ).json() == {'resource': 'resource-99', 'version': 'v1'}

    def test_with_fast_api_client__post_routes_with_body(self):                     # Test POST routes with Type_Safe bodies
        class User_Data(Type_Safe):
            name  : str
            email : str

        class Test_Routes(Fast_API__Routes):
            tag = 'api'

            def create__user(self, user_data: User_Data):
                return {'created': True, 'name': user_data.name}

            def update__user_id(self, user_id: str, user_data: User_Data):
                return {'updated': True, 'id': user_id, 'email': user_data.email}

            def patch__user_profile__setting(self, user_profile: str, setting: str, data: dict):
                return {'profile': user_profile, 'setting': setting, 'data': data}

            def setup_routes(self):
                self.add_routes_post(self.create__user                  ,
                                     self.update__user_id               ,
                                     self.patch__user_profile__setting  )

        class Test_Fast_API(Fast_API):
            def setup_routes(self):
                self.add_routes(Test_Routes)

        fast_api = Test_Fast_API(config=self.config).setup()
        client   = fast_api.client()

        assert fast_api.routes_paths() == sorted(['/api/create/user'                     ,
                                                   '/api/update/{user_id}'                ,
                                                   '/api/patch/{user_profile}/{setting}'  ])

        user_data = User_Data(name='Alice', email='alice@test.com')

        response = client.post('/api/create/user', json=user_data.json())
        assert response.json() == {'created': True, 'name': 'Alice'}

        response = client.post('/api/update/user-123', json=user_data.json())
        assert response.json() == {'updated': True, 'id': 'user-123', 'email': 'alice@test.com'}

        response = client.post('/api/patch/alice-profile/notifications', json={'enabled': True})
        assert response.json() == {'profile': 'alice-profile', 'setting': 'notifications', 'data': {'enabled': True}}

    def test_with_safe_str_primitives(self):                                        # Test Safe_Str primitive types in paths and queries
        class Test_Routes(Fast_API__Routes):
            tag = 'safe_str'

            def user__id(self, id: Safe_Id):
                return {'user_id': str(id), 'type': type(id).__name__}

            def resource__guid(self, guid: Random_Guid):
                return {'resource_guid': str(guid), 'is_valid_guid': len(str(guid)) == 36}

            def fetch_by_name(self, name: Safe_Str):
                return {'name': str(name), 'length': len(str(name))}

            def fetch_by_url(self, url: Safe_Str__Url):
                return {'url': str(url), 'is_url': str(url).startswith('http')}

            def setup_routes(self):
                self.add_routes_get(self.user__id      ,
                                    self.resource__guid ,
                                    self.fetch_by_name  ,
                                    self.fetch_by_url   )

        class Test_Fast_API(Fast_API):
            def setup_routes(self):
                self.add_routes(Test_Routes)

        fast_api = Test_Fast_API(config=self.config).setup()
        client   = fast_api.client()

        assert fast_api.routes_paths() == sorted(['/safe_str/user/{id}'        ,
                                                   '/safe_str/resource/{guid}'  ,
                                                   '/safe_str/fetch-by-name'    ,
                                                   '/safe_str/fetch-by-url'     ])

        response = client.get('/safe_str/user/user-123')
        assert response.json() == {'user_id': 'user-123', 'type': 'Safe_Id'}

        test_guid = '550e8400-e29b-41d4-a716-446655440000'
        response = client.get(f'/safe_str/resource/{test_guid}')
        assert response.json() == {'resource_guid': test_guid, 'is_valid_guid': True}

        response = client.get('/safe_str/fetch-by-name', params={'name': 'test-name**^^'})
        assert response.json() == {'name': 'test_name____', 'length': 13}

        response = client.get('/safe_str/fetch-by-url', params={'url': 'https://example.com'})
        assert response.json() == {'url': 'https://example.com', 'is_url': True}

    def test__regression__with_safe_numeric_primitives__conversion_issue(self):            # Bug test: numeric primitive conversion
        from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now import Timestamp_Now

        class Test_Routes(Fast_API__Routes):
            tag = 'numeric'

            def item__count(self, count: Safe_Int):
                return {'count': int(count), 'doubled': int(count) * 2}

            def price__amount(self, amount: Safe_Float):
                return {'price': amount, 'with_tax': amount * 1.2}

            def calc_percentage(self, value: Safe_Float, rate: Safe_Float):
                result = value * rate / 100
                return {'value': value, 'rate': rate, 'result': result}

            def events_after(self, timestamp: Timestamp_Now):
                return {'timestamp': int(timestamp), 'is_recent': int(timestamp) > 1700000000}

            def setup_routes(self):
                self.add_routes_get(self.item__count     ,
                                    self.price__amount   ,
                                    self.calc_percentage ,
                                    self.events_after    )

        class Test_Fast_API(Fast_API):
            def setup_routes(self):
                self.add_routes(Test_Routes)

        fast_api = Test_Fast_API(config=self.config).setup()
        client   = fast_api.client()

        assert fast_api.routes_paths() == sorted(['/numeric/item/{count}'     ,
                                                   '/numeric/price/{amount}'   ,
                                                   '/numeric/calc-percentage'  ,
                                                   '/numeric/events-after'     ])

        response = client.get('/numeric/item/42')
        assert response.json() == {'count': 42, 'doubled': 84}

        response = client.get('/numeric/price/99.99')
        #assert response.json() == {'price': 99.99, 'with_tax': 119.98799999999999}         # BUG
        assert response.json() == {'price': 99.99, 'with_tax': 119.988}                     # FIXED

        response = client.get('/numeric/calc-percentage', params={'value': '100', 'rate': '15.5'})
        assert response.json() == {'value': 100.0, 'rate': 15.5, 'result': 15.5}

        response = client.get('/numeric/events-after', params={'timestamp': '1735689600'})
        assert response.json() == {'timestamp': 1735689600, 'is_recent': True}

    def test__regression__post_routes__with_safe_primitives__simple_example(self):  # Regression: Safe primitives in POST routes
        class Test_Routes(Fast_API__Routes):
            tag = 'products'

            def create__product_id(self, product_id: Safe_Str):
                pass

            def update__product_id(self, product_id: Safe_Str, product: dict):
                pass

            def setup_routes(self):
                self.add_routes_post(self.create__product_id ,
                                     self.update__product_id )

        class Test_Fast_API(Fast_API):
            def setup_routes(self):
                self.add_routes(Test_Routes)

        fast_api = Test_Fast_API(config=self.config).setup()
        assert fast_api.routes_paths() == ['/products/create/{product_id}' ,
                                           '/products/update/{product_id}' ]