import requests
from fastapi.testclient                                                                             import TestClient
from osbot_fast_api.services.registry.Fast_API__Service__Registry__Client__Base                     import Fast_API__Service__Registry__Client__Base
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode import Enum__Fast_API__Service__Registry__Client__Mode
from osbot_fast_api.services.schemas.registry.collections.List__Fast_API__Registry__Env_Vars        import List__Fast_API__Registry__Env_Vars


# ═══════════════════════════════════════════════════════════════════════════════
# Test Client Implementation - Supports both IN_MEMORY and REMOTE modes
# ═══════════════════════════════════════════════════════════════════════════════

class Integration__Test__Client(Fast_API__Service__Registry__Client__Base):        # Full client implementation for testing

    _test_client : TestClient = None                                                # TestClient for IN_MEMORY mode

    def setup_from_env(self) -> 'Integration__Test__Client':
        return self

    def requests(self):                                                            # Returns appropriate transport
        if self.config.mode == Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY:
            if self._test_client is None and self.config.fast_api_app:
                self._test_client = TestClient(self.config.fast_api_app)
            return self._test_client
        return None                                                                # REMOTE mode uses requests library

    def health(self) -> bool:                                                      # Health check using appropriate mode
        try:
            # Use different paths for different modes
            if self.config.mode == Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY:
                path = "/health"                                                   # FastAPI route
            else:
                path = "/health.json"                                              # Static file server
            response = self.get(path)
            return response.get("status") == "healthy"
        except Exception:
            return False

    def get(self, path: str) -> dict:                                              # GET request abstraction
        if self.config.mode == Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY:
            client = self.requests()
            response = client.get(path)
            return response.json()
        elif self.config.mode == Enum__Fast_API__Service__Registry__Client__Mode.REMOTE:
            url = f"{self.config.base_url}{path}"
            headers = {}
            if self.config.api_key_name and self.config.api_key_value:
                headers[str(self.config.api_key_name)] = str(self.config.api_key_value)
            response = requests.get(url, headers=headers)
            return response.json()
        raise ValueError("Client mode not configured")

    def post(self, path: str, data: dict) -> dict:                                 # POST request abstraction
        if self.config.mode == Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY:
            client = self.requests()
            response = client.post(path, json=data)
            return response.json()
        elif self.config.mode == Enum__Fast_API__Service__Registry__Client__Mode.REMOTE:
            url = f"{self.config.base_url}{path}"
            headers = {"Content-Type": "application/json"}
            if self.config.api_key_name and self.config.api_key_value:
                headers[str(self.config.api_key_name)] = str(self.config.api_key_value)
            response = requests.post(url, json=data, headers=headers)
            return response.json()
        raise ValueError("Client mode not configured")

    @classmethod
    def env_vars(cls) -> List__Fast_API__Registry__Env_Vars:
        return List__Fast_API__Registry__Env_Vars()

    @classmethod
    def client_name(cls) -> str:
        return 'Integration__Test__Client'
