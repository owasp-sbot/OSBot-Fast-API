from typing                          import Dict, Any, List
from fastapi                         import FastAPI
from osbot_utils.type_safe.Type_Safe import Type_Safe


class Fast_API__Routes__Paths(Type_Safe):
    app: FastAPI

    def routes_tree(self) -> Dict[str, Any]:                                    # Returns a hierarchical view of all routes and mounts
        routes_data = { 'title'      : self.app.title       ,
                        'version'    : self.app.version     ,
                        'description': self.app.description ,
                        'routes'     : []                   ,
                        'mounts'     : []                   }

        for route in self.app.routes:                                           # Process regular routes
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                route_info = {
                    'path': route.path,
                    'methods': list(route.methods) if route.methods else [],
                    'name': route.name,
                    #'tags': getattr(route, 'tags', [])
                }
                routes_data['routes'].append(route_info)


            elif hasattr(route, 'path') and hasattr(route, 'app'):              # Handle mounts
                mount_info = {
                    'path': route.path,
                    'type': type(route.app).__name__,
                    'routes': self.get_mount_routes(route.app)
                }
                routes_data['mounts'].append(mount_info)

        return routes_data

    def get_mount_routes(self, mounted_app) -> List[Dict]:                      # Extract routes from a mounted application
        routes = []
        if hasattr(mounted_app, 'routes'):
            for route in mounted_app.routes:
                if hasattr(route, 'path'):
                    routes.append({
                        'path': route.path,
                        'methods': list(getattr(route, 'methods', []))
                    })
        return routes

    def routes_html(self) -> str:                                               # Returns an HTML page with all routes
        routes_data = self.routes_tree()

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{routes_data['title']} - Routes Overview</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .route {{ margin: 10px 0; padding: 10px; border-left: 3px solid #4CAF50; }}
                .mount {{ margin: 10px 0; padding: 10px; border-left: 3px solid #2196F3; }}
                .method {{ 
                    display: inline-block; 
                    padding: 2px 8px; 
                    margin-right: 5px;
                    border-radius: 3px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .GET {{ background: #61affe; color: white; }}
                .POST {{ background: #49cc90; color: white; }}
                .PUT {{ background: #fca130; color: white; }}
                .DELETE {{ background: #f93e3e; color: white; }}
                .path {{ font-family: monospace; }}
            </style>
        </head>
        <body>
            <h1>{routes_data['title']} API Routes</h1>
            <p>Version: {routes_data['version']}</p>
            
            <h2>Routes</h2>
            {"".join(self.format_route_html(r) for r in routes_data['routes'])}
            
            <h2>Mounted Applications</h2>
            {"".join(self.format_mount_html(m) for m in routes_data['mounts'])}
        </body>
        </html>
        """
        return html_content

    def format_route_html(self, route):
        methods_html = "".join(f'<span class="method {m}">{m}</span>' for m in route['methods'])
        return f'<div class="route">{methods_html} <span class="path">{route["path"]}</span></div>'

    def format_mount_html(self, mount):
        return f'<div class="mount"><strong>{mount["path"]}</strong> ({mount["type"]})</div>'

