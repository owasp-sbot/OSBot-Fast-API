from osbot_fast_api.services.registry.Fast_API__Service__Registry__Client__Base        import Fast_API__Service__Registry__Client__Base
from osbot_fast_api.services.schemas.registry.collections.List__Fast_API__Registry__Env_Vars import List__Fast_API__Registry__Env_Vars


class Fake__Client__Alpha(Fast_API__Service__Registry__Client__Base):                 # Test double for first client type

    def setup_from_env(self) -> 'Fake__Client__Alpha':
        return self

    def requests(self):
        return None

    def health(self) -> bool:
        return True

    @classmethod
    def env_vars(cls) -> List__Fast_API__Registry__Env_Vars:
        return List__Fast_API__Registry__Env_Vars()

    @classmethod
    def client_name(cls) -> str:
        return 'Fake__Client__Alpha'
