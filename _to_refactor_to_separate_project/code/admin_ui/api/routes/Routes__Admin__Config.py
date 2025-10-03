from typing                                     import Dict, Any, List
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes


class Routes__Admin__Config(Fast_API__Routes):                      # API routes for configuration and route management
    tag        = 'admin-config'
    parent_app = None                                               # Will be set by Admin_UI__Fast_API

    def api__routes(self) -> List[Dict[str, Any]]:                  # Get all application routes
        if not self.parent_app:
            return []

        routes = self.parent_app.routes(include_default=False, expand_mounts=True)

        # Enhance route information
        enhanced_routes = []
        for route in routes:
            enhanced = { "path"     : route.get('http_path'       ),
                         "methods"  : route.get('http_methods', []),
                         "name"     : route.get('method_name'    ),
                         "tag"      : self._extract_tag_from_path(route.get('http_path', '')),
                         "is_get"   : 'GET'     in route.get('http_methods', []),
                         "is_post"  : 'POST'    in route.get('http_methods', []),
                         "is_put"   : 'PUT'     in route.get('http_methods', []),
                         "is_delete": 'DELETE'  in route.get('http_methods', [])}
            enhanced_routes.append(enhanced)

        return enhanced_routes

    def api__routes_grouped(self) -> Dict[str, List[Dict[str, Any]]]:               # Get routes grouped by prefix/tag
        routes = self.api__routes()

        grouped = {}
        for route in routes:
            tag = route['tag']
            if tag not in grouped:
                grouped[tag] = []
            grouped[tag].append(route)

        return grouped

    def api__middlewares(self) -> List[Dict[str, Any]]:                             # Get middleware information
        if not self.parent_app:
            return []
        return self.parent_app.user_middlewares(include_params=False)

    def api__openapi_spec(self) -> Dict[str, Any]:                                  # Get OpenAPI specification
        if not self.parent_app:
            return {}

        return self.parent_app.open_api_json()

    def _extract_tag_from_path(self, path: str) -> str:                             # Extract a tag/category from the route path
        if not path or path == '/':
            return 'root'

        parts = path.strip('/').split('/')
        if parts:
            return parts[0]
        return 'other'

    def setup_routes(self):
        self.add_route_get(self.api__routes         )
        self.add_route_get(self.api__routes_grouped )
        self.add_route_get(self.api__middlewares    )
        self.add_route_get(self.api__openapi_spec   )