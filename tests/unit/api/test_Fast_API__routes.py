from unittest                                                                   import TestCase
from osbot_fast_api.api.Fast_API                                                import Fast_API
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Email      import Safe_Str__Email
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id               import Safe_Id
from osbot_fast_api.api.decorators.route_path                                   import route_path


class test_Fast_API__routes(TestCase):
    def setUp(self):
        self.fast_api = Fast_API().setup()
        self.client   = self.fast_api.client()

    def test_add_route(self):                                                       # Test add_route with Type_Safe support
        def test_endpoint():
            return {"status": "ok"}

        with self.fast_api as _:
            result = _.add_route(test_endpoint, methods=['GET'])

            assert result is _                                                      # Method chaining
            assert '/test-endpoint' in _.routes_paths()

            response = _.client().get('/test-endpoint')
            assert response.status_code == 200
            assert response.json()      == {"status": "ok"}

    def test_add_route_get(self):                                                   # Test add_route_get with Type_Safe support
        def get_data():
            return {"data": [1, 2, 3]}

        with self.fast_api as _:
            result = _.add_route_get(get_data)

            assert result is _
            assert '/get-data' in _.routes_paths()

            response = _.client().get('/get-data')
            assert response.status_code == 200
            assert response.json()      == {"data": [1, 2, 3]}

    def test_add_route_post(self):                                                  # Test add_route_post with Type_Safe support
        def create_item(data: dict):
            return {"created": True, "data": data}

        with self.fast_api as _:
            result = _.add_route_post(create_item)

            assert result is _
            assert '/create-item' in _.routes_paths()

            response = _.client().post('/create-item', json={"name": "test"})
            assert response.status_code == 200
            assert response.json()      == {"created": True, "data": {"name": "test"}}

    def test_add_route_put(self):                                                   # Test add_route_put with Type_Safe support
        def update_item(data: dict):
            return {"updated": True, "data": data}

        with self.fast_api as _:
            result = _.add_route_put(update_item)

            assert result is _
            assert '/update-item' in _.routes_paths()

            response = _.client().put('/update-item', json={"name": "updated"})
            assert response.status_code == 200
            assert response.json()      == {"updated": True, "data": {"name": "updated"}}

    def test_add_route_delete(self):                                                # Test add_route_delete with Type_Safe support
        def delete_item():
            return {"deleted": True}

        with self.fast_api as _:
            result = _.add_route_delete(delete_item)

            assert result is _
            assert '/delete-item' in _.routes_paths()

            response = _.client().delete('/delete-item')
            assert response.status_code == 200
            assert response.json()      == {"deleted": True}

    def test_add_route__with_type_safe_params(self):                                # Test with Type_Safe parameters

        class User_Data(Type_Safe):
            name  : Safe_Str
            email : Safe_Str__Email

        def create_user(user_data: User_Data):
            return {"name": str(user_data.name), "email": str(user_data.email)}

        with self.fast_api as _:
            _.add_route_post(create_user)

            response = _.client().post('/create-user', json={"name": "Alice", "email": "alice@test.com"})
            assert response.status_code == 200
            assert response.json()      == {"name": "Alice", "email": "alice@test.com"}

    def test_add_route__with_path_params(self):                                     # Test with path parameters

        def get__user_id(user_id: Safe_Id):
            return {"user_id": str(user_id)}

        with self.fast_api as _:
            _.add_route_get(get__user_id)

            assert '/get/{user_id}' in _.routes_paths()

            response = _.client().get('/get/user-123')
            assert response.status_code == 200
            assert response.json()      == {"user_id": "user-123"}

    def test_add_route__with_route_path_decorator(self):                            # Test @route_path decorator support
        @route_path("/api/v1/custom")
        def custom_endpoint():
            return {"custom": True}

        with self.fast_api as _:
            _.add_route_get(custom_endpoint)

            assert '/api/v1/custom' in _.routes_paths()

            response = _.client().get('/api/v1/custom')
            assert response.status_code == 200
            assert response.json()      == {"custom": True}

    def test_add_route__multiple_methods(self):                                     # Test route with multiple HTTP methods
        def handle_resource():
            return {"handled": True}

        with self.fast_api as _:
            _.add_route(handle_resource, methods=['GET', 'POST', 'PUT'])

            assert '/handle-resource' in _.routes_paths()

            # Test all methods work
            assert _.client().get   ('/handle-resource').status_code  == 200
            assert _.client().post  ('/handle-resource').status_code  == 200
            assert _.client().put   ('/handle-resource').status_code  == 200
            assert _.client().delete('/handle-resource').status_code  == 405  # Not allowed

    def test_add_route__method_chaining(self):                                      # Test method chaining for multiple routes
        def endpoint_1():
            return {"id": 1}

        def endpoint_2():
            return {"id": 2}

        def endpoint_3():
            return {"id": 3}

        with self.fast_api as _:
            result = (_.add_route_get(endpoint_1)
                       .add_route_post(endpoint_2)
                       .add_route_put(endpoint_3))

            assert result is _
            assert '/endpoint-1' in _.routes_paths()
            assert '/endpoint-2' in _.routes_paths()
            assert '/endpoint-3' in _.routes_paths()