from unittest                                                import TestCase
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Objs import setup__admin_ui_test_objs, cleanup_admin_ui_test_objs


class test_Routes__Admin__Docs__client(TestCase):       # Test Routes__Admin__Docs via TestClient"""

    @classmethod
    def setUpClass(cls):
        """Setup with client"""
        cls.test_objs = setup__admin_ui_test_objs(with_parent=True)
        cls.client = cls.test_objs.admin_client

    @classmethod
    def tearDownClass(cls):
        """Cleanup"""
        cleanup_admin_ui_test_objs(cls.test_objs)

    def test_01_get_docs_endpoints(self):
        """Test GET /api/docs-endpoints"""
        response = self.client.get('/admin-docs/api/docs-endpoints')

        assert response.status_code == 200
        endpoints = response.json()

        assert isinstance(endpoints, list)
        assert len(endpoints) == 6

        # Verify all expected endpoints present
        endpoint_names = [e['name'] for e in endpoints]
        assert 'Swagger UI' in endpoint_names
        assert 'ReDoc' in endpoint_names
        assert 'OpenAPI JSON' in endpoint_names
        assert 'Python Client' in endpoint_names
        assert 'Routes HTML' in endpoint_names
        assert 'Admin UI' in endpoint_names

        # Check URLs are correct
        swagger = next(e for e in endpoints if e['name'] == 'Swagger UI')
        assert swagger['url'] == '/docs'
        assert swagger['type'] == 'swagger'

    def test_02_get_client_examples(self):
        """Test GET /api/client-examples"""
        response = self.client.get('/admin-docs/api/client-examples')

        assert response.status_code == 200
        examples = response.json()

        assert 'curl' in examples
        assert 'python' in examples
        assert 'javascript' in examples

        # Verify curl example content
        curl_example = examples['curl']['example']
        assert 'curl http://localhost:8000/config/status' in curl_example
        assert 'curl -X POST' in curl_example
        assert 'Content-Type: application/json' in curl_example

        # Verify Python example content
        python_example = examples['python']['example']
        assert 'import requests' in python_example
        assert "requests.get('http://localhost:8000/config/status')" in python_example
        assert "requests.post(" in python_example
        assert "json={'value': 'your-api-key'}" in python_example

        # Verify JavaScript example content
        js_example = examples['javascript']['example']
        assert "fetch('http://localhost:8000/config/status')" in js_example
        assert "method: 'POST'" in js_example
        assert "JSON.stringify({value: 'your-api-key'})" in js_example

    def test_03_get_api_info(self):
        """Test GET /api/api-info"""
        response = self.client.get('/admin-docs/api/api-info')

        assert response.status_code == 200
        info = response.json()

        # Check all expected fields present
        required_fields = [
            'openapi_version', 'api_title', 'api_version',
            'api_description', 'servers', 'total_paths',
            'total_schemas', 'tags'
        ]
        for field in required_fields:
            assert field in info, f"Missing field: {field}"

        # Verify API metadata
        assert info['api_title'] == 'Test Parent API'
        assert info['api_version'] == 'v1.0.99'
        assert info['openapi_version'].startswith('3.')

        # Check paths and schemas
        assert info['total_paths'] > 0
        assert isinstance(info['total_schemas'], int)

        # Check tags
        assert isinstance(info['tags'], list)
        if len(info['tags']) > 0:
            tag = info['tags'][0]
            assert 'name' in tag
            assert 'count' in tag
            assert 'paths' in tag

    def test_04_docs_endpoints_structure(self):
        """Test structure of docs endpoints"""
        response = self.client.get('/admin-docs/api/docs-endpoints')
        endpoints = response.json()

        # Each endpoint should have complete information
        for endpoint in endpoints:
            assert 'name' in endpoint
            assert 'description' in endpoint
            assert 'url' in endpoint
            assert 'type' in endpoint
            assert 'icon' in endpoint

            # URLs should be valid
            assert endpoint['url'].startswith('/')

            # Icons should be meaningful
            assert len(endpoint['icon']) > 0

            # Types should be specific
            assert endpoint['type'] in [
                'swagger', 'redoc', 'openapi',
                'client', 'routes', 'admin'
            ]

    def test_05_client_examples_completeness(self):
        """Test that client examples are complete and valid"""
        response = self.client.get('/admin-docs/api/client-examples')
        examples = response.json()

        # Each language should have complete info
        for lang in ['curl', 'python', 'javascript']:
            assert lang in examples
            lang_info = examples[lang]

            assert 'name' in lang_info
            assert 'description' in lang_info
            assert 'example' in lang_info

            # Examples should be non-empty
            assert len(lang_info['example']) > 100

            # Examples should include multiple operations
            example_code = lang_info['example']
            assert '/config/status' in example_code  # GET example
            assert '/admin/api/' in example_code     # Admin API example
            assert 'POST' in example_code or 'post' in example_code
