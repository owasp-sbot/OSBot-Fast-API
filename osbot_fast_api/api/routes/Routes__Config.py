from fastapi.responses                              import HTMLResponse
from osbot_fast_api.api.routes.Fast_API__Routes     import Fast_API__Routes
from osbot_fast_api.utils.Fast_API__Routes__Paths   import Fast_API__Routes__Paths
from osbot_fast_api.utils.Fast_API__Server_Info     import fast_api__server_info
from osbot_fast_api.utils.Version                   import version__osbot_fast_api


class Routes__Config(Fast_API__Routes):
    tag  = 'config'

    def info(self):
        return fast_api__server_info.json()

    def status(self):
        return {'status':'ok'}

    def version(self):
        return {'version': version__osbot_fast_api}

    def routes__json(self):
        return Fast_API__Routes__Paths(app=self.app).routes_tree()

    def routes__html(self):
        html_content = Fast_API__Routes__Paths(app=self.app).routes_html()
        return HTMLResponse(content=html_content)

    def setup_routes(self):
        self.add_route_get(self.info       )
        self.add_route_get(self.status     )
        self.add_route_get(self.version    )
        self.add_route_get(self.routes__json)
        self.add_route_get(self.routes__html)