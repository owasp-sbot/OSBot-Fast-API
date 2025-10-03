from unittest                                                import TestCase
from osbot_fast_api.admin_ui.api.routes.Routes__Admin__Docs  import Routes__Admin__Docs
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Objs import setup__admin_ui_test_objs, cleanup_admin_ui_test_objs
from osbot_fast_api.api.routes.Fast_API__Routes              import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe                         import Type_Safe
from osbot_utils.utils.Objects                               import base_types
from osbot_utils.utils.Misc                                  import list_set


class test_Routes__Admin__Docs(TestCase):
    """Test Routes__Admin__Docs class directly"""

    @classmethod
    def setUpClass(cls):
        """Setup routes instance"""
        cls.test_objs = setup__admin_ui_test_objs(with_parent=True)
        cls.routes_docs = Routes__Admin__Docs()
        cls.routes_docs.parent_app = cls.test_objs.parent_fast_api

    @classmethod
    def tearDownClass(cls):
        """Cleanup"""
        cleanup_admin_ui_test_objs(cls.test_objs)

    def test_01_setUpClass(self):
        """Verify class setup and inheritance"""
        with self.routes_docs as _:
            assert type(_) is Routes__Admin__Docs
            assert Fast_API__Routes in base_types(_)
            assert Type_Safe in base_types(_)
            assert _.tag == 'admin-docs'
            assert _.parent_app is not None

    def test_02_api__docs_endpoints(self):
        """Test docs endpoints listing"""
        result = self.routes_docs.api__docs_endpoints()

        assert isinstance(result, list)
        assert len(result) == 6  # Should have 6 doc endpoints

        # Check endpoint structure
        for endpoint in result:
            assert 'name' in endpoint
            assert 'description' in endpoint
            assert 'url' in endpoint
            assert 'type' in endpoint
            assert 'icon' in endpoint

        # Check specific endpoints
        endpoint_types = [e['type'] for e in result]
        assert 'swagger' in endpoint_types
        assert 'redoc' in endpoint_types
        assert 'openapi' in endpoint_types
        assert 'client' in endpoint_types
        assert 'routes' in endpoint_types
        assert 'admin' in endpoint_types

        # Verify Swagger endpoint
        swagger = next(e for e in result if e['type'] == 'swagger')
        assert swagger['name'] == 'Swagger UI'
        assert swagger['url'] == '/docs'
        assert swagger['icon'] == 'swagger'

        # Verify ReDoc endpoint
        redoc = next(e for e in result if e['type'] == 'redoc')
        assert redoc['url'] == '/redoc'

    def test_03_api__client_examples(self):
        """Test client code examples"""
        result = self.routes_docs.api__client_examples()

        assert isinstance(result, dict)
        assert len(result) == 3  # curl, python, javascript

        # Check curl example
        assert 'curl' in result
        curl = result['curl']
        assert curl['name'] == 'cURL'
        assert 'curl' in curl['example']
        assert '/config/status' in curl['example']
        assert '/admin/api/cookie/set' in curl['example']

        # Check Python example
        assert 'python' in result
        python = result['python']
        assert python['name'] == 'Python'
        assert 'import requests' in python['example']
        assert 'response.json()' in python['example']

        # Check JavaScript example
        assert 'javascript' in result
        js = result['javascript']
        assert js['name'] == 'JavaScript'
        assert 'fetch' in js['example']
        assert 'then' in js['example']

    def test_04_api__api_info(self):
        """Test API metadata retrieval"""
        result = self.routes_docs.api__api_info()

        assert isinstance(result, dict)

        # Check expected fields
        expected_fields = [
            'openapi_version',
            'api_title',
            'api_version',
            'api_description',
            'servers',
            'total_paths',
            'total_schemas',
            'tags'
        ]
        assert list_set(result.keys()) == sorted(expected_fields)

        # Verify values
        assert result['api_title'       ] == 'Test Parent API'
        assert result['api_version'     ] == 'v1.0.99'
        assert result['api_description' ] == 'Parent API for Admin UI testing'
        assert result['total_paths'     ] > 0
        assert isinstance(result['tags' ], list)

    # def test_05_api__api_info_no_parent(self):                # this is not a realistic scenario any more
    #     """Test API info without parent app"""
    #     routes = Routes__Admin__Docs()
    #     routes.parent_app = None
    #
    #     result = routes.api__api_info()
    #
    #     assert result == {"error": "Parent app not configured"}

    def test_06_extract_tags(self):
        """Test tag extraction from OpenAPI spec"""
        # Create a mock OpenAPI spec
        mock_spec = {
            'paths': {
                '/users': {
                    'get': {'tags': ['users'], 'summary': 'Get users'},
                    'post': {'tags': ['users'], 'summary': 'Create user'}
                },
                '/items': {
                    'get': {'tags': ['items'], 'summary': 'Get items'}
                },
                '/admin/info': {
                    'get': {'tags': ['admin', 'info'], 'summary': 'Admin info'}
                }
            },
            'tags': [
                {'name': 'users', 'description': 'User operations'},
                {'name': 'items', 'description': 'Item operations'}
            ]
        }

        routes = self.routes_docs
        tags = routes._extract_tags(mock_spec)

        assert isinstance(tags, list)
        assert len(tags) >= 2

        # Check tag structure
        for tag in tags:
            assert 'name' in tag
            assert 'count' in tag
            assert 'paths' in tag

        # Check users tag
        users_tag = next((t for t in tags if t['name'] == 'users'), None)
        if users_tag:
            assert users_tag['count'] == 2
            assert len(users_tag['paths']) == 2
            assert users_tag.get('description') == 'User operations'