from osbot_utils.type_safe.Type_Safe                import Type_Safe
from osbot_fast_api.admin_ui.api.Admin_UI__Config   import Admin_UI__Config
from osbot_fast_api.api.Fast_API                    import Fast_API
from osbot_fast_api.admin_ui.api.Admin_UI__Fast_API import Admin_UI__Fast_API
from osbot_fast_api.utils.Fast_API_Server           import Fast_API_Server
from starlette.testclient                           import TestClient
from osbot_utils.utils.Misc                         import random_port, random_guid
import os


# Test constants
TEST_ADMIN_API_KEY__NAME    = 'X-Admin-Test-Key'
TEST_ADMIN_API_KEY__VALUE   = 'test-admin-key-123456'
TEST_PARENT_API_KEY__NAME   = 'X-Parent-Test-Key'
TEST_PARENT_API_KEY__VALUE  = 'test-parent-key-789012'


class Admin_UI__Test_Objs(Type_Safe):
    """Container for Admin UI test objects"""
    parent_fast_api     : Fast_API
    admin_ui            : Admin_UI__Fast_API
    admin_config        : Admin_UI__Config
    parent_client       : TestClient
    admin_client        : TestClient
    parent_server       : Fast_API_Server = None
    admin_server        : Fast_API_Server = None
    test_cookies        : dict
    test_routes_added   : list
    cleanup_functions   : list


def setup__admin_ui_test_objs(with_parent=True, with_server=False):
    """
    Initialize Admin UI test dependencies

    Args:
        with_parent: Include parent FastAPI instance
        with_server: Start actual HTTP servers (for integration tests)

    Returns:
        Admin_UI__Test_Objs with initialized components
    """
    test_objs = Admin_UI__Test_Objs()
    test_objs.test_cookies = {}
    test_objs.test_routes_added = []
    test_objs.cleanup_functions = []

    # Create admin config
    test_objs.admin_config = Admin_UI__Config(
        enabled=True,
        base_path='/admin',
        require_auth=False,  # Disable for most tests
        show_dashboard=True,
        show_cookies=True,
        show_routes=True,
        show_docs=True,
        allow_api_testing=True
    )

    if with_parent:
        # Create parent FastAPI instance
        test_objs.parent_fast_api = Fast_API(name           = 'Test Parent API'                , # todo: move these static string values to a consts* files
                                             version        = 'v1.0.99'                    ,
                                             description    = 'Parent API for Admin UI testing',
                                             enable_api_key = False                            ,  # Disable for tests
                                             enable_cors    = True                             ,
                                             add_admin_ui   = True                             )
        test_objs.parent_fast_api.setup()

        # Add some test routes to parent
        add_test_routes_to_parent(test_objs.parent_fast_api)
        test_objs.test_routes_added.extend(['test-hello', 'test-echo', 'test-items'])

    # Create Admin UI instance
    test_objs.admin_ui = Admin_UI__Fast_API(admin_config = test_objs.admin_config,
                                            name         = 'Test Admin UI'       ,      # refactor static strings
                                            version      = 'v1.0.99'          )

    if with_parent:
        test_objs.admin_ui.parent_app = test_objs.parent_fast_api                   # todo: review this use of parent_app

    test_objs.admin_ui.setup()

    # Create test clients
    if with_parent:
        test_objs.parent_client = TestClient(test_objs.parent_fast_api.app())
    test_objs.admin_client = TestClient(test_objs.admin_ui.app())

    # Start servers if requested
    if with_server:
        if with_parent:
            test_objs.parent_server = Fast_API_Server(
                app=test_objs.parent_fast_api.app(),
                port=random_port()
            )
            test_objs.parent_server.start()
            test_objs.cleanup_functions.append(test_objs.parent_server.stop)

        test_objs.admin_server = Fast_API_Server(
            app=test_objs.admin_ui.app(),
            port=random_port()
        )
        test_objs.admin_server.start()
        test_objs.cleanup_functions.append(test_objs.admin_server.stop)

    # Add test cookies
    setup_test_cookies(test_objs)

    return test_objs


def add_test_routes_to_parent(fast_api: Fast_API):          # Add test routes to parent FastAPI for testing"""

    @fast_api.app().get("/test/hello")
    def test_hello():
        return {"message": "Hello from test route"}

    @fast_api.app().get("/test/echo")
    def test_echo(message: str = "default"):
        return {"echo": message}

    @fast_api.app().post("/test/items")
    def test_create_item(name: str, price: float):
        return {"created": True, "item": {"name": name, "price": price}}

    @fast_api.app().get("/test/protected")
    def test_protected():
        return {"message": "This is protected"}

    # Add routes with different methods
    @fast_api.app().put("/test/update/{item_id}")
    def test_update(item_id: int, data: dict):
        return {"updated": True, "id": item_id, "data": data}

    @fast_api.app().delete("/test/delete/{item_id}")
    def test_delete(item_id: int):
        return {"deleted": True, "id": item_id}


def setup_test_cookies(test_objs: Admin_UI__Test_Objs):
    """Setup test cookies in the test objects"""
    test_objs.test_cookies = {
        'test-cookie-1': 'test-value-1',
        'test-cookie-2': 'test-value-2',
        'openai-api-key': 'sk-test' + 'x' * 44,  # Mock OpenAI key format
        'anthropic-api-key': 'sk-ant-test' + 'x' * 87,  # Mock Anthropic key format
        'auth-token': random_guid()
    }


# todo: review the use of a static method here, since this could had side effects
#       if we really want to do the full clean up (in some cases that is not needed),
# .     we should have a copy of the Admin_UI__Config object
def cleanup_admin_ui_test_objs(test_objs: Admin_UI__Test_Objs): # Clean up test objects and resources
    # Run cleanup functions
    for cleanup_func in test_objs.cleanup_functions:
        try:
            cleanup_func()
        except:
            pass

    # Stop servers if running
    if test_objs.parent_server and test_objs.parent_server.running:
        test_objs.parent_server.stop()

    # todo: see if need this since stopping the parent should be enough
    if test_objs.admin_server and test_objs.admin_server.running:
        test_objs.admin_server.stop()