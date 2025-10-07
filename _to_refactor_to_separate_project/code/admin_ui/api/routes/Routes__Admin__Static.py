import osbot_fast_api
from fastapi                                    import Response
from fastapi.responses                          import FileResponse, HTMLResponse
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes
from osbot_utils.utils.Files                    import file_exists, path_combine_safe


class Routes__Admin__Static(Fast_API__Routes):              # Routes for serving admin UI static files
    tag = 'admin-static'

    def get_static_path(self, filename: str = "") -> str:   # Get full path to static file
        return path_combine_safe(osbot_fast_api.path, 'admin_ui/static/' +  filename)       # todo: refactor this into two separate methods: one with the 'admin_ui/static/' path and one with the full path to the filename

    def index(self) -> HTMLResponse:                                                        # Serve the main admin UI HTML page
        html_path = self.get_static_path('html/index.html')                                 # todo: move this logic of getting the file to a Service_*

        if file_exists(html_path):
            with open(html_path, 'r') as f:
                content = f.read()
            return HTMLResponse(content=content)                                            # this is a good example of what we should be doing in these routes (in this case the return of the HTMLResponse)

        return HTMLResponse(content=DEFAULT_INDEX_HTML)                                     # Return a default HTML if file doesn't exist yet

    def serve_css__filename(self, filename: str) -> Response:                                         # Serve CSS files
        css_path = self.get_static_path(f'css/{filename}')
        if file_exists(css_path):
            return FileResponse(css_path, media_type="text/css")

        return Response(content="", media_type="text/css")                                  # Return empty CSS if file doesn't exist

    def serve_js__filename(self, filename: str) -> Response:                                          # Serve JavaScript files
        js_path = self.get_static_path(f'js/{filename}')

        if file_exists(js_path):
            return FileResponse(js_path, media_type="application/javascript")

        return Response(content="", media_type="application/javascript")                    # Return empty JS if file doesn't exist

    def serve_js__components__filename(self, filename: str) -> Response:                                          # Serve JavaScript files
        js_path = self.get_static_path(f'js/components/{filename}')

        if file_exists(js_path):
            return FileResponse(js_path, media_type="application/javascript")

        return Response(content="", media_type="application/javascript")                    # Return empty JS if file doesn't exist

    def setup_routes(self):                                                                # Main page
        self.add_route_get(self.index)
        self.add_route_get(self.serve_css__filename            )
        self.add_route_get(self.serve_js__filename             )
        self.add_route_get(self.serve_js__components__filename )



# Default HTML to use if index.html doesn't exist yet                                       # todo: move this file to the ./admin-ui/content/html folder
DEFAULT_INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastAPI Admin UI</title>
    <link rel="stylesheet" href="/admin/css/base.css">
    <link rel="stylesheet" href="/admin/css/layout.css">
    <link rel="stylesheet" href="/admin/css/components.css">
</head>
<body>
    <div id="app">
        <nav-header></nav-header>
        <div class="admin-layout">
            <nav-sidebar></nav-sidebar>
            <main id="main-content" class="main-content">
                <!-- Content will be loaded here -->
            </main>
        </div>
    </div>
    
    <script type="module" src="/admin/js/admin_ui.js"></script>
    <script type="module" src="/admin/js/components/navigation.js"></script>
    <script type="module" src="/admin/js/components/dashboard.js"></script>
    <script type="module" src="/admin/js/components/cookie_editor.js"></script>
    <script type="module" src="/admin/js/components/api_explorer.js"></script>
</body>
</html>"""