import os

from osbot_utils.utils.Env                                    import get_env, set_env
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Objs  import TEST_ADMIN_API_KEY__NAME, TEST_ADMIN_API_KEY__VALUE, setup__admin_ui_test_objs, TEST_PARENT_API_KEY__NAME, TEST_PARENT_API_KEY__VALUE, cleanup_admin_ui_test_objs


class Admin_UI__Test_Context:                                 # Context manager for Admin UI testing

    def __init__(self, with_parent=True, with_server=False, with_auth=False):
        self.with_parent    = with_parent
        self.with_server    = with_server
        self.with_auth      = with_auth
        self.test_objs      = None
        self.original_env   = {}

    def __enter__(self):                                                                # Store original environment
        if self.with_auth:
            # todo: refactor this to use OSBot_Utils Temp_Env_Vars class (which already does has the logic to restore the env vars changed)
            self.original_env = { 'FAST_API__AUTH__API_KEY__NAME' : get_env('FAST_API__AUTH__API_KEY__NAME'),
                                  'FAST_API__AUTH__API_KEY__VALUE': get_env('FAST_API__AUTH__API_KEY__VALUE')}
            set_env('FAST_API__AUTH__API_KEY__NAME'     , TEST_ADMIN_API_KEY__NAME)     # Set test auth
            set_env('FAST_API__AUTH__API_KEY__VALUE'    , TEST_ADMIN_API_KEY__VALUE)    # todo move these values to a consts_* file

        self.test_objs = setup__admin_ui_test_objs(with_parent=self.with_parent,       # Setup test objects
                                                   with_server=self.with_server)

        if self.with_auth:
            self.test_objs.admin_config.require_auth = True
            self.test_objs.admin_client.headers[TEST_ADMIN_API_KEY__NAME] = TEST_ADMIN_API_KEY__VALUE                   # Add auth headers to clients
            if self.test_objs.parent_client:
                self.test_objs.parent_client.headers[TEST_PARENT_API_KEY__NAME] = TEST_PARENT_API_KEY__VALUE

        return self.test_objs

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup
        if self.test_objs:
            cleanup_admin_ui_test_objs(self.test_objs)

        # Restore environment
        if self.with_auth:
            for key, value in self.original_env.items():                            # todo: refactor to use OSBot_Utils Temp_Env_Vars
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value