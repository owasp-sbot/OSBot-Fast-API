from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Prefix      import Safe_Str__Fast_API__Route__Prefix
from osbot_fast_api.utils.Version                                               import version__osbot_fast_api
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text    import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Version import Safe_Str__Version
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Name               import Safe_Str__Fast_API__Name
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe


class Schema__Fast_API__Config(Type_Safe):
    base_path      : Safe_Str__Fast_API__Route__Prefix = '/'
    add_admin_ui   : bool                              = False
    docs_offline   : bool                              = True
    enable_cors    : bool                              = False
    enable_api_key : bool                              = False
    default_routes : bool                              = True
    name           : Safe_Str__Fast_API__Name          = None
    version        : Safe_Str__Version                 = version__osbot_fast_api
    description    : Safe_Str__Text                    = None
