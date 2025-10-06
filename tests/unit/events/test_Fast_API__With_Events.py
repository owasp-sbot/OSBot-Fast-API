from unittest import TestCase

import pytest

from osbot_fast_api.events.Fast_API__With_Events import Fast_API__With_Events
from osbot_fast_api.schemas.Schema__Fast_API__Config import Schema__Fast_API__Config


class test_Fast_API__With_Events(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pytest.skip("fix tests after refactoring")

    def test__init__with_type_safety(self):
        with Fast_API__With_Events() as _:
            assert type(_.http_events)           is Fast_API__With_Events

    def test__init__with_custom_name(self):                                        # Test custom name initialization
        config = Schema__Fast_API__Config(name = "My API Service!")
        with Fast_API__With_Events(config=config) as _:
            assert _.config.name               == "My API Service_"                # Sanitized by Safe_Str__Fast_API__Name
            assert _.http_events.fast_api_name == "My API Service_"                # Propagated to http_events

    def test__init__without_name(self):                                            # Test auto-name from class
        with Fast_API__With_Events() as _:
            assert _.config.name               == "Fast_API"                       # Uses class name
            assert _.http_events.fast_api_name == "Fast_API"

    def test_setup_middleware_http_events(self):                                   # Test HTTP events middleware
        with Fast_API() as _:
            _.setup_middleware__http_events()

            middlewares = _.user_middlewares()
            http_middleware = [m for m in middlewares if m['type'] == 'Middleware__Http_Request']

            assert len(http_middleware) == 1
            assert http_middleware[0]['params']['http_events'] == _.http_events

    def test_background_tasks_registration(self):                                      # Test background task functionality
        with Fast_API() as _:
            _.setup()

            def background_task(request, response):                                     # Add background task
                pass

            _.http_events.background_tasks.append(background_task)

            # todo: Verify task gets added to response
            #       This needs integration testing with actual request/response
            #       note: background_tasks doesn't work in Lambdas (which is why this is not usually used in services created from this Fast_API class


    def test_user_middleware(self):
        assert self.fast_api.user_middlewares() == [{'function_name': None, 'params': {}, 'type': 'Middleware__Detect_Disconnect'},
                                                    {'function_name': None, 'params': {}, 'type': 'Middleware__Request_ID'       }]

        #http_events = self.fast_api.http_events
        # params = {'http_events' : http_events}
        # assert self.fast_api.user_middlewares() == [{'function_name': None, 'params': params, 'type': 'Middleware__Http_Request'     },
        #                                             {'function_name': None, 'params': {}     ,'type': 'Middleware__Detect_Disconnect'}]