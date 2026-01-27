# ═══════════════════════════════════════════════════════════════════════════════
# Fast_API__Client__Requests
# Generic transport layer for service clients
# Handles IN_MEMORY (TestClient) and REMOTE (requests) modes transparently
# ═══════════════════════════════════════════════════════════════════════════════

import requests

from typing import Any, Dict, Type
from starlette.testclient                                                                               import TestClient
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import fast_api__service__registry
from osbot_fast_api.services.schemas.registry.Fast_API__Service__Registry__Client__Config               import Fast_API__Service__Registry__Client__Config
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode     import Enum__Fast_API__Service__Registry__Client__Mode
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.decorators.methods.cache_on_self                                                       import cache_on_self

# todo: service_type should have a specific base class
class Fast_API__Client__Requests(Type_Safe):                                    # Generic transport for all service clients
    service_type : Type[Type_Safe] = None                                                  # Subclass sets this to client type

    @cache_on_self
    def config(self) -> Fast_API__Service__Registry__Client__Config:            # Cached config lookup from registry
        config = fast_api__service__registry.config(self.service_type)
        if config is None:
            raise ValueError(f"{self.service_type.__name__} not registered in service registry")
        return config

    @cache_on_self
    def test_client(self) -> TestClient:                                        # TestClient for IN_MEMORY mode
        if self.config().fast_api_app is None:
            raise ValueError("IN_MEMORY mode requires fast_api_app in config")
        return TestClient(self.config().fast_api_app)

    @cache_on_self
    def session(self) -> requests.Session:                                      # requests.Session for REMOTE mode
        session = requests.Session()
        if self.config().api_key_value:
            session.headers['Authorization'] = f'Bearer {self.config().api_key_value}'
        return session

    def execute(self, method  : str            ,                                # HTTP method (GET, POST, etc)
                      path    : str            ,                                # Endpoint path
                      body    : Any       = None,                               # Request body
                      headers : Dict = None                                     # Additional headers
               ):                                                               # Execute request based on mode
        request_headers = {**self.auth_headers(), **(headers or {})}

        if self.config().mode == Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY:
            return self.execute_in_memory(method, path, body, request_headers)
        elif self.config().mode == Enum__Fast_API__Service__Registry__Client__Mode.REMOTE:
            return self.execute_remote(method, path, body, request_headers)
        else:
            raise ValueError("Client mode not configured")

    def execute_in_memory(self, method: str, path: str, body: Any, headers: Dict):
        method_func = getattr(self.test_client(), method.lower())
        if body:
            if type(body) is bytes:
                headers["Content-Type"] = "application/octet-stream"
                return method_func(path, data=body, headers=headers)
            else:
                return method_func(path, json=body, headers=headers)
        return method_func(path, headers=headers)

    def execute_remote(self, method: str, path: str, body: Any, headers: Dict):
        url         = f"{self.config().base_url}{path}"
        method_func = getattr(self.session(), method.lower())
        if body:
            if type(body) is bytes:
                headers["Content-Type"] = "application/octet-stream"
                return method_func(url, data=body, headers=headers)
            else:
                return method_func(url, json=body, headers=headers)
        return method_func(url, headers=headers)

    def auth_headers(self) -> Dict[str, str]:                                   # Get auth headers from config
        headers = {}
        if self.config().api_key_name and self.config().api_key_value:
            headers[str(self.config().api_key_name)] = str(self.config().api_key_value)
        return headers
