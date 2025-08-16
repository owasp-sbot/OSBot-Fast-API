from osbot_utils.utils.Files import path_combine, file_not_exists, file_create_bytes, parent_folder, folder_create
from osbot_utils.utils.Http  import GET_bytes

import osbot_fast_api
from fastapi                                import FastAPI
from fastapi.openapi.docs                   import get_swagger_ui_html, get_redoc_html
from osbot_utils.type_safe.Type_Safe        import Type_Safe

NAME__STATIC__DOCS           = 'static-docs'

URL__STATIC__DOCS            = f'/{NAME__STATIC__DOCS}'
URL__REDOC__JS               = f"/redoc/redoc.standalone.js"
URL__REDOC__FAVICON          = f"/redoc/favicon.png"
URL__SWAGGER__JS             = f"/swagger-ui/swagger-ui-bundle.js"
URL__SWAGGER__CSS            = f"/swagger-ui/swagger-ui.css"
URL__SWAGGER__FAVICON        = f"/swagger-ui/favicon.png"

FILE_PATH__STATIC__DOCS      = path_combine(osbot_fast_api.path, NAME__STATIC__DOCS)

TEXT__SWAGGER__TITLE_SUFFIX  = " - Swagger UI"
TEXT__REDOC__TITLE_SUFFIX    = " - ReDoc"

class Fast_API__Offline_Docs(Type_Safe):            # Manages offline documentation assets for FastAPI
    app                 : FastAPI
    SWAGGER_UI_VERSION  : str   = "5.9.0"                   # Update as needed
    REDOC_VERSION       : str   = "2.1.3"


    def setup(self):

        @self.app.get("/docs", include_in_schema=False)         # this is working
        async def swagger_ui_html():
            return get_swagger_ui_html(openapi_url        = self.app.openapi_url                            ,
                                       title               = self.app.title + TEXT__SWAGGER__TITLE_SUFFIX   ,
                                       swagger_js_url      = f"{URL__STATIC__DOCS}{URL__SWAGGER__JS}"      ,
                                       swagger_css_url     = f"{URL__STATIC__DOCS}{URL__SWAGGER__CSS}"     ,
                                       swagger_favicon_url = f"{URL__STATIC__DOCS}{URL__SWAGGER__FAVICON}" )

        @self.app.get("/redoc", include_in_schema=False)
        async def redoc_html():
            return get_redoc_html(openapi_url       = self.app.openapi_url                        ,
                                  title             = self.app.title + TEXT__REDOC__TITLE_SUFFIX  ,
                                  redoc_js_url      = f"{URL__STATIC__DOCS}{URL__REDOC__JS}"     ,
                                  redoc_favicon_url = f"{URL__STATIC__DOCS}{URL__REDOC__FAVICON}",
                                  with_google_fonts = False                                     ) # removes this font insert <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        return self


    def save_resources_to_static_folder(self):
        # note: this actually adds 2.6Mb to this project (which when this was added only had 3.5Mb of size!
        # note: the current files included in the source code where downloaded on the 16th Aug 2025
        static_files = [(URL__SWAGGER__JS      , "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"),
                        (URL__SWAGGER__CSS     , "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"      ),
                        (URL__SWAGGER__FAVICON , "https://fastapi.tiangolo.com/img/favicon.png"                       ),
                        (URL__REDOC__JS        , "https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js"   ),
                        (URL__REDOC__FAVICON   , "https://fastapi.tiangolo.com/img/favicon.png"                       )]

        for (file_path, file_url) in static_files:          # this will only download the files when they don't exist locally
            full_local_path = path_combine(FILE_PATH__STATIC__DOCS, file_path)
            if file_not_exists(full_local_path):
                file_bytes  = GET_bytes(file_url)
                file_folder = parent_folder(full_local_path)
                folder_create(file_folder)
                file_create_bytes(path=full_local_path, bytes=file_bytes)
