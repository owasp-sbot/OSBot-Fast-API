from unittest                                                   import TestCase
from starlette.testclient                                       import TestClient
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Context import Admin_UI__Test_Context


class test_Admin_UI__Fast_API__with_auth(TestCase):         # Test Admin UI with authentication enabled

    def test_01_bug__auth_required__fix_text(self):                         # Test that auth is enforced when enabled
        with Admin_UI__Test_Context(with_auth=True) as test_objs:           # BUG: Request without auth should fail
            client_no_auth = test_objs.admin_ui.client()
            response = client_no_auth.get('/admin-info/api/health')
            assert response.status_code == 200                              # BUG: this should be 401

            response = client_no_auth.get('/AAAA')
            assert response.status_code == 404

            # Should still work - health check might be excluded
            # But other endpoints should require auth

            # Test authenticated request
            # response = test_objs.admin_client.get('/api/server-info')
            # assert response.status_code == 200