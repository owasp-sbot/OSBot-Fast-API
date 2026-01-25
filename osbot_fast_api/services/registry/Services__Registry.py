# ═══════════════════════════════════════════════════════════════════════════════
# Services__Registry
# Central registry for service client discovery across deployment modes
# Enables zero-code-change switching between IN_MEMORY and REMOTE modes
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_fast_api.services.registry.Service__Client__Base import Service__Client__Base
from osbot_fast_api.services.schemas.registry.collections.Dict__Clients__By_Type import Dict__Clients__By_Type
from osbot_fast_api.services.schemas.registry.collections.List__Client_Types import List__Client_Types
from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe


# todo: rename this class to Fast_API__Service__Registry
#       this class needs to be refactored to not use static methods where _clients is an instance variable
#       and the main static reference for the shared (singleton method) is retrieve by the "fast_api__service_registry = Services__Registry() " that can be seen at the end of this file
#       this means that we can make the Services__Registry a Type_Safe class and remove the None assigment, since Type_Safe will then create that _clients object
#       rename '_clients' with 'clients
class Services__Registry:                                                       # Static singleton registry for service clients
    _clients : Dict__Clients__By_Type = None                                   # Class-level storage (lazy initialized)

    @classmethod
    def clients(cls) -> Dict__Clients__By_Type:                                 # Lazy initialization of storage
        if cls._clients is None:
            cls._clients = Dict__Clients__By_Type()
        return cls._clients

    @classmethod
    @type_safe
    def register(cls, client: Service__Client__Base) -> None:                   # Register a client instance
        cls.clients()[type(client)] = client                                    # Index by actual type

    @classmethod
    def client(cls, client_type: type) -> Service__Client__Base:                # Retrieve client by type
        if client_type not in cls.clients():
            return None                                                         # Not registered = None
        return cls.clients()[client_type]                                       # Return registered client

    @classmethod
    def is_registered(cls, client_type: type) -> bool:                          # Check if type is registered
        return client_type in cls.clients()

    @classmethod
    def clear(cls) -> None:                                                     # Reset registry for test isolation
        cls._clients = None

    @classmethod
    def registered_types(cls) -> List__Client_Types:                            # List all registered client types
        return List__Client_Types(list(cls.clients().keys()))

fast_api__service_registry = Services__Registry()