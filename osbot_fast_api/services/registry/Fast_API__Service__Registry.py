# ═══════════════════════════════════════════════════════════════════════════════
# Fast_API__Service__Registry
# Central registry for service client discovery across deployment modes
# Enables zero-code-change switching between IN_MEMORY and REMOTE modes
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_fast_api.services.registry.Fast_API__Service__Registry__Client__Base       import Fast_API__Service__Registry__Client__Base
from osbot_fast_api.services.schemas.registry.collections.Dict__Fast_API__Service__Clients_By_Type import Dict__Fast_API__Service__Clients_By_Type
from osbot_fast_api.services.schemas.registry.collections.List__Fast_API__Service__Client_Types   import List__Fast_API__Service__Client_Types
from osbot_utils.type_safe.Type_Safe                                                  import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                        import type_safe


class Fast_API__Service__Registry(Type_Safe):                                          # Instance-based registry for service clients
    clients : Dict__Fast_API__Service__Clients_By_Type                                 # Type_Safe auto-creates this

    @type_safe
    def register(self, client: Fast_API__Service__Registry__Client__Base) -> None:    # Register a client instance
        self.clients[type(client)] = client                                            # Index by actual type

    def client(self, client_type: type) -> Fast_API__Service__Registry__Client__Base: # Retrieve client by type
        if client_type not in self.clients:
            return None                                                                # Not registered = None
        return self.clients[client_type]                                               # Return registered client

    def is_registered(self, client_type: type) -> bool:                                # Check if type is registered
        return client_type in self.clients

    def clear(self) -> None:                                                           # Reset registry for test isolation
        self.clients.clear()

    def registered_types(self) -> List__Fast_API__Service__Client_Types:               # List all registered client types
        return List__Fast_API__Service__Client_Types(list(self.clients.keys()))


fast_api__service__registry = Fast_API__Service__Registry()                            # Singleton instance for convenience
