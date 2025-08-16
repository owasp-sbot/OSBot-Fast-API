import re

REGEX__SAFE__STR__FAST_API__TITLE = re.compile(r'[^a-zA-Z0-9 _()-]')


EXPECTED_ROUTES_METHODS = ['info', 'redirect_to_docs', 'routes__html', 'routes__json', 'status', 'version'         ]
EXPECTED_ROUTES_PATHS   = ['/'                  ,
                           '/config/info'       ,
                           '/config/routes/html',
                           '/config/routes/json',
                           '/config/status'     ,
                           '/config/version'    ]
EXPECTED_DEFAULT_ROUTES = ['/docs', '/openapi.json', '/redoc', '/static-docs'      ]


ROUTES__CONFIG          = [{ 'http_methods': ['GET'       ], 'http_path': '/config/info'       , 'method_name': 'info'        },
                           { 'http_methods': ['GET'       ], 'http_path': '/config/status'     , 'method_name': 'status'      },
                           { 'http_methods': ['GET'       ], 'http_path': '/config/version'    , 'method_name': 'version'     },
                           { 'http_methods': ['GET'       ], 'http_path': '/config/routes/json', 'method_name': 'routes__json'},
                           { 'http_methods': ['GET'       ], 'http_path': '/config/routes/html', 'method_name': 'routes__html'}]
ROUTES__STATIC_DOCS     = [{'http_methods': ['GET', 'HEAD'], 'http_path': '/static-docs'       , 'method_name': 'static-docs' }]
ROUTES_PATHS__CONFIG    = ['/config/status', '/config/version']