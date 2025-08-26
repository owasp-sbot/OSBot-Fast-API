import time
import concurrent.futures
from unittest                                                   import TestCase
from osbot_utils.utils.Env                                      import in_github_action
from osbot_utils.utils.Misc                                     import list_set
from starlette.testclient                                       import TestClient
from osbot_fast_api.admin_ui.api.Admin_UI__Config               import Admin_UI__Config
from osbot_fast_api.admin_ui.api.Admin_UI__Fast_API             import Admin_UI__Fast_API
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Context import Admin_UI__Test_Context
from osbot_fast_api.api.Fast_API                                import Fast_API
from osbot_fast_api.utils.Fast_API_Server                       import Fast_API_Server
from osbot_fast_api.utils.Version                               import version__osbot_fast_api


class test_Admin_UI__Fast_API__multiple_workflows(TestCase):         # Full integration tests for Admin UI

    def test_01_complete_workflow(self):
        """Test complete Admin UI workflow"""
        with Admin_UI__Test_Context(with_parent=True, with_server=True) as test_objs:
            server = test_objs.admin_server

            # 1. Get index page
            response = server.requests_get('/admin-static/index')
            assert response.status_code == 200
            assert 'text/html' in response.headers['content-type']

            # 2. Get server info
            response = server.requests_get('/admin-info/api/server-info')
            assert response.status_code == 200
            server_info = response.json()
            assert 'server_id' in server_info

            # 3. Get routes
            response = server.requests_get('/admin-config/api/routes')
            assert response.status_code == 200
            routes = response.json()
            assert len(routes) > 0

            # 4. Set a cookie
            response = server.requests_post('/admin-cookies/api/cookie-set/test-workflow',
                                             data={'value': 'workflow-test-value', 'expires_in': 0})
            assert response.status_code == 200
            assert response.json()['success'] is True

            # 5. Verify cookie was set
            cookies = response.cookies
            response = server.requests_get('/admin-cookies/api/cookie-get/test-workflow', cookies=cookies )
            assert response.status_code == 200
            assert response.json()['value'] == 'workflow-test-value'

            # 6. Get documentation endpoints
            response = server.requests_get('/admin-docs/api/docs-endpoints')
            assert response.status_code == 200
            docs = response.json()
            assert len(docs) == 6

            # 7. Get stats
            response = server.requests_get('/admin-info/api/stats')
            assert response.status_code == 200
            stats = response.json()
            assert stats['total_routes'] > 0

    def test_02_parent_child_interaction(self):                         # Test interaction between parent app and admin UI
        parent = Fast_API(name         = 'Integration Test Parent')     # Create parent with some routes

        with parent as _:
            assert _.name         == 'Integration Test Parent'
            assert _.add_admin_ui is False

        @parent.app().get("/parent/test")
        def parent_test():
            return {"source": "parent"}

        @parent.app().post("/parent/echo")
        def parent_echo(message: str):
            return {"echo": message}

        parent.setup()


        # Create and mount admin UI (this is doing manually what the Fast_API.setup_admin_ui() does)
        admin_config = Admin_UI__Config( enabled      = True                    ,
                                         base_path    = '/admin'                )
        # admin = Admin_UI__Fast_API     ( admin_config = admin_config            ,
        #                                  name         = 'Integration Test Admin',
        #                                                    )

        # Mount admin to parent
        kwargs = dict(admin_config=admin_config, parent_app=parent)
        parent.mount_fast_api(Admin_UI__Fast_API, **kwargs)

        with Fast_API_Server(app=parent.app()) as server:                       # Start server with combined app
            response = server.requests_get('/parent/test')                      # Test parent routes work
            assert response.status_code == 200
            assert response.json()['source'] == 'parent'

            response = server.requests_get('/admin/admin-info/api/health')      # Test admin routes work
            assert response.status_code == 200
            assert response.json()['status'] == 'Ok'

            # # Test admin can see parent routes
            response = server.requests_get('/admin/admin-config/api/routes')
            assert response.status_code == 200
            routes = response.json()

            # Should include parent routes
            paths = [r['path'] for r in routes]

            assert '/parent/test'                           in paths
            assert '/parent/echo'                           in paths
            assert '/admin/admin-info/api/server-info'      in paths
            assert '/admin/admin-info/api/health'           in paths
            assert '/admin/admin-docs/api/content/{doc_id}' in paths

            # Test admin can get parent app info
            response = server.requests_get('/admin/admin-info/api/app-info')
            assert response.status_code == 200
            info = response.json()
            assert info['name'] == 'Integration Test Parent'

    def test_03_cookie_management_workflow(self):   # Test complete cookie management workflow
        with Admin_UI__Test_Context(with_server=True) as test_objs:
            server = test_objs.admin_server

            # 1. Get cookie templates
            response = server.requests_get('/admin-cookies/api/cookies-templates')
            assert response.status_code == 200
            templates = response.json()
            assert len(templates) > 0

            # 2. Generate an API key
            response = server.requests_get('/admin-cookies/api/generate-value/api_key')
            assert response.status_code == 200
            generated = response.json()
            api_key = generated['value']
            assert api_key.startswith('sk-')

            # 3. Set OpenAI API key
            open_ai_key__value = 'sk-' + 'a' * 48
            response = server.requests_post('/admin-cookies/api/cookie-set/openai-api-key',
                                             data={'value': open_ai_key__value, 'expires_in': 0})
            cookies_1 = response.cookies
            assert response.json()['success'] is True
            assert dict(cookies_1) == { 'openai-api-key': open_ai_key__value }
            # 4. Set multiple cookies at once
            bulk_cookies = {'cookies':[{'name': 'groq-api-key', 'value': 'groq-test-key'   , 'expires_in':0 },
                                       {'name': 'auth-token'  , 'value': generated['value'], 'expires_in':0 }]}
            response = server.requests_post('/admin-cookies/api/cookies-bulk-set',
                                             json=bulk_cookies ,
                                             cookies=cookies_1   )
            assert response.status_code == 200
            assert response.json() == { 'results': [ {'name': 'groq-api-key', 'success': True, 'value_set': True},
                                                     {'name': 'auth-token', 'success': True, 'value_set': True}],
                                        'success': True}
            cookies_2 = response.cookies
            assert dict(cookies_2) == { 'auth-token': generated['value'],
                                        'groq-api-key': 'groq-test-key' }


            # 5. List all cookies
            cookies_3 = dict(cookies_1) | dict(cookies_2)           # question how to do this
            assert list_set(cookies_3) == ['auth-token', 'groq-api-key', 'openai-api-key']

            response = server.requests_get('/admin-cookies/api/cookies-list', cookies=cookies_3)
            cookie_list = response.json()
            assert cookie_list == [{  'category'    : 'llm'             ,
                                      'description' : 'OpenAI API Key'  ,
                                      'has_value'   : True              ,
                                      'is_valid'    : True              ,
                                      'name'        : 'openai-api-key'  ,
                                      'required'    : True              ,
                                      'value_length': 51                }]
            # Verify cookies are set
            openai = next((c for c in cookie_list if c['name'] == 'openai-api-key'), None)
            assert openai is not None
            assert openai['has_value'] is True
            assert openai['is_valid'] is True

            # 6. Delete a cookie
            response = server.requests_delete('/admin-cookies/api/cookie-delete/groq-api-key', cookies=cookies_3)
            assert response.json()['deleted'] is True

    def test_04_performance_under_load(self):
        """Test Admin UI performance under concurrent load"""
        with Admin_UI__Test_Context(with_server=True) as test_objs:
            server = test_objs.admin_server

            # Define different request types
            def get_health():
                return server.requests_get('/admin-info/api/health')

            def get_stats():
                return server.requests_get('/admin-info/api/stats')

            def get_routes():
                return server.requests_get('/admin-config/api/routes')

            def set_cookie(name):
                return server.requests_post( f'/admin-cookies/api/cookie-set/{name}',
                                             data={'value': f'value-{name}', 'expires_in': 0})

            # Warm up and that all are working
            assert get_health(   ).status_code == 200
            assert get_stats (   ).status_code == 200
            assert get_routes(   ).status_code == 200
            assert set_cookie('a').status_code == 200

            # Measure performance
            start_time = time.time()

            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                futures = []

                # Mix of different operations
                for i in range(100):
                    if i % 4 == 0:
                        futures.append(executor.submit(get_health))
                    elif i % 4 == 1:
                        futures.append(executor.submit(get_stats))
                    elif i % 4 == 2:
                        futures.append(executor.submit(get_routes))
                    else:
                        futures.append(executor.submit(set_cookie, f'perf-{i}'))

                # Wait for all to complete
                results = [f.result() for f in futures]

            duration = time.time() - start_time

            # All requests should succeed
            assert all(r.status_code == 200 for r in results)

            # Should complete in reasonable time
            throughput = len(results) / duration                    # Calculate throughput
            if in_github_action():
                assert duration   < 3    # 100 requests in under 3 seconds
                assert throughput > 100  # At least 100 req/s
            else:
                assert duration   < 0.3  # 100 requests in under 0.3 seconds (locally)
                assert throughput > 400  # At least 500 req/s                (locally)

    def test_05_error_handling(self):
        """Test error handling in Admin UI"""
        with Admin_UI__Test_Context() as test_objs:
            client = test_objs.admin_client

            # 1. Invalid cookie validation
            response = client.post('/admin-cookies/api/cookie-set/openai-api-key',
                                    json={'value': 'invalid-key', 'expires_in': 0})
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is False
            assert 'does not match required pattern' in data['error']

            # 2. Non-existent route
            response = client.get('/admin-info/api/non-existent')
            assert response.status_code == 404

            # 3. Missing parent app
            admin = Admin_UI__Fast_API()
            admin.setup()
            test_client = TestClient(admin.app())

            response = test_client.get('/admin-info/api/app-info')
            assert response.status_code == 200
            assert response.json() == {  'base_path'    : '/',          # default Fast_API data , since parent_app was not defined
                                         'description'  : None,
                                         'docs_offline' : True,
                                         'enable_api_key': False,
                                         'enable_cors'  : False,
                                         'name'         : 'Fast_API',
                                         'version'      : version__osbot_fast_api }

            # 4. Invalid request data
            response = client.post('/admin-cookies/api/cookie-set/test', json={})
            # Should handle gracefully
            assert response.status_code  == 400
            assert response.json()       == {'detail': [{'input': {},
                                                         'loc': ['body', 'expires_in'],
                                                         'msg': 'Field required',
                                                         'type': 'missing'}]}

    def test_06_static_file_serving(self):
        """Test static file serving for UI assets"""
        with Admin_UI__Test_Context() as test_objs:
            client = test_objs.admin_client

            # Test CSS files
            css_files = ['base.css', 'layout.css', 'components.css']
            for css_file in css_files:
                response = client.get(f'/admin-static/serve-css/{css_file}')
                assert response.status_code == 200
                assert 'text/css' in response.headers['content-type']

            # Test JS files
            js_files = ['admin_ui.js']
            for js_file in js_files:
                response = client.get(f'/admin-static/serve-js/{js_file}')
                assert response.status_code == 200
                assert 'application/javascript' in response.headers['content-type']

            # Test non-existent files
            response = client.get('/admin-static/serve-css/non-existent.css')
            assert response.status_code == 200  # Returns empty content
            assert response.text == ""

    def test_07_openapi_integration(self):
        """Test OpenAPI spec includes admin routes"""
        with Admin_UI__Test_Context() as test_objs:
            # Get OpenAPI spec from admin
            response = test_objs.admin_client.get('/admin-config/api/openapi-spec')
            spec = response.json()

            # Should have parent API info
            assert spec['info']['title'] == 'Test Parent API'

            # Should include parent paths
            assert len(spec['paths']) > 0

            # Check for test routes
            test_paths = [p for p in spec['paths'] if '/test' in p]
            assert len(test_paths) > 0

            # Verify path operations
            if '/test/hello' in spec['paths']:
                hello_spec = spec['paths']['/test/hello']
                assert 'get' in hello_spec
                assert '200' in hello_spec['get']['responses']