from unittest                                                import TestCase
from osbot_utils.utils.Misc                                  import random_guid
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Objs import setup__admin_ui_test_objs, cleanup_admin_ui_test_objs


class test_Routes__Admin__Cookies__http(TestCase):                  # Test Routes__Admin__Cookies with HTTP server

    @classmethod
    def setUpClass(cls):                                            # Setup with HTTP server
        cls.test_objs = setup__admin_ui_test_objs(with_parent=True, with_server=True)
        cls.server = cls.test_objs.admin_server

    @classmethod
    def tearDownClass(cls):                                         # Cleanup
        cleanup_admin_ui_test_objs(cls.test_objs)

    def test_01_cookie_persistence(self):                           # Test cookie persistence across requests
        # Set a cookie
        response1 = self.server.requests_post('/admin-cookies/api/cookie-set/persist-test',
                                                data={'value': 'persistent-value', 'expires_in': 0})

        assert response1.status_code == 200
        assert response1.json() == { "success"  : True           ,
                                     "name"     : "persist-test" ,
                                     "value_set": True           }
        # Get cookie in next request
        cookies = response1.cookies
        response2 = self.server.requests_get('/admin-cookies/api/cookie-get/persist-test',cookies=cookies)

        assert response2.status_code == 200
        data = response2.json()
        assert data['value'] == 'persistent-value'
        assert data['exists'] is True

    def test_02_cookie_security_headers(self):                  # Test cookie security headers
        response = self.server.requests_post('/admin-cookies/api/cookie-set/secure-test',
                                            data={'value': 'secure-value', 'expires_in': 0})

        assert response.status_code == 200

        # Check cookie attributes in response headers
        set_cookie_header = response.headers.get('set-cookie', '')

        assert 'HttpOnly'        in set_cookie_header               # Should have security attributes
        assert 'SameSite=strict' in set_cookie_header               # Note: Secure flag depends on HTTPS (so we can't easily test it here)

    def test_03_concurrent_cookie_operations(self):                 # Test concurrent cookie operations
        import concurrent.futures
        import random

        def set_random_cookie():
            cookie_name = f'concurrent-{random.randint(1000, 9999)}'
            cookie_value = f'value-{random_guid()}'

            response = self.server.requests_post(f'/admin-cookies/api/cookie-set/{cookie_name}',
                                                 data={'value': cookie_value, 'expires_in': 0})

            return response.status_code == 200 and response.json()['success']

        # Make concurrent cookie set requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(set_random_cookie) for _ in range(20)]
            results = [f.result() for f in futures]

        # All should succeed
        assert all(results)

    def test_04_cookie_validation_patterns(self):
        """Test various cookie validation patterns"""
        test_cases = [
            ('openai-api-key'   , 'sk-' + 'a' * 48           , True ),
            ('openai-api-key'   , 'sk-short'                 , False),
            ('anthropic-api-key', 'sk-ant-' + 'x' * 95       , True ),
            ('anthropic-api-key', 'wrong-prefix-' + 'x' * 95 , True ),  # we don't have a template for anthropic
            ('groq-api-key'     , 'any-value'                , True ),  # No validator
            ('custom-cookie'    , 'any-value'                , True )   # Unknown cookie
        ]

        for cookie_name, cookie_value, should_succeed in test_cases:
            response = self.server.requests_post(f'/admin-cookies/api/cookie-set/{cookie_name}',
                                                 data={'value': cookie_value, 'expires_in':0})

            assert response.status_code == 200
            data = response.json()

            if should_succeed:
                assert data['success'] is True, f"Failed for {cookie_name} with {cookie_value}"
            else:
                assert data['success'] is False, f"Should have failed for {cookie_name} with {cookie_value}"