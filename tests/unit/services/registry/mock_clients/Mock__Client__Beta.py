from osbot_fast_api.services.registry.Service__Client__Base import Service__Client__Base
from osbot_fast_api.services.schemas.registry.collections.List__Env_Vars import List__Env_Vars


# ═══════════════════════════════════════════════════════════════════════════════
# Test Double: Real implementation of Service__Client__Base for testing
# ═══════════════════════════════════════════════════════════════════════════════


# todo: see if we can find a better name than Mock__* for these test doubles
#       I don't like the implications and baggage that the 'mock' word has

class Mock__Client__Beta(Service__Client__Base):                                # Test double for second client type

    def setup_from_env(self) -> 'Mock__Client__Beta':
        return self

    def requests(self):
        return None

    def health(self) -> bool:
        return True

    @classmethod
    def env_vars(cls) -> List__Env_Vars:
        return List__Env_Vars()

    @classmethod
    def client_name(cls) -> str:
        return 'Mock__Client__Beta'