from osbot_fast_api.services.registry.Service__Client__Base              import Service__Client__Base
from osbot_fast_api.services.schemas.registry.collections.List__Env_Vars import List__Env_Vars


class Mock__Client__Alpha(Service__Client__Base):                               # Test double for first client type

    def setup_from_env(self) -> 'Mock__Client__Alpha':
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
        return 'Mock__Client__Alpha'