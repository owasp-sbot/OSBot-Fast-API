import osbot_fast_api
from osbot_utils.type_safe.primitives.safe_str.text.Safe_Str__Text  import Safe_Str__Text
from osbot_utils.utils.Files                                        import path_combine
from osbot_fast_api.admin_ui.api.Admin_UI__Config                   import Admin_UI__Config
from osbot_fast_api.admin_ui.api.routes.Routes__Admin__Config       import Routes__Admin__Config
from osbot_fast_api.admin_ui.api.routes.Routes__Admin__Cookies      import Routes__Admin__Cookies
from osbot_fast_api.admin_ui.api.routes.Routes__Admin__Docs         import Routes__Admin__Docs
from osbot_fast_api.admin_ui.api.routes.Routes__Admin__Info         import Routes__Admin__Info
from osbot_fast_api.admin_ui.api.routes.Routes__Admin__Static       import Routes__Admin__Static
from osbot_fast_api.api.Fast_API                                    import Fast_API
from osbot_fast_api.schemas.Safe_Str__Fast_API__Name                import Safe_Str__Fast_API__Name
from osbot_fast_api.schemas.Safe_Str__Fast_API__Route__Prefix       import Safe_Str__Fast_API__Route__Prefix


class Admin_UI__Fast_API(Fast_API):                                 # Admin UI for FastAPI applications.
    add_admin_ui  : bool                              = False       # in the admin ui we can't add an admin ui :)
    admin_config  : Admin_UI__Config
    base_path     : Safe_Str__Fast_API__Route__Prefix = '/admin'
    description   : Safe_Str__Text                    = 'Administration interface for FastAPI applications'
    docs_offline  : bool                              = True
    default_routes: bool                              = False
    name          : Safe_Str__Fast_API__Name          = 'FastAPI Admin UI'
    parent_app    : Fast_API

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.admin_config.base_path:                             # todo we should move this into a method that applies all changes we might have in admin_config
            self.base_path = self.admin_config.base_path

    def path_static_folder(self):                           # Override to serve admin UI static files
        return path_combine(osbot_fast_api.path, 'admin_ui/static')     # todo move string to consts__Fast_API__Admin_UI

    def setup_routes(self):             # Set up all admin UI routes"""
        Routes__Admin__Info    .parent_app = self.parent_app                        # Pass parent_app reference to routes that need it
        Routes__Admin__Config  .parent_app = self.parent_app                        # todo: see if there is a better way to do this, since these routes (like Routes__Admin__Info) have access to the .app() object
        Routes__Admin__Cookies .parent_app = self.parent_app
        Routes__Admin__Docs    .parent_app = self.parent_app

        if self.admin_config.show_dashboard:  self.add_routes(Routes__Admin__Info   )      # Add API routes (depending on config)
        if self.admin_config.show_routes:     self.add_routes(Routes__Admin__Config )
        if self.admin_config.show_cookies:    self.add_routes(Routes__Admin__Cookies)
        if self.admin_config.show_docs:       self.add_routes(Routes__Admin__Docs   )

        self.add_routes(Routes__Admin__Static)                                          # Add static file serving for the UI
        return self