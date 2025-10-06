from unittest                                               import TestCase
from fastapi                                                import FastAPI
from osbot_fast_api.schemas.consts.consts__Fast_API         import ROUTES__CONFIG, ROUTE_REDIRECT_TO_DOCS
from osbot_utils.utils.Files                                import folder_exists, folder_name, files_names, files_list, parent_folder
from osbot_fast_api.api.Fast_API                            import Fast_API
from osbot_fast_api.examples.ex_1_simple                    import static_files
from osbot_fast_api.examples.ex_1_simple.Fast_API__Simple   import Fast_API__Simple, EX_1__FOLDER_NAME__STATIC_FOLDER, EX_1_ROUTES
from tests.unit.api.test_Fast_API                           import EXPECTED_ROUTES_PATHS


class test_Fast_API__Simple(TestCase):

    def setUp(self):
        self.enable_cors = True
        self.fast_api    = Fast_API__Simple(enable_cors=self.enable_cors).setup()
        self.client       = self.fast_api.client()
        #self.fast_api.http_events.add_header_request_id = False

    def test__init__(self):
        assert isinstance(self.fast_api, Fast_API__Simple)
        assert isinstance(self.fast_api, Fast_API        )
        assert type(self.fast_api.app()) is FastAPI
        assert self.fast_api.enable_cors is True

    def test_client__an_post(self):
        result_1 = self.client.post('/an-post')
        result_2 = self.client.get ('/an-post')

        assert result_1.status_code == 200
        assert result_1.json()      == 'an post method'
        assert result_2.status_code == 405
        assert result_2.json()      == {'detail': 'Method Not Allowed'}




    def test_path_static_folder(self):
        static_folder = self.fast_api.path_static_folder()
        assert static_folder is not None
        assert folder_exists(static_folder) is True
        assert folder_name(static_folder)   == EX_1__FOLDER_NAME__STATIC_FOLDER
        assert files_names(files_list(static_folder)).__contains__( 'aaa.txt') is True

    def test_route__docs(self):
        response = self.client.get('/docs')
        fast_api_request_id = response.headers.get('fast-api-request-id')
        assert response.status_code == 200
        assert 'Fast_API__Simple - Swagger UI' in response.text
        assert dict(response.headers) == {'content-length'     : '817'                      ,
                                          'content-type'       : 'text/html; charset=utf-8' ,
                                          'fast-api-request-id': fast_api_request_id        }


    def test_route__root(self):
        response            = self.client.get('/', follow_redirects=False)
        fast_api_request_id = response.headers.get('fast-api-request-id')
        assert response.status_code == 307
        assert response.headers.get('location') == '/docs'
        assert dict(response.headers) == {'content-length': '0', 'fast-api-request-id':fast_api_request_id, 'location': '/docs'}

    def test_routes(self):
        routes = self.fast_api.routes()
        assert routes ==  [ROUTE_REDIRECT_TO_DOCS] + ROUTES__CONFIG + EX_1_ROUTES

    def test_routes_paths(self):
        assert self.fast_api.routes_paths(expand_mounts=True) == sorted(EXPECTED_ROUTES_PATHS + ['/an-post', '/static'])

    def test_static_file(self):
        response = self.client.get('/static/aaa.txt')
        assert response.status_code == 200
        assert response.text        == 'this is a static file'

    def test_static_files__init__(self):
        assert folder_name(static_files.path) == 'static_files'

    def test_user_middleware(self):
        middlewares = self.fast_api.user_middlewares()
        middleware_1  = middlewares[0]
        middleware_2  = middlewares[1]

        assert len(middlewares)  == 3
        assert middleware_1      == {'function_name': None                                      ,
                                     'params'       : { 'allow_credentials': True               ,
                                                        'allow_headers': ['Content-Type', 'X-Requested-With', 'Origin', 'Accept', 'Authorization'],
                                                        'allow_methods': ['GET', 'POST', 'HEAD'],
                                                        'allow_origins': ['*'                  ],
                                                        'expose_headers': ['Content-Type', 'X-Requested-With', 'Origin', 'Accept', 'Authorization']},
                                     'type'          : 'CORSMiddleware'                         }
        assert middleware_2      == { 'function_name': None                                       ,
                                      'params'       : {'http_events': self.fast_api.http_events },
                                      'type'         : 'Middleware__Http_Request'                }




    # BUGS

    # def test_bug___CORS_headers_are_not_showing_in_headers(self):
    #     assert self.enable_cors is True
    #     response = self.client.get('/docs')
    #     fast_api_request_id = response.headers.get('fast-api-request-id')
    #     assert dict(response.headers) == {'content-length': '931',
    #                                       'fast-api-request-id': fast_api_request_id,
    #                                       'content-type': 'text/html; charset=utf-8'
    #                                       } # bug: the cors headers should show here