from osbot_utils.type_safe.Type_Safe                          import Type_Safe
from osbot_fast_api.schemas.Safe_Str__Fast_API__Route__Prefix import Safe_Str__Fast_API__Route__Prefix

class Admin_UI__Config(Type_Safe):                                   # Configuration for Admin UI
    enabled          : bool = True
    base_path        : Safe_Str__Fast_API__Route__Prefix = '/admin'
    require_auth     : bool = True
    show_dashboard   : bool = True
    show_cookies     : bool = True
    show_routes      : bool = True
    show_docs        : bool = True
    allow_api_testing: bool = True