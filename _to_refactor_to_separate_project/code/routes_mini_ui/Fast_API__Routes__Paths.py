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
                { CSS__FAST_API__Routes__Paths }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{routes_data['title']} API Routes</h1>
                <div class="version">Version: {routes_data['version']}</div>
                
                {self.format_stats_html(routes_data)}
                
                <div class="search-box">
                    <input type="text" class="search-input" id="searchInput" 
                           placeholder="Search routes by path, method, or name...">
                    <button class="search-clear" id="searchClear" onclick="clearSearch()">Clear</button>
                </div>
                
                <h2>Routes</h2>
                <div class="routes-grid" id="routesContainer">
                    {"".join(self.format_route_html(r) for r in routes_data['routes'])}
                </div>
                
                <div id="noResults" class="no-results" style="display: none;">
                    No routes match your search criteria
                </div>
                
                <h2>Mounted Applications</h2>
                <div id="mountsContainer">
                    {"".join(self.format_mount_html(m) for m in routes_data['mounts'])}
                </div>
            </div>
            
            <script>
                // Search functionality
                const searchInput = document.getElementById('searchInput');
                const searchClear = document.getElementById('searchClear');
                const routesContainer = document.getElementById('routesContainer');
                const mountsContainer = document.getElementById('mountsContainer');
                const noResults = document.getElementById('noResults');
                
                searchInput.addEventListener('input', function() {{
                    const searchTerm = this.value.toLowerCase();
                    const routes = routesContainer.querySelectorAll('.route');
                    const mounts = mountsContainer.querySelectorAll('.mount');
                    let hasVisibleRoutes = false;
                    
                    searchClear.style.display = searchTerm ? 'block' : 'none';
                    
                    routes.forEach(route => {{
                        const text = route.textContent.toLowerCase();
                        const isVisible = text.includes(searchTerm);
                        route.style.display = isVisible ? 'flex' : 'none';
                        if (isVisible) hasVisibleRoutes = true;
                    }});
                    
                    mounts.forEach(mount => {{
                        const text = mount.textContent.toLowerCase();
                        mount.style.display = text.includes(searchTerm) ? 'flex' : 'none';
                    }});
                    
                    noResults.style.display = hasVisibleRoutes ? 'none' : 'block';
                }});
                
                function clearSearch() {{
                    searchInput.value = '';
                    searchInput.dispatchEvent(new Event('input'));
                }}
                
                // Copy path functionality
                function copyPath(path, button) {{
                    const fullUrl = window.location.origin + path;
                    navigator.clipboard.writeText(fullUrl).then(() => {{
                        const originalText = button.textContent;
                        button.textContent = 'Copied!';
                        button.classList.add('copied');
                        setTimeout(() => {{
                            button.textContent = originalText;
                            button.classList.remove('copied');
                        }}, 2000);
                    }});
                }}
                
                // Make GET routes clickable
                document.querySelectorAll('.path-link').forEach(link => {{
                    link.addEventListener('click', function(e) {{
                        if (e.ctrlKey || e.metaKey) {{
                            // Allow normal link behavior for ctrl/cmd+click
                            return;
                        }}
                        e.preventDefault();
                        window.open(this.href, '_blank');
                    }});
                }});
            </script>
        </body>
        </html>
        """
        return html_content

    def format_route_html(self, route):
        methods_html = "".join(f'<span class="method {m}">{m}</span>' for m in route['methods'])

        # Make GET requests clickable (and HEAD since they're safe methods)
        path_html = route['path']
        if 'GET' in route['methods'] or 'HEAD' in route['methods']:
            path_html = f'<a href="{route["path"]}" class="path-link" target="_blank">{route["path"]}</a>'

        # Add copy button for easy path copying
        copy_btn = f'<button class="copy-btn" onclick="copyPath(\'{route["path"]}\', this)">Copy</button>'

        # Add route name if different from path
        name_html = ""
        if route['name'] and route['name'] != route['path']:
            name_html = f'<span class="route-name">{route["name"]}</span>'

        return f'<div class="route">{methods_html}<span class="path">{path_html}</span>{copy_btn}{name_html}</div>'

    def format_mount_html(self, mount):
        mount_type = f'<span class="mount-type">{mount["type"]}</span>'
        return f'<div class="mount"><strong>{mount["path"]}</strong>{mount_type}</div>'

    def format_stats_html(self, routes_data):
        """Generate statistics section"""
        total_routes = len(routes_data['routes'])
        total_mounts = len(routes_data['mounts'])

        # Count methods
        method_counts = {}
        for route in routes_data['routes']:
            for method in route['methods']:
                method_counts[method] = method_counts.get(method, 0) + 1

        get_count = method_counts.get('GET', 0)
        post_count = method_counts.get('POST', 0)

        return f"""
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">{total_routes}</div>
                <div class="stat-label">Total Routes</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{get_count}</div>
                <div class="stat-label">GET Endpoints</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{post_count}</div>
                <div class="stat-label">POST Endpoints</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{total_mounts}</div>
                <div class="stat-label">Mounted Apps</div>
            </div>
        </div>
        """


CSS__FAST_API__Routes__Paths = """\
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 30px;
            }
            h1 {
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 2em;
            }
            .version {
                color: #7f8c8d;
                font-size: 0.9em;
                margin-bottom: 30px;
            }
            h2 {
                color: #34495e;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 10px;
                margin-top: 30px;
            }
            .routes-grid {
                display: grid;
                gap: 12px;
                margin-top: 20px;
            }
            .route {
                display: flex;
                align-items: center;
                padding: 12px 15px;
                border-left: 3px solid #4CAF50;
                background: #fafafa;
                border-radius: 4px;
                transition: all 0.2s ease;
            }
            .route:hover {
                background: #f0f0f0;
                transform: translateX(5px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .mount {
                display: flex;
                align-items: center;
                padding: 15px;
                border-left: 3px solid #2196F3;
                background: #f8f9fa;
                border-radius: 4px;
                margin-bottom: 10px;
            }
            .method {
                display: inline-block;
                padding: 4px 10px;
                margin-right: 10px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                min-width: 60px;
                text-align: center;
            }
            .GET { background: #61affe; color: white; }
            .POST { background: #49cc90; color: white; }
            .PUT { background: #fca130; color: white; }
            .DELETE { background: #f93e3e; color: white; }
            .HEAD { background: #9012fe; color: white; }
            .OPTIONS { background: #0d5aa7; color: white; }
            .PATCH { background: #50e3c2; color: white; }

            .path {
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 14px;
                color: #2c3e50;
                flex-grow: 1;
            }
            .path-link {
                color: #3498db;
                text-decoration: none;
                transition: color 0.2s ease;
            }
            .path-link:hover {
                color: #2980b9;
                text-decoration: underline;
            }
            .route-name {
                color: #7f8c8d;
                font-size: 12px;
                margin-left: auto;
                padding-left: 20px;
                font-style: italic;
            }
            .mount-type {
                background: #e3f2fd;
                color: #1976d2;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                margin-left: 10px;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin: 20px 0;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
            }
            .stat-item {
                text-align: center;
            }
            .stat-value {
                font-size: 2em;
                font-weight: bold;
                color: #3498db;
            }
            .stat-label {
                font-size: 0.9em;
                color: #7f8c8d;
                margin-top: 5px;
            }
            .search-box {
                margin: 20px 0;
                position: relative;
            }
            .search-input {
                width: 100%;
                padding: 12px 40px 12px 15px;
                border: 2px solid #ecf0f1;
                border-radius: 6px;
                font-size: 14px;
                transition: border-color 0.3s ease;
            }
            .search-input:focus {
                outline: none;
                border-color: #3498db;
            }
            .search-clear {
                position: absolute;
                right: 10px;
                top: 50%;
                transform: translateY(-50%);
                background: #e74c3c;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                display: none;
            }
            .no-results {
                text-align: center;
                padding: 40px;
                color: #7f8c8d;
                font-style: italic;
            }
            .copy-btn {
                background: #95a5a6;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 11px;
                margin-left: 10px;
                transition: background 0.2s ease;
            }
            .copy-btn:hover {
                background: #7f8c8d;
            }
            .copy-btn.copied {
                background: #27ae60;
            }
"""