import re
from unittest                                                import TestCase
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Objs import setup__admin_ui_test_objs, cleanup_admin_ui_test_objs


class test_Routes__Admin__Cookies__client(TestCase):            # Test Routes__Admin__Cookies via TestClient

    @classmethod
    def setUpClass(cls):
        """Setup with client"""
        cls.test_objs = setup__admin_ui_test_objs(with_parent=True)
        cls.client = cls.test_objs.admin_client

    @classmethod
    def tearDownClass(cls):
        """Cleanup"""
        cleanup_admin_ui_test_objs(cls.test_objs)

    def test_01_get_cookies_list(self):
        """Test GET /api/cookies-list"""
        # Set some cookies first
        self.client.cookies['test-cookie'] = 'test-value'
        self.client.cookies['openai-api-key'] = 'sk-' + 'x' * 48

        response = self.client.get('/admin-cookies/api/cookies-list')

        assert response.status_code == 200
        cookies = response.json()

        assert isinstance(cookies, list)

        # Find test cookie in list
        test_cookie = next((c for c in cookies if c['name'] == 'test-cookie'), None)
        if test_cookie:  # May not exist if not in templates
            assert test_cookie['has_value'] is True
            assert test_cookie['value_length'] == len('test-value')

        # Find OpenAI cookie
        openai_cookie = next((c for c in cookies if c['name'] == 'openai-api-key'), None)
        assert openai_cookie is not None
        assert openai_cookie['has_value'] is True
        assert openai_cookie['is_valid'] is True
        assert openai_cookie['required'] is True
        assert openai_cookie['category'] == 'llm'

    def test_02_get_cookie_templates(self):
        """Test GET /api/cookies-templates"""
        response = self.client.get('/admin-cookies/api/cookies-templates')

        assert response.status_code == 200
        templates = response.json()

        assert len(templates) == 1

        # Verify template structure
        for template in templates:
            assert 'id' in template
            assert 'name' in template
            assert 'description' in template
            assert 'cookies' in template
            assert isinstance(template['cookies'], list)

    def test_03_get_specific_cookie(self):
        """Test GET /api/cookie-get/{cookie_name}"""
        # Set a cookie
        self.client.cookies['auth-token'] = 'test-token-123'

        response = self.client.get('/admin-cookies/api/cookie-get/auth-token')

        assert response.status_code == 200
        data = response.json()

        assert data['name'] == 'auth-token'
        assert data['value'] == 'test-token-123'
        assert data['exists'] is True
        assert data['is_valid'] is True

        # Test non-existent cookie
        response = self.client.get('/admin-cookies/api/cookie-get/non-existent')
        data = response.json()

        assert data['name'] == 'non-existent'
        assert data['value'] is None
        assert data['exists'] is False

    def test_04_set_cookie(self):
        """Test POST /api/cookie-set/{cookie_name}"""
        cookie_data = { 'value'     : 'new-test-value',
                        'expires_in': 3600            }

        response = self.client.post('/admin-cookies/api/cookie-set/test-cookie', json=cookie_data)

        assert response.status_code == 200
        data = response.json()

        assert data['success'] is True
        assert data['name'] == 'test-cookie'
        assert data['value_set'] is True

        # Verify cookie was set in response
        assert 'test-cookie' in response.cookies

    def test_05_set_cookie_with_validation(self):
        """Test setting cookie with validation"""
        # Try to set invalid OpenAI key
        invalid_data = {'value': 'invalid-key' , 'expires_in': 3600 }

        response = self.client.post('/admin-cookies/api/cookie-set/openai-api-key', json=invalid_data)

        assert response.status_code == 200
        data = response.json()

        assert data['success'] is False
        assert 'error' in data
        assert 'does not match required pattern' in data['error']

        # Set valid OpenAI key
        valid_data = { 'value'     : 'sk-' + 'a' * 48,
                       'expires_in': 3600            }

        response = self.client.post('/admin-cookies/api/cookie-set/openai-api-key', json=valid_data)
        data = response.json()

        assert data['success'] is True
        assert data['name'] == 'openai-api-key'

    def test_06_delete_cookie(self):
        """Test DELETE /api/cookie-delete/{cookie_name}"""
        # Set a cookie first
        self.client.cookies['to-delete'] = 'delete-me'

        response = self.client.delete('/admin-cookies/api/cookie-delete/to-delete')

        assert response.status_code == 200
        data = response.json()

        assert data['success'] is True
        assert data['name'   ] == 'to-delete'
        assert data['deleted'] is True

    def test_07__bulk_set_cookies(self):
        """Test POST /api/cookies-bulk-set"""
        cookies_data = {'cookies': [ {'name': 'cookie1'       , 'value': 'value1'         , 'expires_in': 0},
                                     {'name': 'cookie2'       , 'value': 'value2'         , 'expires_in': 0},
                                     {'name': 'openai-api-key', 'value': 'sk-' + 'b' * 48 , 'expires_in': 0}]}


        response = self.client.post('/admin-cookies/api/cookies-bulk-set', json=cookies_data)



        assert response.status_code == 200

        data = response.json()
        assert data == { 'results': [  {'name': 'cookie1'       , 'success': True, 'value_set': True},
                                       {'name': 'cookie2'       , 'success': True, 'value_set': True},
                                       {'name': 'openai-api-key', 'success': True, 'value_set': True}],
                          'success': True}

    def test_08_generate_values(self):
        """Test GET /api/generate-value"""
        # Generate UUID
        response = self.client.get('/admin-cookies/api/generate-value/uuid')

        assert response.status_code == 200
        data = response.json()

        assert data['type'] == 'uuid'
        assert len(data['value']) == 36

        # Verify it's a valid UUID format
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        assert re.match(uuid_pattern, data['value'])

        # Generate API key
        response = self.client.get('/admin-cookies/api/generate-value/api_key')
        data = response.json()

        assert data['type'] == 'api_key'
        assert data['value'].startswith('sk-')


