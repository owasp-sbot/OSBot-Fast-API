import re
from unittest import TestCase

import pytest
from fastapi.exceptions import FastAPIError
from osbot_utils.type_safe.primitives.safe_str.Safe_Str import Safe_Str

from osbot_fast_api.api.Fast_API         import Fast_API
from osbot_fast_api.api.Fast_API__Routes import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe     import Type_Safe


class test_Fast_API__Routes__path_parsing(TestCase):

    def setUp(self):
        self.fast_api_routes = Fast_API__Routes()

    def test_add_routes__simple_examples(self):
        def no_params   (   ): pass
        def no__vars    (   ): pass
        def an__var     (var): pass
        def an_post     (abc:dict): pass
        def an__user_id (user_id, abc: dict): pass
        def an__user__id(user   , abc: dict): pass

        with self.fast_api_routes as _:
            _.add_routes_get(no_params    ,
                             no__vars     ,
                             an__var      )
            _.add_routes_post(an_post     ,
                              an__user_id ,
                              an__user__id)
            assert _.routes_paths()  == ['/no-params', '/no/vars', '/an/{var}',
                                         '/an-post', '/an/{user_id}', '/an/{user}/id']

    def test_edge_cases__underscores_and_hyphens(self):
        def api_v1__data            (self                       ): pass                  # Simple with underscore
        def api_v2__user_profile    (self                       ): pass                  # Multiple underscores
        def get__user_id            (user_id                    ): pass                  # Param matches exactly
        def get__user_profile_id    (user_profile_id            ): pass                  # Long param name
        def fetch__user_profile_id  (user                       ): pass                  # Param matches {user}
        def update__profile_user_id (profile_user_id, data: dict): pass                  # Complex param name

        with self.fast_api_routes as _:
            _.add_routes_get(api_v1__data              ,
                            api_v2__user_profile       ,
                            get__user_id               ,
                            get__user_profile_id       ,
                            fetch__user_profile_id     )
            _.add_route_post(update__profile_user_id)

            assert _.routes_paths() == ['/api-v1/data'                  ,
                                       '/api-v2/user-profile'           ,
                                       '/get/{user_id}'                 ,
                                       '/get/{user_profile_id}'          ,
                                       '/fetch/{user}/profile-id'         ,
                                       '/update/{profile_user_id}'       ]

    def test_multiple_path_segments(self):
        def api__v1__users(self): pass                                                  # Multiple segments, no params
        def api__v1__user(user): pass                                                   # With param
        def api__v1__user__posts(user): pass                                            # Param in middle
        def api__v1__user__post(user, post): pass                                       # Multiple params
        def api__user_profile__post_details(user, post): pass                           # Mixed underscores
        def get__user_id__profile__settings(user_id): pass                              # Long path with param

        with self.fast_api_routes as _:
            _.add_routes_get(api__v1__users                 ,
                            api__v1__user                   ,
                            api__v1__user__posts            ,
                            api__v1__user__post             ,
                            api__user_profile__post_details ,
                            get__user_id__profile__settings )

            assert _.routes_paths() == ['/api/v1/users'                          ,
                                        '/api/v1/{user}'                         ,
                                        '/api/v1/{user}/posts'                   ,
                                        '/api/v1/{user}/{post}'                  ,
                                        '/api/{user}/profile/{post}/details'     ,
                                        '/get/{user_id}/profile/settings'        ]

    def test_confusing_parameter_names(self):
        def get__id                      (id             ): pass            # '/get/{id}'
        def get__id_user                 (id             ): pass            # '/get/{id}/user'
        def get__id__user                (id             ): pass            # '/get/{id}/user'                  (same as above)
        def fetch__user_id_profile       (user_id        ): pass            # '/fetch/user-id-profile'          (with _profile, doesn't detect user_id)
        def fetch__user_id__profile      (user_id        ): pass            # '/fetch/{user_id}/profile'        (with __profile, it does)
        def update__user_profile_id_data (user_profile_id): pass            # '/update/user-profile-id-data'    (with _data, doesn't detect user_profile_id)
        def update__user_profile_id__data(user_profile_id): pass            # '/update/{user_profile_id}/data'  (with __data , it does)

        with self.fast_api_routes as _:
            _.add_routes_get (get__id                       ,
                              get__id_user                  ,
                              get__id__user                 ,
                              fetch__user_id_profile        ,
                              fetch__user_id__profile       )
            _.add_routes_post(update__user_profile_id_data  ,
                              update__user_profile_id__data )

            # Note: get__id_user appears twice with different params, last one wins
            assert _.routes_paths() == [ '/get/{id}'                        ,
                                         '/get/{id}/user'                   ,
                                         '/fetch/user-id-profile'           ,
                                         '/fetch/{user_id}/profile'         ,
                                         '/update/user-profile-id-data'     ,
                                         '/update/{user_profile_id}/data'  ]

    def test_empty_and_special_cases(self):
        def __(self): pass                                                              # Just double underscore
        def a__(self): pass                                                             # Ends with double underscore
        def __b(self): pass                                                             # Starts with double underscore
        def a____b(self): pass                                                          # Multiple double underscores
        def api__(self): pass                                                           # Trailing double underscore
        def __user__(user): pass                                                        # Param surrounded by __

        with self.fast_api_routes as _:
            _.add_routes_get(__         ,
                             a__        ,
                             __b        ,
                             a____b     ,
                             api__      ,
                             __user__)

            assert _.routes_paths() == ['/'      ,                                      # Empty first part
                                        '/a'     ,                                      # Empty after __
                                        '/b'     ,                                      # Empty before __
                                        '/a/b'   ,                                      # Empty middle segment
                                        '/api'   ,                                      # Trailing empty
                                        '/{user}']                                      # Param with empty around

    def test_with_fast_api_client__get_routes(self):
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
                self.add_routes_get(self.users                      ,
                                    self.user__id                   ,
                                    self.user_profile__profile_name ,
                                    self.api__v1__resource_id       )

        class Test_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(Test_Routes)

        fast_api = Test_Fast_API().setup()
        client   = fast_api.client()

        # Test the routes are correctly generated
        assert fast_api.routes_paths() == sorted([ '/test/users'                      ,
                                                   '/test/user/{id}'                  ,
                                                   '/test/user-profile/{profile_name}',
                                                   '/test/api/v1/{resource_id}'       ])

        # Test actual calls
        assert client.get('/test/users'                ).json()  == {'users': ['alice', 'bob']}
        assert client.get('/test/user/123'             ).json()  == {'user_id': '123'}
        assert client.get('/test/user-profile/john-doe').json()  == {'profile': 'john-doe'}
        assert client.get('/test/api/v1/resource-99'   ).json()  == {'resource': 'resource-99', 'version': 'v1'}

    def test_with_fast_api_client__post_routes_with_body(self):
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
                self.add_routes_post(self.create__user                 ,
                                     self.update__user_id              ,
                                     self.patch__user_profile__setting )

        class Test_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(Test_Routes)

        fast_api = Test_Fast_API().setup()
        client   = fast_api.client()

        # Test routes are correctly generated
        assert fast_api.routes_paths() == sorted(['/api/create/user'                    ,
                                                  '/api/update/{user_id}'               ,
                                                  '/api/patch/{user_profile}/{setting}' ])

        # Test actual calls
        user_data = User_Data(name='Alice', email='alice@test.com')

        response = client.post('/api/create/user', json=user_data.json())
        assert response.json() == {'created': True, 'name': 'Alice'}

        response = client.post('/api/update/user-123', json=user_data.json())
        assert response.json() == {'updated': True, 'id': 'user-123', 'email': 'alice@test.com'}

        response = client.post('/api/patch/alice-profile/notifications', json={'enabled': True})
        assert response.json() == {'profile': 'alice-profile', 'setting': 'notifications', 'data': {'enabled': True}}

    def test_mixed_methods_same_path_pattern(self):
        class Test_Routes(Fast_API__Routes):
            tag = 'resource'

            def item__id(self, id: str):                                                # GET
                return {'action': 'get', 'id': id}

            def item__id_post(self, id: str, data: dict):                               # POST (different name)
                return {'action': 'create', 'id': id, 'data': data}

            def item__id_put(self, id: str, data: dict):                                # PUT
                return {'action': 'update', 'id': id, 'data': data}

            def item__id_delete(self, id: str):                                         # DELETE
                return {'action': 'delete', 'id': id}

            def setup_routes(self):
                self.add_route_get(self.item__id)
                self.add_route_post(self.item__id_post)
                self.add_route_put(self.item__id_put)
                self.add_route_delete(self.item__id_delete)

        class Test_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(Test_Routes)

        fast_api = Test_Fast_API().setup()
        client   = fast_api.client()

        # All methods create different routes due to different function names
        assert fast_api.routes_paths() == sorted(['/resource/item/{id}'        ,
                                                  '/resource/item/{id}/post'     ,
                                                  '/resource/item/{id}/put'      ,
                                                  '/resource/item/{id}/delete'   ])

        # Test different HTTP methods
        assert client.get('/resource/item/123').json()                        == {'action': 'get', 'id': '123'}
        assert client.post('/resource/item/123/post', json={'a': 1}).json()   == {'action': 'create', 'id': '123', 'data': {'a': 1}}
        assert client.put('/resource/item/123/put', json={'b': 2}).json()     == {'action': 'update', 'id': '123', 'data': {'b': 2}}
        assert client.delete('/resource/item/123/delete').json()              == {'action': 'delete', 'id': '123'}

    def test_numeric_and_special_patterns(self):
        def api__v1          (self): pass                                                         # Version number
        def api__v2_beta     (self): pass                                                    # Version with suffix
        def item__123        (self): pass                                                       # Numeric literal
        def get__user_123    (self, user_123): pass                                         # Numeric in param
        def fetch__id_123_456(self, id_123_456): pass                                   # Multiple numbers

        with self.fast_api_routes as _:
            _.add_routes_get(api__v1               ,
                            api__v2_beta           ,
                            item__123              ,
                            get__user_123          ,
                            fetch__id_123_456      )

            assert _.routes_paths() == ['/api/v1'                    ,
                                        '/api/v2-beta'               ,
                                        '/item/123'                  ,                   # Numeric literal (no param named 123)
                                        '/get/{user_123}'            ,
                                        '/fetch/{id_123_456}'        ]

    def test_with_safe_str_primitives(self):
        from osbot_utils.type_safe.primitives.safe_str.Safe_Str                                  import Safe_Str
        from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                       import Safe_Id
        from osbot_utils.type_safe.primitives.safe_str.identifiers.Random_Guid                   import Random_Guid
        from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__Url                         import Safe_Str__Url

        class Test_Routes(Fast_API__Routes):
            tag = 'safe_str'

            def user__id(self, id: Safe_Id):                                                     # Path param with Safe_Id
                return {'user_id': str(id), 'type': type(id).__name__}

            def resource__guid(self, guid: Random_Guid):                                         # Path param with Random_Guid
                return {'resource_guid': str(guid), 'is_valid_guid': len(str(guid)) == 36}

            def fetch_by_name(self, name: Safe_Str):                                             # Query param with Safe_Str
                return {'name': str(name), 'length': len(str(name))}

            def fetch_by_url(self, url: Safe_Str__Url):                                          # Query param with Safe_Str__Url
                return {'url': str(url), 'is_url': str(url).startswith('http')}

            def setup_routes(self):
                self.add_routes_get(self.user__id         ,
                                   self.resource__guid    ,
                                   self.fetch_by_name     ,
                                   self.fetch_by_url      )

        class Test_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(Test_Routes)

        fast_api = Test_Fast_API().setup()
        client   = fast_api.client()

        # Test routes generation
        assert fast_api.routes_paths() ==sorted( ['/safe_str/user/{id}'       ,
                                                  '/safe_str/resource/{guid}' ,
                                                  '/safe_str/fetch-by-name'   ,
                                                  '/safe_str/fetch-by-url'    ])

        # Test actual calls with Safe_Str types
        response = client.get('/safe_str/user/user-123')
        assert response.json() == {'user_id': 'user-123', 'type': 'Safe_Id'}

        test_guid = '550e8400-e29b-41d4-a716-446655440000'
        response = client.get(f'/safe_str/resource/{test_guid}')
        assert response.json() == {'resource_guid': test_guid, 'is_valid_guid': True}

        response = client.get('/safe_str/fetch-by-name', params={'name': 'test-name**^^'})
        assert response.json() == {'name': 'test_name____', 'length': 13}

        response = client.get('/safe_str/fetch-by-url', params={'url': 'https://example.com'})
        assert response.json() == {'url': 'https://example.com', 'is_url': True}

    def test___bug__with_safe_numeric_primitives__conversion_issue(self):
        from osbot_utils.type_safe.primitives.safe_int.Safe_Int                                  import Safe_Int
        from osbot_utils.type_safe.primitives.safe_float.Safe_Float                              import Safe_Float
        from osbot_utils.type_safe.primitives.safe_int.Timestamp_Now                             import Timestamp_Now

        class Test_Routes(Fast_API__Routes):
            tag = 'numeric'

            def item__count(self, count: Safe_Int):                                              # Path param with Safe_Int
                return {'count': int(count), 'doubled': int(count) * 2}

            def price__amount(self, amount: Safe_Float):                                         # Path param with Safe_Float
                return {'price': float(amount), 'with_tax': float(amount) * 1.2}

            def calc_percentage(self, value: Safe_Float, rate: Safe_Float):                      # Multiple query params
                result = float(value) * float(rate) / 100
                return {'value': float(value), 'rate': float(rate), 'result': result}

            def events_after(self, timestamp: Timestamp_Now):                                    # Query param with Timestamp
                return {'timestamp': int(timestamp), 'is_recent': int(timestamp) > 1700000000}

            def setup_routes(self):
                self.add_routes_get(self.item__count        ,
                                    self.price__amount      ,
                                    self.calc_percentage    ,
                                    self.events_after       )

        class Test_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(Test_Routes)

        fast_api = Test_Fast_API().setup()
        client   = fast_api.client()

        # Test routes generation
        assert fast_api.routes_paths() == sorted(['/numeric/item/{count}'    ,
                                                  '/numeric/price/{amount}'  ,
                                                  '/numeric/calc-percentage' ,
                                                  '/numeric/events-after'    ])

        # Test actual calls
        response = client.get('/numeric/item/42')
        assert response.json() == {'count': 42, 'doubled': 84}

        response = client.get('/numeric/price/99.99')
        assert response.json() == {'price': 99.99, 'with_tax': 119.98799999999999   }       # BUG: this value 119.98799999999999 , should be 119.987

        response = client.get('/numeric/calc-percentage', params={'value': '100', 'rate': '15.5'})
        assert response.json() == {'value': 100.0, 'rate': 15.5, 'result': 15.5}

        response = client.get('/numeric/events-after', params={'timestamp': '1735689600'})
        assert response.json() == {'timestamp': 1735689600, 'is_recent': True}

    def test_post_routes_with_safe_primitives(self):
        from osbot_utils.type_safe.primitives.safe_str.Safe_Str                                  import Safe_Str
        from osbot_utils.type_safe.primitives.safe_str.identifiers.Random_Guid                   import Random_Guid
        from osbot_utils.type_safe.primitives.safe_int.Safe_Int                                  import Safe_Int
        from osbot_utils.type_safe.primitives.safe_float.Safe_Float                              import Safe_Float

        class Product_Data(Type_Safe):
            name     : Safe_Str
            price    : Safe_Float
            quantity : Safe_Int
            sku      : Random_Guid

        class Test_Routes(Fast_API__Routes):
            tag = 'products'

            def create__product(self, product_data: Product_Data):
                return { 'created'  : True                   ,
                         'name'     : str  (product_data.name)       ,
                         'price'    : float(product_data.price)    ,
                         'quantity' : int  (product_data.quantity)   ,
                         'sku'      : str  (product_data.sku)        }

            def update__product_id(self, product_id: Random_Guid, product: Product_Data):
                return { 'updated'    : True                   ,
                        'product_id' : str(product_id)        ,
                        'new_price'  : float(product.price)   ,
                        'new_qty'    : int(product.quantity)  }

            def adjust__store_id__adjustment(self, store_id: Safe_Int, adjustment: Safe_Int, product: Product_Data):
                new_qty = int(product.quantity) + int(adjustment)
                return { 'store_id'     : int(store_id)          ,
                         'adjustment'   : int(adjustment)         ,
                         'old_quantity' : int(product.quantity)   ,
                         'new_quantity' : new_qty                 }

            def setup_routes(self):
                self.add_routes_post(self.create__product              ,
                                     self.update__product_id           ,
                                     self.adjust__store_id__adjustment )

        class Test_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(Test_Routes)

        fast_api = Test_Fast_API().setup()
        client   = fast_api.client()

        # Test routes generation
        assert fast_api.routes_paths() == sorted(['/products/create/product'                  ,
                                                  '/products/update/{product_id}'              ,
                                                  '/products/adjust/{store_id}/{adjustment}'   ])

        # Create test data with Safe primitives
        product_data = Product_Data(
            name     = Safe_Str('Premium Widget')                        ,
            price    = Safe_Float(49.99)                                 ,
            quantity = Safe_Int(100)                                     ,
            sku      = Random_Guid('550e8400-e29b-41d4-a716-446655440000')
        )

        # Test POST with Type_Safe containing Safe primitives
        response = client.post('/products/create/product', json=product_data.json())
        assert response.json() == { 'created'  : True                                      ,
                                   'name'     : 'Premium_Widget'                          ,
                                   'price'    : 49.99                                      ,
                                   'quantity' : 100                                        ,
                                   'sku'      : '550e8400-e29b-41d4-a716-446655440000'    }

        # Test with path param as Random_Guid
        product_id = '660e8400-e29b-41d4-a716-446655440001'
        response = client.post(f'/products/update/{product_id}', json=product_data.json())
        assert response.json() == { 'updated'    : True         ,
                                   'product_id' : product_id    ,
                                   'new_price'  : 49.99          ,
                                   'new_qty'    : 100            }

        # Test with multiple path params including Safe_Int
        response = client.post('/products/adjust/5/25', json=product_data.json())
        assert response.json() == { 'store_id'     : 5    ,
                                   'adjustment'   : 25   ,
                                   'old_quantity' : 100  ,
                                   'new_quantity' : 125  }

    def test_mixed_safe_primitives_complex_scenario(self):
        from osbot_utils.type_safe.primitives.safe_str.Safe_Str                                  import Safe_Str
        from osbot_utils.type_safe.primitives.safe_str.identifiers.Random_Guid                   import Random_Guid
        from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                       import Safe_Id
        from osbot_utils.type_safe.primitives.safe_int.Safe_Int                                  import Safe_Int
        from osbot_utils.type_safe.primitives.safe_float.Safe_Float                              import Safe_Float
        from osbot_utils.type_safe.primitives.safe_int.Timestamp_Now                             import Timestamp_Now

        class Order_Item(Type_Safe):
            item_id  : Random_Guid
            quantity : Safe_Int
            price    : Safe_Float

        class Order_Data(Type_Safe):
            customer_id : Safe_Id
            items       : list[Order_Item]
            timestamp   : Timestamp_Now
            notes       : Safe_Str

        class Test_Routes(Fast_API__Routes):
            tag = 'orders'

            def get__customer_id__order_id(self, customer_id: Safe_Id, order_id: Random_Guid):
                return { 'customer' : str(customer_id)  ,
                        'order'    : str(order_id)      ,
                        'found'    : True                }

            def create__store_id__order(self, store_id: Safe_Int, order_data: Order_Data):
                total = sum(float(item.price) * int(item.quantity) for item in order_data.items)
                return { 'store_id'    : int(store_id)              ,
                        'customer_id' : str(order_data.customer_id)     ,
                        'items_count' : len(order_data.items)           ,
                        'total'       : total                      ,
                        'timestamp'   : int(order_data.timestamp)       ,
                        'notes'       : str(order_data.notes)           }

            def calculate_discount(self, amount: Safe_Float, discount_pct: Safe_Float, min_order: Safe_Float = Safe_Float(0)):
                if float(amount) >= float(min_order):
                    discount = float(amount) * float(discount_pct) / 100
                    final = float(amount) - discount
                else:
                    discount = 0
                    final = float(amount)
                return { 'amount'       : float(amount)        ,
                        'discount_pct' : float(discount_pct)  ,
                        'min_order'    : float(min_order)     ,
                        'discount'     : discount              ,
                        'final'        : final                 }

            def setup_routes(self):
                self.add_route_get(self.get__customer_id__order_id)
                self.add_route_get(self.calculate_discount)
                self.add_route_post(self.create__store_id__order)

        class Test_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(Test_Routes)

        fast_api = Test_Fast_API().setup()

        client   = fast_api.client()

        # Test routes
        assert fast_api.routes_paths() == sorted(['/orders/get/{customer_id}/{order_id}'  ,
                                                  '/orders/calculate-discount'            ,
                                                  '/orders/create/{store_id}/order'       ])

        # Test GET with multiple Safe path params
        response = client.get('/orders/get/cust-123/550e8400-e29b-41d4-a716-446655440000')
        assert response.json() == { 'customer' : 'cust-123'                                ,
                                   'order'    : '550e8400-e29b-41d4-a716-446655440000'    ,
                                   'found'    : True                                       }

        # Test GET with query params including default Safe_Float
        response = client.get('/orders/calculate-discount', params={'amount': '100', 'discount_pct': '15'})
        assert response.json() == { 'amount'       : 100.0  ,
                                   'discount_pct' : 15.0   ,
                                   'min_order'    : 0.0    ,
                                   'discount'     : 15.0   ,
                                   'final'        : 85.0   }

        # Test with min_order specified
        response = client.get('/orders/calculate-discount', params={'amount': '50', 'discount_pct': '15', 'min_order': '75'})
        assert response.json() == { 'amount'       : 50.0  ,
                                   'discount_pct' : 15.0  ,
                                   'min_order'    : 75.0  ,
                                   'discount'     : 0     ,
                                   'final'        : 50.0  }

        # Test POST with nested Safe primitives
        order_data = Order_Data(
            customer_id = Safe_Id('cust-456')                          ,
            items       = [ Order_Item(item_id  = Random_Guid('111e8400-e29b-41d4-a716-446655440001')  ,
                                      quantity = Safe_Int(2)                                           ,
                                      price    = Safe_Float(29.99))                                    ,
                           Order_Item(item_id  = Random_Guid('222e8400-e29b-41d4-a716-446655440002')  ,
                                      quantity = Safe_Int(1)                                           ,
                                      price    = Safe_Float(49.99))                                    ],
            timestamp   = Timestamp_Now(1735689600)                    ,
            notes       = Safe_Str('Rush delivery requested!!!***')
        )

        response = client.post('/orders/create/3/order', json=order_data.json())
        assert response.json() == { 'store_id'    : 3                             ,
                                   'customer_id' : 'cust-456'                     ,
                                   'items_count' : 2                              ,
                                   'total'       : 109.97                         ,  # 2*29.99 + 1*49.99
                                   'timestamp'   : 1735689600                     ,
                                   'notes'       : 'Rush_delivery_requested______'} # Str_Safe changed spaces, ! and * into _

    def test_confusing_parameter_names__with_explanations(self):
        """
        The parser's logic for segments after '__':
        1. First checks if the ENTIRE segment matches a parameter name
        2. If not, checks if it contains '_' and splits on first underscore
        3. After split, checks if first part is a parameter

        This creates predictable but sometimes surprising behavior.
        """

        def get__id                      (id             ): pass            # '/get/{id}'                       - 'id' matches param exactly
        def get__id_user                 (id             ): pass            # '/get/{id}/user'                  - 'id_user' split → 'id' matches, 'user' is literal
        def get__id__user                (id             ): pass            # '/get/{id}/user'                  - '__' makes separate segments, 'id' matches param
        def fetch__user_id_profile       (user_id        ): pass            # '/fetch/user-id-profile'          - 'user_id_profile' != 'user_id', split on '_' → 'user' != 'user_id'
        def fetch__user_id__profile      (user_id        ): pass            # '/fetch/{user_id}/profile'        - '__' makes separate segments, 'user_id' matches param
        def update__user_profile_id_data (user_profile_id): pass            # '/update/user-profile-id-data'    - 'user_profile_id_data' != 'user_profile_id', becomes literal
        def update__user_profile_id__data(user_profile_id): pass            # '/update/{user_profile_id}/data'  - '__' makes separate segments, 'user_profile_id' matches

        with self.fast_api_routes as _:
            _.add_routes_get (get__id                       ,
                              get__id_user                  ,
                              get__id__user                 ,
                              fetch__user_id_profile        ,
                              fetch__user_id__profile       )
            _.add_routes_post(update__user_profile_id_data  ,
                              update__user_profile_id__data )

            assert _.routes_paths() == [ '/get/{id}'                        ,
                                         '/get/{id}/user'                   ,       # todo: see how to detect and raise exception when two functions point to the same path, in this case get__id_user and get__id__user
                                         '/fetch/user-id-profile'           ,
                                         '/fetch/{user_id}/profile'         ,
                                         '/update/user-profile-id-data'     ,
                                         '/update/{user_profile_id}/data'  ]

    def test_parameter_matching_rules(self):
        """
        Test to clearly demonstrate the parameter matching rules:
        Rule 1: Exact match takes precedence
        Rule 2: Split on '_' only if no exact match
        Rule 3: Double underscore '__' always creates segment boundary
        """

        # Rule 1: Exact match examples
        def exact__user_id       (user_id       ): pass    # '/exact/{user_id}'         - exact match
        def exact__user_id_extra (user_id_extra ): pass    # '/exact/{user_id_extra}'   - NOW it's exact match

        # Rule 2: Split on underscore when no exact match
        def split__user_profile  (user_profile  ): pass    # '/split/{user_profile}'    - exact match, no split needed

        # Rule 3: Double underscore creates boundaries
        def boundary__user__profile__data(user, profile): pass    # '/boundary/{user}/{profile}/data'
        def boundary__user_profile__data (user_profile ): pass    # '/boundary/{user_profile}/data'
        def boundary__user__profile_data (user         ): pass    # '/boundary/{user}/profile-data'

        with self.fast_api_routes as _:
            _.add_routes_get(exact__user_id                ,
                            exact__user_id_extra           ,
                            split__user_profile            ,
                            boundary__user__profile__data  ,
                            boundary__user_profile__data   ,
                            boundary__user__profile_data   )

            # Results show the clear pattern
            assert _.routes_paths() == ['/exact/{user_id}'                  ,
                                       '/exact/{user_id_extra}'             ,  # Last registration with matching param
                                       '/split/{user_profile}'              ,  # Last registration with matching param
                                       '/boundary/{user}/{profile}/data'    ,
                                       '/boundary/{user_profile}/data'      ,
                                       '/boundary/{user}/profile-data'      ]

    def test_best_practices_for_clear_routes(self):
        """
        Best practices to avoid confusion:
        1. Use '__' to clearly separate path segments
        2. Match parameter names exactly to avoid ambiguity
        3. Use descriptive parameter names
        """

        # GOOD: Clear segment separation
        def api__v1__users__id__profile(self, id): pass              # Clear: /api/v1/users/{id}/profile
        def api__v1__users__user_id__profile(self, user_id): pass    # Clear: /api/v1/users/{user_id}/profile

        # AVOID: Ambiguous parameter placement
        def api__user_id_profile(self, user_id): pass                # Confusing: /api/user-id-profile (not a param!)

        # BETTER: Use double underscore
        def api__user_id__profile(self, user_id): pass               # Clear: /api/{user_id}/profile

        # GOOD: Parameter name matches segment exactly
        def get__customer_order_id(self, customer_order_id): pass    # Clear: /get/{customer_order_id}

        # AVOID: Parameter is substring of segment
        def get__customer_order_id_details(self, customer_order_id): pass  # Confusing: /get/customer-order-id-details

        # BETTER: Separate with double underscore
        def get__customer_order_id__details(self, customer_order_id): pass # Clear: /get/{customer_order_id}/details

        with self.fast_api_routes as _:
            _.add_routes_get(api__v1__users__id__profile          ,
                            api__v1__users__user_id__profile      ,
                            api__user_id_profile                   ,
                            api__user_id__profile                  ,
                            get__customer_order_id                 ,
                            get__customer_order_id_details         ,
                            get__customer_order_id__details        )

            assert _.routes_paths() == ['/api/v1/users/{id}/profile'              ,
                                       '/api/v1/users/{user_id}/profile'          ,
                                       '/api/user-id-profile'                     ,  # Not what you might expect!
                                       '/api/{user_id}/profile'                   ,  # This is clearer
                                       '/get/{customer_order_id}'                 ,
                                       '/get/customer-order-id-details'           ,  # Not what you might expect!
                                       '/get/{customer_order_id}/details'         ]  # This is clearer

    def test_underscore_parameter_detection_rules(self):
        """
        Parameter Detection Rules:

        1. SINGLE underscore (param_suffix): AUTO-DETECTS if param exists
           Example: 'user_id' with param 'user' → '{user}/id'

        2. MULTIPLE underscores (param_with_underscores): NEEDS exact match or '__' separator
           Example: 'user_id_profile' with param 'user_id' → 'user-id-profile' (NOT detected)
           Example: 'user_id__profile' with param 'user_id' → '{user_id}/profile' (detected)

        3. EXACT MATCH: Always works regardless of underscores
           Example: 'user_profile_id' with param 'user_profile_id' → '{user_profile_id}'
        """

        # SINGLE UNDERSCORE - Auto-detection works
        def fetch__user_id       (user         ): pass    # '/fetch/{user}/id'        ✓ Auto-detected
        def fetch__order_status  (order        ): pass    # '/fetch/{order}/status'   ✓ Auto-detected
        def fetch__item_count    (item         ): pass    # '/fetch/{item}/count'     ✓ Auto-detected

        # MULTIPLE UNDERSCORES - Need exact match or '__'
        def get__user_id_profile (user_id_profile): pass  # '/get/{user_id_profile}'  ✓ Exact match works!
        def get__user_id__profile(user_id      ): pass    # '/get/{user_id}/profile'  ✓ Using __ works!

        # EXACT MATCH - Always works
        def process__long_param_name     (long_param_name      ): pass    # '/process/{long_param_name}'       ✓
        def process__very_long_param_name(very_long_param_name ): pass    # '/process/{very_long_param_name}'  ✓
        def process__id_123_456          (id_123_456           ): pass    # '/process/{id_123_456}'            ✓

        with self.fast_api_routes as _:
            _.add_routes_get(fetch__user_id                   ,
                            fetch__order_status               ,
                            fetch__item_count                 ,
                            get__user_id_profile              ,  # With user_id_profile param
                            get__user_id__profile             ,
                            process__long_param_name          ,
                            process__very_long_param_name     ,
                            process__id_123_456               )

            assert _.routes_paths() == ['/fetch/{user}/id'                  ,
                                       '/fetch/{order}/status'              ,
                                       '/fetch/{item}/count'                ,
                                       '/get/{user_id_profile}'              ,  # Exact match
                                       '/get/{user_id}/profile'              ,  # With __
                                       '/process/{long_param_name}'          ,
                                       '/process/{very_long_param_name}'     ,
                                       '/process/{id_123_456}'               ]

    def test_pattern_summary(self):
        """
        Summary of patterns:

        Pattern                     | Param      | Result                      | Detection
        ----------------------------|------------|-----------------------------|-----------
        func__abc_xyz              | abc        | /func/{abc}/xyz             | ✓ Auto
        func__abc_xyz              | xyz        | /func/abc-xyz               | ✗ No match
        func__abc_xyz              | abc_xyz    | /func/{abc_xyz}             | ✓ Exact
        func__abc_xyz_123          | abc        | /func/abc-xyz-123           | ✗ Multiple _
        func__abc_xyz_123          | abc_xyz    | /func/abc-xyz-123           | ✗ Not exact
        func__abc_xyz_123          | abc_xyz_123| /func/{abc_xyz_123}         | ✓ Exact
        func__abc_xyz__123         | abc_xyz    | /func/{abc_xyz}/123         | ✓ With __
        func__abc__xyz__123        | abc, xyz   | /func/{abc}/{xyz}/123       | ✓ Multiple __
        """

        # Single underscore patterns
        def single__abc_xyz          (abc        ): pass    # '{abc}/xyz'         - Auto-detect works
        def single__user_profile     (user       ): pass    # '{user}/profile'    - Auto-detect works

        # Multiple underscore patterns - need help
        def multi__abc_xyz_123       (abc        ): pass    # 'abc-xyz-123'       - Too many underscores
        def multi__user_profile_data (user       ): pass    # 'user-profile-data' - Too many underscores

        # Solutions for multiple underscores
        def solution1__abc_xyz_123   (abc_xyz_123): pass    # '{abc_xyz_123}'     - Exact match
        def solution2__abc_xyz__123  (abc_xyz    ): pass    # '{abc_xyz}/123'     - Use __ separator
        def solution3__user__profile_data(user   ): pass    # '{user}/profile-data' - Use __ separator

        with self.fast_api_routes as _:
            _.add_routes_get(single__abc_xyz               ,
                             single__user_profile           ,
                             multi__abc_xyz_123             ,
                             multi__user_profile_data       ,
                             solution1__abc_xyz_123         ,
                             solution2__abc_xyz__123        ,
                             solution3__user__profile_data  )

            assert sorted(_.routes_paths()) ==sorted( ['/single/{abc}/xyz'               ,  # ✓ Auto-detected
                                                       '/single/{user}/profile'          ,  # ✓ Auto-detected
                                                       '/multi/{abc}/xyz-123'       ,
                                                       '/multi/{user}/profile-data' ,
                                                       '/solution1/{abc_xyz_123}'        ,  # ✓ Exact match
                                                       '/solution2/{abc_xyz}/123'        ,  # ✓ With __
                                                       '/solution3/{user}/profile-data'  ])  # ✓ With __

    def test_bug__practical_examples__two_methods_create_same_path(self):
        """
        Real-world practical examples showing when to use '__'
        """

        # API versioning with parameters
        def api_v1__user_profile     (user        ): pass    # '/api-v1/{user}/profile'      ✓ Works
        def api_v2__user_profile_data(user        ): pass    # '/api-v2/user-profile-data'   ✗ Needs help
        def api_v2__user__profile_data(user       ): pass    # '/api-v2/{user}/profile-data' ✓ Fixed with __

        # Resource with complex IDs
        def get__order_2024_001      (order_2024_001): pass  # '/get/{order_2024_001}'       ✓ Exact match
        #def get__order_2024_001      (order        ): pass   # '/get/order-2024-001'         ✗ Not detected
        def get__order__2024_001     (order        ): pass   # '/get/{order}/2024-001'       ✓ With __ separator

        # Nested resources
        def fetch__company_dept_id   (company      ): pass   # '/fetch/{company}/dept-id'    ✓ Single _ works
        def fetch__company_dept_id_mgr(company     ): pass   # '/fetch/company-dept-id-mgr'  ✗ Multiple _ fails
        def fetch__company__dept_id_mgr(company    ): pass   # '/fetch/{company}/dept-id-mgr'✓ __ helps

        with self.fast_api_routes as _:
            _.add_routes_get(api_v1__user_profile         ,
                            api_v2__user_profile_data     ,
                            api_v2__user__profile_data    ,
                            get__order_2024_001           ,  # With exact match param
                            get__order__2024_001          ,
                            fetch__company_dept_id        ,
                            fetch__company_dept_id_mgr    , # BUG: creates '/fetch/{company}/dept-id-mgr'
                            fetch__company__dept_id_mgr   ) # BUG: creates '/fetch/{company}/dept-id-mgr'  (todo: this should not be allowed, since this could cause subtle bugs)

            assert sorted(_.routes_paths()) ==sorted( ['/api-v1/{user}/profile'         ,
                                                       '/api-v2/{user}/profile-data'     ,  # Fixed!
                                                       '/get/{order_2024_001}'           ,
                                                       '/get/{order}/2024-001'           ,
                                                       '/fetch/{company}/dept-id'        ,
                                                       '/fetch/{company}/dept-id-mgr'    ])  # BUG: two methods create same path: fetch__company_dept_id_mgr and fetch__company__dept_id_mgr

    def test__regression__post_routes__with_safe_primitives__simple_example(self):

        class Test_Routes(Fast_API__Routes):
            tag = 'products'

            def create__product_id(self, product_id: Safe_Str): pass                        # FIXED: BUG   also fails here
            def update__product_id(self, product_id: Safe_Str, product: dict): pass         # FIXED:BUG  Fails here



            def setup_routes(self):
                self.add_routes_post(self.create__product_id,
                                     self.update__product_id)


        class Test_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(Test_Routes)

        #error_message = "Invalid args for response field! Hint: check that <class 'osbot_utils.type_safe.primitives.safe_str.Safe_Str.Safe_Str'> is a valid Pydantic field type. If you are using a return type annotation that is not a valid Pydantic field (e.g. Union[Response, dict, None]) you can disable generating the response model from the type annotation with the path operation decorator parameter response_model=None. Read more: https://fastapi.tiangolo.com/tutorial/response-model/"
        #with pytest.raises(FastAPIError, match=re.escape(error_message)):
        #    Test_Fast_API().setup()                                         # BUG : should had not raised exception

        assert Test_Fast_API().setup().routes_paths() == ['/products/create/{product_id}',      # FIXED
                                                          '/products/update/{product_id}']      # FIXED
