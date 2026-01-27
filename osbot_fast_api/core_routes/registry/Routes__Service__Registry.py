# ═══════════════════════════════════════════════════════════════════════════════
# Routes__Service__Registry - REST API for service registry introspection
# Provides endpoints for viewing registered services, health checks, and diagnostics
#
# Path pattern: /registry/...
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                             import List, Optional
from osbot_fast_api.api.decorators.route_path                                                           import route_path
from osbot_fast_api.api.routes.Fast_API__Routes                                                         import Fast_API__Routes
from osbot_fast_api.schemas.core_routes.registry.Schema__Registry__Responses                            import Schema__Registry__Status, Schema__Registry__Health__Summary, Schema__Registry__Service__Health
from osbot_fast_api.schemas.core_routes.registry.Schema__Registry__Service__Info                        import Schema__Registry__Service__Info
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import Fast_API__Service__Registry
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import fast_api__service__registry
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List import Type_Safe__List

TAG__ROUTES_REGISTRY = 'registry'

ROUTES_PATHS__REGISTRY = [
    f'/{TAG__ROUTES_REGISTRY}/status'                   ,
    f'/{TAG__ROUTES_REGISTRY}/services'                 ,
    f'/{TAG__ROUTES_REGISTRY}/services/{{service_name}}',
    f'/{TAG__ROUTES_REGISTRY}/health'                   ,
    f'/{TAG__ROUTES_REGISTRY}/health/{{service_name}}'  ,
]


# todo: refactor the business logic in this file into a services class
class Routes__Service__Registry(Fast_API__Routes):                              # Service registry introspection routes
    tag      : str                       = TAG__ROUTES_REGISTRY                 # Route tag
    registry : Fast_API__Service__Registry = None                               # Registry to inspect (defaults to global)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.registry is None:
            self.registry = fast_api__service__registry

    # ═══════════════════════════════════════════════════════════════════════════════
    # Status Endpoint
    # ═══════════════════════════════════════════════════════════════════════════════

    def status(self) -> Schema__Registry__Status:                               # GET /registry/status
        """Get overall registry status."""
        service_names = [self._get_service_name(client_type)
                        for client_type in self.registry.configs.keys()]

        return Schema__Registry__Status(
            registered_count = len(self.registry.configs)      ,
            stack_depth      = self.registry.configs__stack_size(),
            services         = service_names
        )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Services Endpoints
    # ═══════════════════════════════════════════════════════════════════════════════

    #def services(self) -> List[Schema__Registry__Service__Info]:               # GET /registry/services : List all registered services with their configuration (sanitized).
    def services(self) -> List:                                                 # todo: figure why the Schema__Registry__Service__Info class is creating issues with pydantic serialisation
        results = Type_Safe__List(expected_type=Schema__Registry__Service__Info)
        for client_type, config in self.registry.configs.items():
            info = self._build_service_info(client_type, config)
            results.append(info.json())
        return results.json()

    @route_path('/services/{service_name}')
    def service__get(self,                                                      # GET /registry/services/{service_name} | Get configuration for a specific service (sanitized).
                     service_name: str
                ) -> Schema__Registry__Service__Info:
        client_type = self._find_client_type(service_name)
        if client_type is None:
            return None

        config = self.registry.config(client_type)
        return self._build_service_info(client_type, config)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Health Endpoints
    # ═══════════════════════════════════════════════════════════════════════════════

    def health(self) -> Schema__Registry__Health__Summary:                      # GET /registry/health
        """Health check all registered services."""
        results = []
        healthy_count = 0

        for client_type in self.registry.configs.keys():
            health = self._check_service_health(client_type)
            results.append(health)
            if health.healthy:
                healthy_count += 1

        return Schema__Registry__Health__Summary(
            total_services  = len(results)              ,
            healthy_count   = healthy_count             ,
            unhealthy_count = len(results) - healthy_count,
            services        = results
        )

    @route_path('/health/{service_name}')
    def health__service(self, service_name: str                                 # GET /registry/health/{service_name}
                       ) -> Schema__Registry__Service__Health:
        """Health check a specific service."""
        client_type = self._find_client_type(service_name)
        if client_type is None:
            return Schema__Registry__Service__Health(
                service_name = service_name     ,
                healthy      = False            ,
                mode         = 'NOT_REGISTERED' ,
                error        = f"Service '{service_name}' not found in registry"
            )

        return self._check_service_health(client_type)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def _get_service_name(self, client_type: type) -> str:                      # Extract service name from type
        return client_type.__name__

    def _get_service_module(self, client_type: type) -> str:                    # Extract module from type
        return client_type.__module__

    def _find_client_type(self, service_name: str) -> Optional[type]:           # Find client type by name
        for client_type in self.registry.configs.keys():
            if client_type.__name__ == service_name:
                return client_type
        return None

    def _build_service_info(self, client_type: type, config                     # Build sanitized service info
                           ) -> Schema__Registry__Service__Info:
        mode_str = config.mode.value if config.mode else 'UNKNOWN'

        # Sanitize base_url (hide sensitive path components if needed)
        base_url = None
        if config.base_url:
            base_url = str(config.base_url)

        return Schema__Registry__Service__Info(
            service_name   = self._get_service_name(client_type)  ,
            service_module = self._get_service_module(client_type),
            mode           = mode_str                             ,
            base_url       = base_url                             ,
            has_api_key    = bool(config.api_key_name and config.api_key_value),
            has_fast_api   = config.fast_api_app is not None      ,
        )

    def _check_service_health(self, client_type: type                           # Check health for a service
                             ) -> Schema__Registry__Service__Health:
        config       = self.registry.config(client_type)
        service_name = self._get_service_name(client_type)
        mode_str     = config.mode.value if config.mode else 'UNKNOWN'

        try:
            # Create client instance and call health()
            client = client_type()

            # Check if client has health method
            if hasattr(client, 'health') and callable(client.health):
                healthy = client.health()
                return Schema__Registry__Service__Health(
                    service_name = service_name,
                    healthy      = healthy     ,
                    mode         = mode_str
                )
            else:
                return Schema__Registry__Service__Health(
                    service_name = service_name                              ,
                    healthy      = True                                      ,  # Assume healthy if no health method
                    mode         = mode_str                                  ,
                    error        = "Service has no health() method"
                )
        except Exception as e:
            return Schema__Registry__Service__Health(
                service_name = service_name,
                healthy      = False       ,
                mode         = mode_str    ,
                error        = str(e)
            )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Route Setup
    # ═══════════════════════════════════════════════════════════════════════════════

    def setup_routes(self):                                                     # Configure all routes
        self.add_route_get(self.status        )
        self.add_route_get(self.services      )
        self.add_route_get(self.service__get  )
        self.add_route_get(self.health        )
        self.add_route_get(self.health__service)
        return self