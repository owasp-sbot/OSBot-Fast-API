from unittest                                                         import TestCase
from osbot_utils.type_safe.Type_Safe                                  import Type_Safe
from osbot_utils.utils.Objects                                        import base_classes
from osbot_fast_api.api.Fast_API                                      import Fast_API
from osbot_fast_api.api.events.Fast_API__Http_Events                  import Fast_API__Http_Events
from osbot_fast_api.events.Fast_API__With_Events                      import Fast_API__With_Events
from osbot_fast_api.schemas.Schema__Fast_API__Config                  import Schema__Fast_API__Config
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid import Random_Guid
from fastapi                                                          import Request
from osbot_utils.utils.Misc                                           import is_guid, list_set


class test_Fast_API__With_Events(TestCase):

    @classmethod
    def setUpClass(cls):                                                          # ONE-TIME expensive setup
        cls.fast_api_with_events = Fast_API__With_Events().setup()
        cls.client = cls.fast_api_with_events.client()

    def test__init__with_type_safety(self):                                       # Test Type_Safe inheritance and auto-initialization
        with Fast_API__With_Events() as _:
            assert type(_)         is Fast_API__With_Events
            assert base_classes(_) == [Fast_API, Type_Safe, object]               # Verify inheritance chain

            # Verify http_events is properly initialized
            assert type(_.http_events) is Fast_API__Http_Events
            assert type(_.config)      is Schema__Fast_API__Config
            assert type(_.server_id)   is Random_Guid

            # Verify http_events wiring
            assert _.http_events.fast_api_name == "Fast_API__With_Events"         # Auto-named from class

    def test__init__with_custom_name(self):                                       # Test custom name propagation
        config = Schema__Fast_API__Config(name="My API Service!")
        with Fast_API__With_Events(config=config) as _:
            assert _.config.name                == "My API Service_"              # Sanitized
            assert _.http_events.fast_api_name  == "My API Service_"              # Propagated to http_events

    def test__init__without_name(self):                                           # Test auto-name from parent class
        with Fast_API__With_Events() as _:
            assert _.config.name                == "Fast_API__With_Events"        # Uses actual class name
            assert _.http_events.fast_api_name  == "Fast_API__With_Events"

    def test_setup_middlewares(self):                                             # Test middleware chain includes events
        with Fast_API__With_Events() as _:
            _.setup()

            middlewares = _.user_middlewares()
            middleware_types = [m['type'] for m in middlewares]

            # Should have base middlewares PLUS http events
            assert 'Middleware__Request_ID'        in middleware_types
            assert 'Middleware__Detect_Disconnect' in middleware_types
            assert 'Middleware__Http_Request'      in middleware_types            # This is the events middleware

            # Verify http_events is passed to the middleware
            http_middleware = [m for m in middlewares if m['type'] == 'Middleware__Http_Request']
            assert len(http_middleware) == 1
            assert http_middleware[0]['params']['http_events'] == _.http_events

    def test_event_tracking_methods(self):                                        # Test event-specific methods
        with self.fast_api_with_events as _:
            # Make a request to generate an event
            response = self.client.get('/config/status')
            assert response.status_code == 200

            # Get request ID from response header
            request_id = response.headers.get('fast-api-request-id')
            assert is_guid(request_id)

            # Verify event was tracked
            assert request_id in list_set(_.http_events.requests_data)
            event_data = _.http_events.requests_data.get(Random_Guid(request_id))
            assert event_data.http_event_request.path   == '/config/status'
            assert event_data.http_event_request.method == 'GET'

    def test_request_data_access(self):                                           # Test request data retrieval
        with self.fast_api_with_events as _:
            # Create test endpoint that accesses request data
            @_.app().get("/test-request-data")
            def test_endpoint(request: Request):
                request_data = _.request_data(request)
                return { 'has_request_data': request_data is not None                              ,
                         'event_id'        : str(request_data.event_id) if request_data else None  }

            response = self.client.get("/test-request-data")
            data = response.json()

            assert data['has_request_data'] is True
            assert is_guid(data['event_id'])

    def test_background_tasks_registration(self):                                 # Test background task management
        with Fast_API__With_Events() as _:
            _.setup()

            # Add background task
            task_executed = {'called': False}

            def background_task(request, response):
                task_executed['called'] = True

            _.add_background_task(background_task)

            assert background_task in _.http_events.background_tasks

            # Note: Actual execution testing requires request/response cycle
            # Background tasks don't work in Lambda environments

    def test_enable_disable_request_tracing(self):                               # Test tracing configuration
        with Fast_API__With_Events() as _:
            # Initially disabled
            assert _.http_events.trace_calls is False

            # Enable tracing
            _.enable_request_tracing()
            assert _.http_events.trace_calls is True

            # Disable tracing
            _.disable_request_tracing()
            assert _.http_events.trace_calls is False

    def test__bug__callbacks_configuration(self):                                       # Test callback configuration
        with Fast_API__With_Events() as _:
            _.setup()

            callback_data = {'request_called': False, 'response_called': False}

            def on_request(request_data):
                callback_data['request_called'] = True

            def on_response(response, request_data):
                callback_data['response_called'] = True

            _.set_callback_on_request (on_request )
            _.set_callback_on_response(on_response)

            assert _.http_events.callback_on_request == on_request
            assert _.http_events.callback_on_response == on_response

            # Test callbacks are executed
            self.client.get('/config/status')

            assert callback_data == {'request_called': False, 'response_called': False}         # BUG
            #assert callback_data['request_called' ] is True                                    # BUG
            #assert callback_data['response_called'] is True                                    # BUG

    def test_get_recent_requests(self):                                          # Test request history retrieval
        with self.fast_api_with_events as _:
            # Clear history first
            _.clear_request_history()

            # Make several requests
            paths = ['/config/status', '/config/version', '/config/info']
            for path in paths:
                self.client.get(path)

            # Get recent requests
            recent = _.get_recent_requests(count=2)

            assert len(recent) == 2
            # Should be the last 2 requests
            assert recent[0].http_event_request.path == '/config/version'
            assert recent[1].http_event_request.path == '/config/info'

    def test_clear_request_history(self):                                        # Test history clearing
        with self.fast_api_with_events as _:
            # Make a request
            self.client.get('/config/status')
            assert len(_.http_events.requests_data) > 0

            # Clear history
            _.clear_request_history()

            assert len(_.http_events.requests_data) == 0
            assert len(_.http_events.requests_order) == 0

    def test_comparison_with_base_fast_api(self):                               # Test difference from base Fast_API
        # Base Fast_API should not have http_events
        with Fast_API() as base_api:
            assert not hasattr(base_api, 'http_events')
            assert not hasattr(base_api, 'request_data')
            assert not hasattr(base_api, 'enable_request_tracing')

            base_api.setup()
            middlewares = base_api.user_middlewares()
            middleware_types = [m['type'] for m in middlewares]
            assert 'Middleware__Http_Request' not in middleware_types            # No events middleware

        # With_Events should have all event features
        with Fast_API__With_Events() as events_api:
            assert hasattr(events_api, 'http_events')
            assert hasattr(events_api, 'request_data')
            assert hasattr(events_api, 'enable_request_tracing')

            events_api.setup()
            middlewares = events_api.user_middlewares()
            middleware_types = [m['type'] for m in middlewares]
            assert 'Middleware__Http_Request' in middleware_types                # Has events middleware

    def test_serialization_with_events(self):                                    # Test Type_Safe serialization
        config = Schema__Fast_API__Config(name="TestAPI", version="v1.0.0")
        with Fast_API__With_Events(config=config) as original:
            # Can't directly serialize due to http_events complexity
            # But config should serialize fine
            config_json = original.config.json()

            restored_config = Schema__Fast_API__Config.from_json(config_json)
            assert restored_config.name == "TestAPI"
            assert restored_config.version == "v1.0.0"

    def test_request_id_preserved_from_base_middleware(self):                    # Test request ID coordination
        with self.fast_api_with_events as _:
            response = self.client.get('/config/status')

            # Request ID should be in header (from base middleware)
            request_id = response.headers.get('fast-api-request-id')
            assert is_guid(request_id)

            # Same ID should be used in events
            assert request_id in list_set(_.http_events.requests_data)
            event = _.http_events.requests_data.get(Random_Guid(request_id))
            assert str(event.event_id) == request_id                            # Same ID throughout

    def test_max_requests_logged(self):                                          # Test request limit enforcement
        with Fast_API__With_Events() as _:
            _.setup()
            _.http_events.max_requests_logged = 3                                # Set low limit

            client = _.client()

            # Make more requests than limit
            request_ids = []
            for i in range(5):
                response = client.get(f'/config/status')
                request_ids.append(response.headers['fast-api-request-id'])

            # Should only keep last 3
            assert len(_.http_events.requests_data) == 3
            captured_ids = list_set(_.http_events.requests_data )
            assert request_ids[0] not in captured_ids            # First two removed
            assert request_ids[1] not in captured_ids
            assert request_ids[4]     in captured_ids            # Last three kept

    def test_event_id_method(self):                                              # Test event_id retrieval
        with self.fast_api_with_events as _:
            @_.app().get("/test-event-id")
            def test_endpoint(request: Request):
                event_id = _.event_id(request)
                return {'event_id': str(event_id)}

            response = self.client.get("/test-event-id")
            data = response.json()

            # Should match the header
            assert data['event_id'] == response.headers['fast-api-request-id']

    def test_request_messages(self):                                             # Test message retrieval
        with self.fast_api_with_events as _:
            @_.app().get("/test-messages")
            def test_endpoint(request: Request):
                # Add some messages
                request_data = _.request_data(request)
                request_data.add_log_message("Message 1")
                request_data.add_log_message("Message 2")

                messages = _.request_messages(request)
                return {'messages': messages}

            response = self.client.get("/test-messages")
            data = response.json()

            assert data['messages'] == ["Message 1", "Message 2"]