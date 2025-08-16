import re

# todo: the names of these variables need a bit of refactoring and normalising

REGEX__SAFE__STR__FAST_API__TITLE       = re.compile(r'[^a-zA-Z0-9 _()-]')

DEFAULT_ROUTES_PATHS                    = ['/', '/config/status', '/config/version']
DEFAULT__NAME__FAST_API                 = 'Fast_API'
ENV_VAR__FAST_API__AUTH__API_KEY__NAME  = 'FAST_API__AUTH__API_KEY__NAME'
ENV_VAR__FAST_API__AUTH__API_KEY__VALUE = 'FAST_API__AUTH__API_KEY__VALUE'

ROUTE_REDIRECT_TO_DOCS                  = {'http_methods': ['GET'        ], 'http_path': '/'      , 'method_name': 'redirect_to_docs'}
FAST_API_DEFAULT_ROUTES_PATHS           = ['/docs', '/docs/oauth2-redirect', '/openapi.json', '/redoc', '/static-docs']
FAST_API_DEFAULT_ROUTES                 = [ { 'http_methods': ['GET','HEAD'], 'http_path': '/openapi.json'         , 'method_name': 'openapi'              },
                                            ROUTE_REDIRECT_TO_DOCS                                                                                          ,
                                            { 'http_methods': ['GET'       ], 'http_path': '/docs'                 , 'method_name': 'swagger_ui_html'      },
                                            { 'http_methods': ['GET'       ], 'http_path': '/redoc'                , 'method_name': 'redoc_html'           }]


EXPECTED_ROUTES_METHODS                 = ['auth_cookie_form',
                                           'info'            ,
                                           'redirect_to_docs',
                                           'routes__html'    ,
                                           'routes__json'    ,
                                           'set_auth_cookie' ,
                                           'status'          ,
                                           'version'         ]
EXPECTED_ROUTES_PATHS                   = ['/'                     ,
                                           '/auth/auth-cookie-form',
                                           '/auth/set-auth-cookie' ,
                                           '/config/info'          ,
                                           '/config/routes/html'   ,
                                           '/config/routes/json'   ,
                                           '/config/status'        ,
                                           '/config/version'       ]
EXPECTED_DEFAULT_ROUTES                 = ['/docs', '/openapi.json', '/redoc', '/static-docs'      ]


ROUTES__CONFIG                          = [{ 'http_methods': ['GET'       ], 'http_path': '/config/info'          , 'method_name': 'info'               },
                                           { 'http_methods': ['GET'       ], 'http_path': '/config/status'        , 'method_name': 'status'             },
                                           { 'http_methods': ['GET'       ], 'http_path': '/config/version'       , 'method_name': 'version'            },
                                           { 'http_methods': ['GET'       ], 'http_path': '/config/routes/json'   , 'method_name': 'routes__json'       },
                                           { 'http_methods': ['GET'       ], 'http_path': '/config/routes/html'   , 'method_name': 'routes__html'       },
                                           { 'http_methods': ['GET'       ], 'http_path': '/auth/auth-cookie-form', 'method_name': 'auth_cookie_form'   },
                                           { 'http_methods': ['POST'      ], 'http_path': '/auth/set-auth-cookie' , 'method_name': 'set_auth_cookie'    },]
ROUTES__STATIC_DOCS                     = [{'http_methods': ['GET', 'HEAD'], 'http_path': '/static-docs'          , 'method_name': 'static-docs'        }]
ROUTES_PATHS__CONFIG                    = ['/config/status', '/config/version']