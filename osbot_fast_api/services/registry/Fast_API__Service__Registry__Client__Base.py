# ═══════════════════════════════════════════════════════════════════════════════
# Fast_API__Service__Registry__Client__Base
# Abstract base class that all service clients must inherit
# Provides the contract for registration with Fast_API__Service__Registry
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_fast_api.services.schemas.registry.Fast_API__Service__Registry__Client__Config import Fast_API__Service__Registry__Client__Config
from osbot_fast_api.services.schemas.registry.collections.List__Fast_API__Registry__Env_Vars import List__Fast_API__Registry__Env_Vars
from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe


class Fast_API__Service__Registry__Client__Base(Type_Safe):                            # Base class for all service clients
    config : Fast_API__Service__Registry__Client__Config                               # Configuration for this client

    def setup_from_env(self) -> 'Fast_API__Service__Registry__Client__Base':           # Configure from environment variables
        raise NotImplementedError("Subclass must implement setup_from_env()")

    def requests(self):                                                                # Return the *__Requests transport object
        raise NotImplementedError("Subclass must implement requests()")

    def health(self) -> bool:                                                          # Basic health check
        raise NotImplementedError("Subclass must implement health()")

    @classmethod
    def env_vars(cls) -> List__Fast_API__Registry__Env_Vars:                           # Expected env vars for this client
        raise NotImplementedError("Subclass must implement env_vars()")

    @classmethod
    def client_name(cls) -> str:                                                       # Human-readable name for errors
        return cls.__name__
