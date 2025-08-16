from unittest                                                          import TestCase
from osbot_fast_api.api.Fast_API                                       import Fast_API
from osbot_fast_api.api.routes.Fast_API__Routes                               import Fast_API__Routes
from osbot_fast_api.api.decorators.route_path                          import route_path
from osbot_utils.type_safe.Type_Safe                                   import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                import Safe_Str
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id     import Safe_Id
from osbot_utils.type_safe.primitives.safe_str.identifiers.Random_Guid import Random_Guid
from osbot_utils.type_safe.primitives.safe_int.Safe_Int                import Safe_Int
from osbot_utils.type_safe.primitives.safe_float.Safe_Float            import Safe_Float


class test_route_path(TestCase):

    def setUp(self):
        self.fast_api_routes = Fast_API__Routes()

    def test_route_path_decorator(self):
        @route_path("/api/v1/users.json")
        def get_users_json(): pass                                                          # Would normally be /get-users-json

        @route_path("/api/v2/user/{id}/profile.html")
        def user_profile_html(id: str): pass                                                # Explicit path with extension

        @route_path("/legacy/API/GetUser")                                                  # Maintain legacy uppercase path
        def get_user_legacy(user_id: str): pass

        @route_path("/files/{filename}.{extension}")                                        # Multiple path params with dots
        def download_file(filename: str, extension: str): pass

        def normal__route__parsing(self): pass                                              # Still works without decorator

        with self.fast_api_routes as _:
            _.add_routes_get(get_users_json      ,
                            user_profile_html    ,
                            get_user_legacy      ,
                            download_file        ,
                            normal__route__parsing)

            assert _.routes_paths() == sorted(['/api/v1/users.json'              ,
                                               '/api/v2/user/{id}/profile.html'   ,
                                               '/legacy/API/GetUser'              ,
                                               '/files/{filename}.{extension}'    ,
                                               '/normal/route/parsing'            ])

    def test_route_path_with_primitive_types(self):
        @route_path("/user/{user_id}/balance")
        def get_balance(user_id: Safe_Id, include_pending: bool = False):
            return {'user_id': str(user_id), 'balance': 100.50, 'pending': include_pending}

        @route_path("/api/v1/resource/{guid}.json")
        def get_resource_json(guid: Random_Guid):
            return {'resource_id': str(guid), 'format': 'json'}

        @route_path("/calc/percentage/{value}/{rate}")
        def calculate_percentage(value: Safe_Float, rate: Safe_Float):
            result = float(value) * float(rate) / 100
            return {'value': float(value), 'rate': float(rate), 'result': result}

        @route_path("/items/page/{page_num}/size/{page_size}")
        def get_paginated_items(page_num: Safe_Int, page_size: Safe_Int):
            return {'page': int(page_num), 'size': int(page_size), 'total': int(page_num) * int(page_size)}

        with self.fast_api_routes as _:
            _.add_routes_get(get_balance          ,
                            get_resource_json     ,
                            calculate_percentage  ,
                            get_paginated_items   )

            assert _.routes_paths() == sorted(['/user/{user_id}/balance'                ,
                                               '/api/v1/resource/{guid}.json'           ,
                                               '/calc/percentage/{value}/{rate}'        ,
                                               '/items/page/{page_num}/size/{page_size}'])

    def test_route_path_with_type_safe_post(self):
        class User_Data(Type_Safe):
            name  : Safe_Str
            email : Safe_Str
            age   : Safe_Int

        class Product_Update(Type_Safe):
            price    : Safe_Float
            quantity : Safe_Int
            sku      : Random_Guid

        @route_path("/api/v2/users/create.json")
        def create_user_json(user: User_Data):
            return {'created': True, 'name': str(user.name), 'format': 'json'}

        @route_path("/products/{product_id}/update")
        def update_product(product_id: Random_Guid, update: Product_Update):
            return {'id': str(product_id), 'new_price': float(update.price)}

        @route_path("/LEGACY/API/UpdateUserProfile")                                        # Legacy uppercase endpoint
        def legacy_update_profile(user_id: Safe_Id, profile: User_Data):
            return {'legacy': True, 'user': str(user_id), 'updated': str(profile.name)}

        with self.fast_api_routes as _:
            _.add_routes_post(create_user_json      ,
                             update_product         ,
                             legacy_update_profile  )

            assert _.routes_paths() == sorted(['/api/v2/users/create.json'       ,
                                               '/products/{product_id}/update'    ,
                                               '/LEGACY/API/UpdateUserProfile'    ])

    def test_edge_cases_and_special_patterns(self):
        @route_path("/")                                                                    # Root path
        def root_handler(): pass

        @route_path("//double//slash")                                                      # Double slashes (will be normalized by most servers)
        def double_slash(): pass

        @route_path("/path/with spaces/and-special_chars!@")                                # Special characters
        def special_chars(): pass

        @route_path("/very/deep/nested/path/structure/with/many/segments/endpoint.xml")     # Deep nesting
        def deep_path(): pass

        @route_path("/../relative/path")                                                    # Relative path (potentially dangerous)
        def relative_path(): pass

        @route_path("/path/{param1}/{param2}/{param3}/{param4}/{param5}")                   # Many parameters
        def many_params(param1: str, param2: str, param3: str, param4: str, param5: str): pass

        @route_path("/mixed_{style}/path-{id}/file.{ext}")                                  # Mixed naming styles
        def mixed_styles(style: str, id: Safe_Id, ext: str): pass

        with self.fast_api_routes as _:
            _.add_routes_get(root_handler   ,
                            double_slash    ,
                            special_chars   ,
                            deep_path       ,
                            relative_path   ,
                            many_params     ,
                            mixed_styles    )

            assert _.routes_paths() == sorted(['/'                                                            ,
                                               '//double//slash'                                              ,
                                               '/path/with spaces/and-special_chars!@'                       ,
                                               '/very/deep/nested/path/structure/with/many/segments/endpoint.xml',
                                               '/../relative/path'                                           ,
                                               '/path/{param1}/{param2}/{param3}/{param4}/{param5}'          ,
                                               '/mixed_{style}/path-{id}/file.{ext}'                         ])

    def test_mixing_decorated_and_auto_generated(self):
        @route_path("/custom/path")
        def custom_route(): pass

        def auto__generated__route(self): pass                                              # Will auto-generate

        @route_path("/override/auto/generation")
        def should__be__auto__generated(self): pass                                         # Decorator overrides auto-generation

        def another__auto_route__with_param(self, param: Safe_Str): pass                    # Auto with param

        @route_path("/files/{user_id}/{filename}.pdf")
        def download__user__file(self, user_id: Safe_Id, filename: str): pass               # Decorator overrides complex auto-generation

        with self.fast_api_routes as _:
            _.add_routes_get(custom_route                    ,
                            auto__generated__route           ,
                            should__be__auto__generated      ,
                            another__auto_route__with_param  ,
                            download__user__file             )

            assert _.routes_paths() == sorted(['/custom/path'                           ,
                                               '/auto/generated/route'                  ,
                                               '/override/auto/generation'              ,  # Decorator wins
                                               '/another/auto-route/with-param'         ,  # Auto-generated (no param in path)
                                               '/files/{user_id}/{filename}.pdf'        ])  # Decorator wins

    def test_with_fast_api_client_integration(self):
        class Test_Routes(Fast_API__Routes):
            tag = 'api'

            @route_path("/v1/users.json")
            def get_users_json(self):
                return {'users': ['alice', 'bob'], 'format': 'json'}

            @route_path("/v2/user/{user_id}/profile.xml")
            def get_user_profile_xml(self, user_id: Safe_Id):
                return {'user_id': str(user_id), 'format': 'xml', 'name': 'User Name'}

            @route_path("/download/{filename}.{ext}")
            def download_file(self, filename: str, ext: str):
                return {'file': f"{filename}.{ext}", 'size': 1024}

            @route_path("/calc/tax/{amount}")
            def calculate_tax(self, amount: Safe_Float, rate: Safe_Float = Safe_Float(0.1)):
                tax = float(amount) * float(rate)
                return {'amount': float(amount), 'rate': float(rate), 'tax': tax}

            def normal__auto__route(self, param: Safe_Str):                                # Mix in auto-generated
                return {'method': 'auto', 'param': str(param)}

            def setup_routes(self):
                self.add_routes_get(self.get_users_json         ,
                                   self.get_user_profile_xml    ,
                                   self.download_file           ,
                                   self.calculate_tax           ,
                                   self.normal__auto__route      )

        class Test_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(Test_Routes)

        fast_api = Test_Fast_API().setup()
        client   = fast_api.client()

        # Test routes are correctly generated
        assert fast_api.routes_paths() == sorted(['/api/v1/users.json'              ,
                                                  '/api/v2/user/{user_id}/profile.xml',
                                                  '/api/download/{filename}.{ext}'    ,
                                                  '/api/calc/tax/{amount}'            ,
                                                  '/api/normal/auto/route'            ])

        # Test actual calls
        response = client.get('/api/v1/users.json')
        assert response.json() == {'users': ['alice', 'bob'], 'format': 'json'}

        response = client.get('/api/v2/user/user-123/profile.xml')
        assert response.json() == {'user_id': 'user-123', 'format': 'xml', 'name': 'User Name'}

        response = client.get('/api/download/report.pdf')
        assert response.json() == {'file': 'report.pdf', 'size': 1024}

        response = client.get('/api/calc/tax/100', params={'rate': '0.15'})
        assert response.json() == {'amount': 100.0, 'rate': 0.15, 'tax': 15.0}

        response = client.get('/api/normal/auto/route', params={'param': 'test-value**!!'})
        assert response.json() == {'method': 'auto', 'param': 'test_value____'}

    def test_post_routes_with_decorator_and_type_safe(self):
        class Order_Item(Type_Safe):
            product_id : Random_Guid
            quantity   : Safe_Int
            price      : Safe_Float

        class Order_Request(Type_Safe):
            customer_id : Safe_Id
            items       : list[Order_Item]
            notes       : Safe_Str

        class Test_Routes(Fast_API__Routes):
            tag = 'orders'

            @route_path("/api/v3/orders/create.json")
            def create_order_json(self, order: Order_Request):
                total = sum(float(item.price) * int(item.quantity) for item in order.items)
                return {'customer': str(order.customer_id), 'total': total, 'format': 'json'}

            @route_path("/LEGACY/CreateOrder")                                              # Legacy uppercase
            def legacy_create_order(self, customer_id: Safe_Id, order: Order_Request):
                return {'legacy': True, 'customer': str(customer_id), 'items': len(order.items)}

            @route_path("/orders/{order_id}/items/{item_id}/update.json")
            def update_order_item(self, order_id: Random_Guid, item_id: Random_Guid, quantity: Safe_Int):
                return {'order': str(order_id), 'item': str(item_id), 'new_quantity': int(quantity)}

            def setup_routes(self):
                self.add_routes_post(self.create_order_json    ,
                                    self.legacy_create_order   ,
                                    self.update_order_item     )

        class Test_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(Test_Routes)

        fast_api = Test_Fast_API().setup()
        client   = fast_api.client()

        # Test routes
        assert fast_api.routes_paths() == sorted(['/orders/api/v3/orders/create.json'              ,
                                                  '/orders/legacy/createorder'                     ,            # the path is always converted to lower (via the Safe_Str__FastAPI__Route__Prefix conversion)
                                                  '/orders/orders/{order_id}/items/{item_id}/update.json'])

        # Test POST with complex Type_Safe
        order_data = Order_Request(
            customer_id = Safe_Id('cust-456'),
            items       = [Order_Item(product_id = Random_Guid('111e8400-e29b-41d4-a716-446655440001'),
                                     quantity   = Safe_Int(2),
                                     price      = Safe_Float(29.99))],
            notes       = Safe_Str('Rush delivery')
        )

        response = client.post('/orders/api/v3/orders/create.json', json=order_data.json())
        assert response.json() == {'customer': 'cust-456', 'total': 59.98, 'format': 'json'}

    def test_conflicting_paths_and_overrides(self):
        @route_path("/users/{id}")
        def method_one(id: str): pass

        @route_path("/users/{id}")                                                          # Same path, different function
        def method_two(id: str): pass

        @route_path("/items/list")
        def items__list(self): pass                                                         # Would auto-generate to /items/list anyway

        @route_path("/completely/different/path")
        def expected__to__be__elsewhere(self): pass                                         # Completely override expected path

        with self.fast_api_routes as _:
            _.add_routes_get(method_one                   ,
                            method_two                    ,  # This will override method_one
                            items__list                   ,
                            expected__to__be__elsewhere   )

            # Note: method_two wins for /users/{id} due to registration order
            assert _.routes_paths() == sorted(['/users/{id}'                  ,  # Only one registration
                                               '/items/list'                   ,
                                               '/completely/different/path'   ])

    def test_decorator_with_query_params_not_in_path(self):
        @route_path("/search")                                                              # Query params not in path
        def search_items(q: str, limit: Safe_Int = Safe_Int(10), offset: Safe_Int = Safe_Int(0)):
            return {'query': q, 'limit': int(limit), 'offset': int(offset)}

        @route_path("/api/v1/data.csv")                                                     # Fixed path, params in query
        def export_data_csv(start_date: str, end_date: str, format: str = 'csv'):
            return {'start': start_date, 'end': end_date, 'format': format}

        with self.fast_api_routes as _:
            _.add_routes_get(search_items    ,
                            export_data_csv  )

            assert _.routes_paths() == sorted(['/search'           ,
                                               '/api/v1/data.csv'  ])