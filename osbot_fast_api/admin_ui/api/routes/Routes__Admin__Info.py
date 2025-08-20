from typing                                     import Dict, Any, List
from osbot_utils.utils.Misc                     import timestamp_utc_now
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes
from osbot_fast_api.utils.Fast_API__Server_Info import fast_api__server_info

# todo: refactor any creation logic to Services__Admin_Info since here we should only have the Fast_API__Routes specific logic (for example the type of data to return)

class Routes__Admin__Info(Fast_API__Routes):        # API routes for admin dashboard and server information
    tag        = 'admin-info'
    parent_app = None                               # Will be set by Admin_UI__Fast_API

    def api__server_info(self) -> Dict[str, Any]:           # Get server information # todo: convert this object to Schema__Fast_API__Admin__Server_Info
        return { "server_id"         : fast_api__server_info.server_id   or ''       ,
                 "server_name"       : fast_api__server_info.server_name or "unnamed",
                 "server_instance_id": fast_api__server_info.server_instance_id,
                 "server_boot_time"  : int(fast_api__server_info.server_boot_time),
                 "current_time"      : timestamp_utc_now(),
                 "uptime_ms"         : timestamp_utc_now() - int(fast_api__server_info.server_boot_time)         # double check this calculation
        }

    def api__app_info(self) -> Dict[str, Any]:              # Get FastAPI application information # todo: convert this object to Schema__Fast_API__Admin__App_Info

        return { "name"       : self.parent_app.name              ,
                 "version"    : self.parent_app.version           ,
                 "description": self.parent_app.description       ,
                 "base_path"  : self.parent_app.base_path         ,
                 "docs_offline": self.parent_app.docs_offline     ,
                 "enable_cors": self.parent_app.enable_cors       ,
                 "enable_api_key": self.parent_app.enable_api_key }

    def api__stats(self) -> Dict[str, Any]:                                     # Get application statistics

        routes = self.parent_app.routes(include_default=False, expand_mounts=True)

        # Count routes by method
        method_counts = {}
        for route in routes:
            for method in route.get('http_methods', []):
                method_counts[method] = method_counts.get(method, 0) + 1

        # Count routes by prefix
        prefix_counts = {}
        for route in routes:
            path = route.get('http_path', '')
            prefix = '/' + path.split('/')[1] if '/' in path[1:] else path
            prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1

        return {
            "total_routes"     : len(routes),
            "methods"          : method_counts,
            "prefixes"         : prefix_counts,
            "middlewares_count": len(self.parent_app.user_middlewares()),
            "has_static_files" : self.parent_app.path_static_folder() is not None
        }

    def api__health(self) -> Dict[str, str]:                                                # Health check endpoint
        return { "status": "Ok",
                 "timestamp": str(timestamp_utc_now()) }

    def setup_routes(self):
        self.add_route_get(self.api__server_info)
        self.add_route_get(self.api__app_info   )
        self.add_route_get(self.api__stats      )
        self.add_route_get(self.api__health     )