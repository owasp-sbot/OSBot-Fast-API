# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Fast_API__Client__Requests
# Validates generic transport layer with IN_MEMORY and REMOTE modes
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from fastapi                                                                                            import FastAPI
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import fast_api__service__registry
from osbot_fast_api.services.registry.Fast_API__Service__Registry__Client__Base                         import Fast_API__Service__Registry__Client__Base
from osbot_fast_api.services.registry.Fast_API__Client__Requests                                        import Fast_API__Client__Requests
from osbot_fast_api.services.schemas.registry.Fast_API__Service__Registry__Client__Config               import Fast_API__Service__Registry__Client__Config
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode     import Enum__Fast_API__Service__Registry__Client__Mode
from osbot_utils.utils.Objects                                                                          import base_classes
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe


# ═══════════════════════════════════════════════════════════════════════════════
# Test FastAPI App
# ═══════════════════════════════════════════════════════════════════════════════

def create_test_app() -> FastAPI:                                               # Creates a simple FastAPI app for testing
    app = FastAPI(title="Test API")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/users/{user_id}")
    def get_user(user_id: int):
        return {"id": user_id, "name": f"User {user_id}"}

    @app.post("/echo")
    def echo(data: dict):
        return {"received": data}

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# Fake Client and Requests for Testing
# ═══════════════════════════════════════════════════════════════════════════════

class Fake__Test__Service__Client(Fast_API__Service__Registry__Client__Base):   # Test double client
    pass


class Fake__Test__Service__Client__Requests(Fast_API__Client__Requests):        # Test double requests
    service_type : type = Fake__Test__Service__Client


# ═══════════════════════════════════════════════════════════════════════════════
# Unit Tests
# ═══════════════════════════════════════════════════════════════════════════════

class test_Fast_API__Client__Requests(TestCase):

    def setUp(self):
        fast_api__service__registry.clear()                                     # Reset global registry

    def tearDown(self):
        fast_api__service__registry.clear()                                     # Clean up

    def test__init__(self):                                                     # Test auto-initialization
        with Fast_API__Client__Requests() as _:
            assert type(_)         is Fast_API__Client__Requests
            assert base_classes(_) == [Type_Safe, object]
            assert _.service_type  is None

    def test__config__not_registered__raises_error(self):                       # Test error when not registered
        requests = Fake__Test__Service__Client__Requests()

        with self.assertRaises(ValueError) as context:
            requests.config()

        assert "Fake__Test__Service__Client not registered" in str(context.exception)

    def test__config__registered__returns_config(self):                         # Test config lookup
        config = Fast_API__Service__Registry__Client__Config(mode     = Enum__Fast_API__Service__Registry__Client__Mode.REMOTE,
                                                             base_url = 'https://example.com'                                 )
        fast_api__service__registry.register(Fake__Test__Service__Client, config)

        requests = Fake__Test__Service__Client__Requests()

        assert requests.config()         is config
        assert requests.config().mode    == Enum__Fast_API__Service__Registry__Client__Mode.REMOTE


    # ═══════════════════════════════════════════════════════════════════════════════
    # Error Handling Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__execute__mode_not_configured__raises_error(self):                 # Test error when mode is None
        config = Fast_API__Service__Registry__Client__Config()                  # mode = None
        fast_api__service__registry.register(Fake__Test__Service__Client, config)

        requests = Fake__Test__Service__Client__Requests()

        with self.assertRaises(ValueError) as context:
            requests.execute("GET", "/health")

        assert "Client mode not configured" in str(context.exception)

    def test__test_client__no_app__raises_error(self):                          # Test error when no FastAPI app
        config = Fast_API__Service__Registry__Client__Config(mode = Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY)
        fast_api__service__registry.register(Fake__Test__Service__Client, config)

        requests = Fake__Test__Service__Client__Requests()

        with self.assertRaises(ValueError) as context:
            requests.test_client()

        assert "IN_MEMORY mode requires fast_api_app" in str(context.exception)
