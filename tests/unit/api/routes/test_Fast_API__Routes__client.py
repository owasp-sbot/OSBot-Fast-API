from unittest                                                 import TestCase
from fastapi                                                  import Request

from osbot_fast_api.schemas.Schema__Fast_API__Config import Schema__Fast_API__Config
from osbot_utils.type_safe.Type_Safe                          import Type_Safe
from osbot_fast_api.api.Fast_API                              import Fast_API
from osbot_fast_api.api.routes.Fast_API__Routes               import Fast_API__Routes
from osbot_fast_api.schemas.safe_str.Safe_Str__Fast_API__Route__Prefix import Safe_Str__Fast_API__Route__Prefix


class test_Fast_API__Routes__client(TestCase):

    def setUp(self):
        # Create a Fast_API instance and a custom routes class
        self.config   = Schema__Fast_API__Config(default_routes=False)      # Disable default routes for cleaner testing
        self.fast_api = Fast_API        (config=self.config)
        self.app      = self.fast_api.app()
        self.client   = self.fast_api.client()

        # Create a routes instance
        self.routes   = Routes__Examples(app=self.app)
        self.routes.setup()

    def test_get_routes(self):
        response = self.client.get('/routes-examples/hello')
        assert response.status_code == 200
        assert response.json() == {"message": "Hello from GET"}

        response = self.client.get('/routes-examples/data')
        assert response.status_code == 200
        assert response.json() == {"data": [1, 2, 3]}

    def test_post_routes(self):
        response = self.client.post('/routes-examples/create', json={"name": "test", "value": 42})
        assert response.status_code == 200
        assert response.json() == {"created": True, "item": {"name": "test", "value": 42}}

        # Test POST without body
        response = self.client.post('/routes-examples/action')
        assert response.status_code == 200
        assert response.json() == {"action": "performed"}

    def test_put_routes(self):
        response = self.client.put('/routes-examples/update/123', json={"name": "updated"})
        assert response.status_code == 200
        assert response.json() == {"updated": True, "id": 123, "data": {"name": "updated"}}

    def test_delete_routes(self):
        response = self.client.delete('/routes-examples/item/456')
        assert response.status_code == 200
        assert response.json() == {"deleted": True, "id": 456}

    def test_route_any_without_path(self):
        # Test ANY route with default path parsing
        for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            if method == 'GET':
                response = self.client.get('/routes-examples/any-method')
            elif method == 'POST':
                response = self.client.post('/routes-examples/any-method')
            elif method == 'PUT':
                response = self.client.put('/routes-examples/any-method')
            elif method == 'DELETE':
                response = self.client.delete('/routes-examples/any-method')
            elif method == 'PATCH':
                response = self.client.patch('/routes-examples/any-method')

            assert response.status_code == 200
            assert response.json()["method"] == method

    def test_route_any_with_catch_all_path(self):                                   # Test proxy-style catch-all route
        test_paths = [  '/routes-examples/proxy/simple',
                        '/routes-examples/proxy/deep/nested/path',
                        '/routes-examples/proxy/with-dashes-and_underscores',
                        '/routes-examples/proxy/123/456/789']

        for test_path in test_paths:                                                # Test different HTTP methods
            response = self.client.get(test_path)
            assert response.status_code == 200
            expected_path = test_path.replace('/routes-examples/proxy/', '')
            assert response.json() == {"method": "GET", "proxied_path": expected_path}

            response = self.client.post(test_path, json={"data": "test"})
            assert response.status_code == 200
            assert response.json()["method"] == "POST"
            assert response.json()["proxied_path"] == expected_path

    def test_path_parameters(self):
        # Test routes with path parameters
        response = self.client.get('/routes-examples/user/alice')
        assert response.status_code == 200
        assert response.json() == {"user_id": "alice"}

        response = self.client.get('/routes-examples/user/alice/post/123')
        assert response.status_code == 200
        assert response.json() == {"user_id": "alice", "post_id": 123}

    def test_routes_with_request_object(self):
        # Test route that accesses request directly
        response = self.client.get('/routes-examples/request-info', headers={"X-Custom-Header": "test-value"})
        assert response.status_code == 200
        result = response.json()
        assert result["method"] == "GET"
        assert result["path"] == "/routes-examples/request-info"
        assert "x-custom-header" in result["headers"]  # Headers are lowercase in request

    def test_multiple_routes_methods(self):
        # Test add_routes_get, add_routes_post, etc.
        response = self.client.get('/routes-examples/multi1')
        assert response.status_code == 200
        assert response.json() == {"endpoint": "multi1"}

        response = self.client.get('/routes-examples/multi2')
        assert response.status_code == 200
        assert response.json() == {"endpoint": "multi2"}

    def test_404_for_nonexistent_routes(self):
        response = self.client.get('/routes-examples/nonexistent')
        assert response.status_code == 404

        # Test wrong method for a route
        response = self.client.post('/routes-examples/hello')  # This is a GET-only route
        assert response.status_code == 405  # Method Not Allowed

    def test__regression__path_path_colon_was_lost(self):
        with self.fast_api as _:
            routes_paths = _.routes_paths()
            assert  Safe_Str__Fast_API__Route__Prefix('/routes-examples/proxy/{path_path}') not in routes_paths   # FIXED: BUG should not be there (path_path was sanitized by Safe_Str__Fast_API__Route__Prefix)
            assert  Safe_Str__Fast_API__Route__Prefix('/routes-examples/proxy/{path:path}') in     routes_paths   # FIXED: ok but false positive
            assert                                    '/routes-examples/proxy/{path_path}'  not in routes_paths   # FIXED: BUG should not be there
            assert                                    '/routes-examples/proxy/{path:path}'  in     routes_paths   # FIXED: BUG should be there

class Schema__Multiple_Examples__Base(Type_Safe):
    name : str

class Schema__Multiple_Examples__Create(Schema__Multiple_Examples__Base):
    value: int

class Routes__Examples(Fast_API__Routes):            # Test routes class with various endpoint types
    tag = 'routes-examples'

    def setup_routes(self):
        # GET routes
        self.add_route_get(self.hello)
        self.add_route_get(self.data)
        self.add_route_get(self.user__user_id)
        self.add_route_get(self.user__user_id__post__post_id)
        self.add_route_get(self.request_info)

        # POST routes
        self.add_route_post(self.create)
        self.add_route_post(self.action)

        # PUT route
        self.add_route_put(self.update__id)

        # DELETE route
        self.add_route_delete(self.item__id)

        # ANY routes
        self.add_route_any(self.any_method)
        self.add_route_any(self.proxy, "/proxy/{path:path}")

        # Multiple routes at once
        self.add_routes_get(self.multi1, self.multi2)

    # Route implementations
    def hello(self):
        return {"message": "Hello from GET"}

    def data(self):
        return {"data": [1, 2, 3]}

    def create(self, create: Schema__Multiple_Examples__Create):
        return {"created": True, "item": {"name": create.name, "value": create.value}}

    def action(self):
        return {"action": "performed"}

    def update__id(self, id: int, base: Schema__Multiple_Examples__Base):
        return {"updated": True, "id": id, "data": {"name": base.name}}

    def item__id(self, id: int):
        return {"deleted": True, "id": id}

    def any_method(self, request: Request):
        return {"method": request.method, "path": request.url.path}

    def proxy(self, request: Request, path: str):
        return {"method": request.method, "proxied_path": path}

    def user__user_id(self, user_id: str):
        return {"user_id": user_id}

    def user__user_id__post__post_id(self, user_id: str, post_id: int):
        return {"user_id": user_id, "post_id": post_id}

    def request_info(self, request: Request):
        return {
            "method": request.method,
            "path": str(request.url.path),
            "headers": dict(request.headers)
        }

    def multi1(self):
        return {"endpoint": "multi1"}

    def multi2(self):
        return {"endpoint": "multi2"}