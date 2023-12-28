from unittest import TestCase

from fastapi import FastAPI
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import folder_exists, folder_name, files_names, files_list

from osbot_fast_api.api.Fast_API                          import Fast_API
from osbot_fast_api.examples.ex_1_simple.Fast_API__Simple import Fast_API__Simple, EX_1__FOLDER_NAME__STATIC_FOLDER


class test_Fast_API__Simple(TestCase):

    def setUp(self):
        self.fast_api__simple = Fast_API__Simple()

    def test__init__(self):
        assert isinstance(self.fast_api__simple, Fast_API__Simple)
        assert isinstance(self.fast_api__simple, Fast_API        )
        assert type(self.fast_api__simple.app()) is FastAPI

    def test_path_static_folder(self):
        static_folder = self.fast_api__simple.path_static_folder()
        assert static_folder is not None
        assert folder_exists(static_folder) is True
        assert folder_name(static_folder)   == EX_1__FOLDER_NAME__STATIC_FOLDER
        assert files_names(files_list(static_folder)) == ['aaa.txt']

    def test_routes(self):
        routes = self.fast_api__simple.routes()
        assert routes == [{'http_methods': ['GET'        ], 'http_path': '/'      , 'method_name': 'redirect_to_docs'},
                          {'http_methods': ['GET', 'HEAD'], 'http_path': '/static', 'method_name': 'static'          }]