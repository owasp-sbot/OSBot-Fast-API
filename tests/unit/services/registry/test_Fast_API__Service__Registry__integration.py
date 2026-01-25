# ═══════════════════════════════════════════════════════════════════════════════
# Integration Tests for Fast_API__Service__Registry
# Tests IN_MEMORY and REMOTE modes with actual FastAPI apps
# Uses Temp_Web_Server from osbot_utils for REMOTE mode testing
# ═══════════════════════════════════════════════════════════════════════════════
from unittest                                                                                  import TestCase
from fastapi                                                                                   import FastAPI
from fastapi.testclient                                                                        import TestClient
from osbot_utils.testing.Temp_Web_Server                                                       import Temp_Web_Server
from osbot_utils.testing.Temp_Folder                                                           import Temp_Folder
from osbot_utils.testing.__                                                                    import __
from osbot_utils.testing.__helpers                                                             import obj
from osbot_fast_api.services.registry.Fast_API__Service__Registry                              import Fast_API__Service__Registry
from osbot_fast_api.services.schemas.registry.enums.Enum__Client__Mode                         import Enum__Client__Mode
from tests.unit.services.registry.test_clients.Integration__Test__Client                       import Integration__Test__Client


# ═══════════════════════════════════════════════════════════════════════════════
# Test FastAPI App - Simple API for testing
# ═══════════════════════════════════════════════════════════════════════════════

def create_test_app() -> FastAPI:                                                  # Creates a simple FastAPI app for testing
    app = FastAPI(title="Test API")

    @app.get("/health")
    def health():
        return {"status": "healthy"}

    @app.get("/users/{user_id}")
    def get_user(user_id: int):
        return {"id": user_id, "name": f"User {user_id}"}

    @app.post("/echo")
    def echo(data: dict):
        return {"received": data}

    return app




# ═══════════════════════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════

class test_Fast_API__Service__Registry__integration(TestCase):

    # ───────────────────────────────────────────────────────────────────────────
    # IN_MEMORY Mode Tests
    # ───────────────────────────────────────────────────────────────────────────

    def test__in_memory_mode__health_check(self):                                  # Test health check in IN_MEMORY mode
        app = create_test_app()

        with Fast_API__Service__Registry() as registry:
            client = Integration__Test__Client()
            client.config.mode         = Enum__Client__Mode.IN_MEMORY
            client.config.fast_api_app = app

            registry.register(client)

            registered_client = registry.client(Integration__Test__Client)
            assert registered_client.health() is True

    def test__in_memory_mode__get_request(self):                                   # Test GET request in IN_MEMORY mode
        app = create_test_app()

        with Fast_API__Service__Registry() as registry:
            client = Integration__Test__Client()
            client.config.mode         = Enum__Client__Mode.IN_MEMORY
            client.config.fast_api_app = app

            registry.register(client)

            registered_client = registry.client(Integration__Test__Client)
            user = registered_client.get("/users/42")
            assert obj(user)    == __(id=42, name='User 42')
            assert user["id"]   == 42
            assert user["name"] == "User 42"

    def test__in_memory_mode__post_request(self):                                  # Test POST request in IN_MEMORY mode
        app = create_test_app()

        with Fast_API__Service__Registry() as registry:
            client = Integration__Test__Client()
            client.config.mode         = Enum__Client__Mode.IN_MEMORY
            client.config.fast_api_app = app

            registry.register(client)

            registered_client = registry.client(Integration__Test__Client)
            result = registered_client.post("/echo", {"message": "hello"})

            assert result["received"]["message"] == "hello"

    def test__in_memory_mode__requests_returns_test_client(self):                  # Verify requests() returns TestClient
        app = create_test_app()

        client = Integration__Test__Client()
        client.config.mode         = Enum__Client__Mode.IN_MEMORY
        client.config.fast_api_app = app

        transport = client.requests()

        assert type(transport) is TestClient

    # ───────────────────────────────────────────────────────────────────────────
    # REMOTE Mode Tests - Using Temp_Web_Server
    # ───────────────────────────────────────────────────────────────────────────

    def test__remote_mode__health_check(self):                                     # Test health check in REMOTE mode
        with Temp_Folder() as folder:
            folder.add_file('health.json', '{"status": "healthy"}')                # Use .json extension

            with Temp_Web_Server(root_folder=folder.path()) as server:
                with Fast_API__Service__Registry() as registry:
                    client = Integration__Test__Client()
                    client.config.mode     = Enum__Client__Mode.REMOTE
                    client.config.base_url = server.url().rstrip('/')              # Remove trailing slash

                    registry.register(client)

                    # Override health to use the .json file
                    registered_client = registry.client(Integration__Test__Client)
                    response = registered_client.get("/health.json")
                    assert response.get("status") == "healthy"

    def test__remote_mode__get_request(self):                                      # Test GET request in REMOTE mode
        with Temp_Folder() as folder:
            folder.add_file('data.json', '{"id": 1, "name": "Test"}')              # Create API endpoint file (no subdir)

            with Temp_Web_Server(root_folder=folder.path()) as server:
                with Fast_API__Service__Registry() as registry:
                    client = Integration__Test__Client()
                    client.config.mode     = Enum__Client__Mode.REMOTE
                    client.config.base_url = server.url().rstrip('/')

                    registry.register(client)

                    registered_client = registry.client(Integration__Test__Client)
                    result = registered_client.get("/data.json")

                    assert result["id"]   == 1
                    assert result["name"] == "Test"

    def test__remote_mode__with_api_key_headers(self):                             # Test API key headers in REMOTE mode
        with Temp_Folder() as folder:
            folder.add_file('endpoint.json', '{"access": "granted"}')              # Use .json extension (no subdir)

            with Temp_Web_Server(root_folder=folder.path()) as server:
                with Fast_API__Service__Registry() as registry:
                    client = Integration__Test__Client()
                    client.config.mode          = Enum__Client__Mode.REMOTE
                    client.config.base_url      = server.url().rstrip('/')
                    client.config.api_key_name  = 'X-API-KEY'
                    client.config.api_key_value = 'secret-123'

                    registry.register(client)

                    registered_client = registry.client(Integration__Test__Client)
                    result = registered_client.get("/endpoint.json")

                    assert result["access"] == "granted"                           # Request succeeded with headers

    # ───────────────────────────────────────────────────────────────────────────
    # Mode Switching Tests
    # ───────────────────────────────────────────────────────────────────────────

    def test__mode_switching__in_memory_to_remote(self):                           # Test switching from IN_MEMORY to REMOTE
        app = create_test_app()

        with Fast_API__Service__Registry() as registry:
            # Start with IN_MEMORY mode
            client = Integration__Test__Client()
            client.config.mode         = Enum__Client__Mode.IN_MEMORY
            client.config.fast_api_app = app

            registry.register(client)
            assert registry.client(Integration__Test__Client).health() is True

            # Switch to REMOTE mode
            with Temp_Folder() as folder:
                folder.add_file('health.json', '{"status": "healthy"}')

                with Temp_Web_Server(root_folder=folder.path()) as server:
                    remote_client = Integration__Test__Client()
                    remote_client.config.mode     = Enum__Client__Mode.REMOTE
                    remote_client.config.base_url = server.url().rstrip('/')

                    registry.register(remote_client)                               # Re-register with new mode
                    assert registry.client(Integration__Test__Client).health() is True
                    assert registry.client(Integration__Test__Client).config.mode == Enum__Client__Mode.REMOTE

    def test__multiple_clients__different_modes(self):                             # Test multiple clients with different modes
        app = create_test_app()

        # Create a second client type for testing
        class Secondary__Test__Client(Integration__Test__Client):
            @classmethod
            def client_name(cls) -> str:
                return 'Secondary__Test__Client'

        with Temp_Folder() as folder:
            folder.add_file('health.json', '{"status": "healthy"}')

            with Temp_Web_Server(root_folder=folder.path()) as server:
                with Fast_API__Service__Registry() as registry:
                    # First client - IN_MEMORY mode
                    in_memory_client = Integration__Test__Client()
                    in_memory_client.config.mode         = Enum__Client__Mode.IN_MEMORY
                    in_memory_client.config.fast_api_app = app

                    # Second client - REMOTE mode
                    remote_client = Secondary__Test__Client()
                    remote_client.config.mode     = Enum__Client__Mode.REMOTE
                    remote_client.config.base_url = server.url().rstrip('/')

                    registry.register(in_memory_client)
                    registry.register(remote_client)

                    # Both clients should work independently
                    assert registry.client(Integration__Test__Client).config.mode  == Enum__Client__Mode.IN_MEMORY
                    assert registry.client(Secondary__Test__Client).config.mode    == Enum__Client__Mode.REMOTE

                    assert registry.client(Integration__Test__Client).health() is True
                    assert registry.client(Secondary__Test__Client).health()   is True

    # ───────────────────────────────────────────────────────────────────────────
    # Error Handling Tests
    # ───────────────────────────────────────────────────────────────────────────

    def test__unconfigured_mode__raises_error(self):                               # Test error when mode not configured
        client = Integration__Test__Client()                                       # No mode set

        with self.assertRaises(ValueError) as context:
            client.get("/test")

        assert "Client mode not configured" in str(context.exception)

    def test__remote_mode__connection_failure__returns_false_health(self):         # Test health check fails on connection error
        client = Integration__Test__Client()
        client.config.mode     = Enum__Client__Mode.REMOTE
        client.config.base_url = 'http://localhost:99999'                          # Non-existent server

        assert client.health() is False                                            # Should return False, not raise
