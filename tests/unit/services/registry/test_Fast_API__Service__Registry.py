# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Fast_API__Service__Registry
# Validates config storage, save/restore, and context managers
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from fastapi                                                                                            import FastAPI
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import Fast_API__Service__Registry
from osbot_fast_api.services.registry.Fast_API__Service__Registry__Client__Base                         import Fast_API__Service__Registry__Client__Base
from osbot_fast_api.services.schemas.registry.Fast_API__Service__Registry__Client__Config               import Fast_API__Service__Registry__Client__Config
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode     import Enum__Fast_API__Service__Registry__Client__Mode
from osbot_fast_api.services.schemas.registry.collections.Dict__Fast_API__Service__Configs_By_Type      import Dict__Fast_API__Service__Configs_By_Type
from osbot_fast_api.services.schemas.registry.collections.List__Fast_API__Service__Configs_Stack        import List__Fast_API__Service__Configs_Stack
from osbot_utils.utils.Objects                                                                          import base_classes
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe


# ═══════════════════════════════════════════════════════════════════════════════
# Fake Clients for Testing
# ═══════════════════════════════════════════════════════════════════════════════

class Fake__Cache__Service__Client(Fast_API__Service__Registry__Client__Base):  # Test double for cache client
    pass


class Fake__Html__Service__Client(Fast_API__Service__Registry__Client__Base):   # Test double for html client
    pass


class Fake__LLM__Service__Client(Fast_API__Service__Registry__Client__Base):    # Test double for LLM client
    pass


# ═══════════════════════════════════════════════════════════════════════════════
# Core Registry Tests
# ═══════════════════════════════════════════════════════════════════════════════

class test_Fast_API__Service__Registry(TestCase):

    def setUp(self):
        self.registry = Fast_API__Service__Registry()

    def test__init__(self):                                                     # Test auto-initialization
        with Fast_API__Service__Registry() as _:
            assert type(_)              is Fast_API__Service__Registry
            assert base_classes(_)      == [Type_Safe, object]
            assert type(_.configs)      is Dict__Fast_API__Service__Configs_By_Type
            assert type(_.configs_stack) is List__Fast_API__Service__Configs_Stack
            assert len(_.configs)       == 0
            assert len(_.configs_stack) == 0

    def test__register__and__config(self):                                      # Test register and retrieve
        config = Fast_API__Service__Registry__Client__Config(mode     = Enum__Fast_API__Service__Registry__Client__Mode.REMOTE,
                                                             base_url = 'https://example.com'                                 )

        self.registry.register(Fake__Cache__Service__Client, config)

        retrieved = self.registry.config(Fake__Cache__Service__Client)
        assert retrieved               is config
        assert retrieved.mode          == Enum__Fast_API__Service__Registry__Client__Mode.REMOTE
        assert str(retrieved.base_url) == 'https://example.com'

    def test__config__not_registered__returns_none(self):                       # Test unregistered lookup
        result = self.registry.config(Fake__Cache__Service__Client)
        assert result is None

    def test__is_registered__false_when_not_registered(self):                   # Test registration check (false)
        assert self.registry.is_registered(Fake__Cache__Service__Client) is False

    def test__is_registered__true_when_registered(self):                        # Test registration check (true)
        config = Fast_API__Service__Registry__Client__Config()
        self.registry.register(Fake__Cache__Service__Client, config)

        assert self.registry.is_registered(Fake__Cache__Service__Client) is True

    def test__clear__resets_configs(self):                                      # Test clearing configs
        config = Fast_API__Service__Registry__Client__Config()
        self.registry.register(Fake__Cache__Service__Client, config)
        assert self.registry.is_registered(Fake__Cache__Service__Client) is True

        self.registry.clear()

        assert len(self.registry.configs) == 0
        assert self.registry.is_registered(Fake__Cache__Service__Client) is False

    def test__clear__does_not_affect_stack(self):                               # Test clear doesn't touch stack
        config = Fast_API__Service__Registry__Client__Config()
        self.registry.register(Fake__Cache__Service__Client, config)
        self.registry.configs__save()
        assert self.registry.configs__stack_size() == 1

        self.registry.clear()

        assert len(self.registry.configs)          == 0
        assert self.registry.configs__stack_size() == 1                         # Stack unchanged

    def test__multiple_clients__different_configs(self):                        # Test multiple client types
        config_cache = Fast_API__Service__Registry__Client__Config(mode     = Enum__Fast_API__Service__Registry__Client__Mode.REMOTE,
                                                                   base_url = 'https://cache.example.com'                           )
        config_html  = Fast_API__Service__Registry__Client__Config(mode     = Enum__Fast_API__Service__Registry__Client__Mode.REMOTE,
                                                                   base_url = 'https://html.example.com'                            )

        self.registry.register(Fake__Cache__Service__Client, config_cache)
        self.registry.register(Fake__Html__Service__Client , config_html )

        assert self.registry.config(Fake__Cache__Service__Client) is config_cache
        assert self.registry.config(Fake__Html__Service__Client)  is config_html

    def test__register__overwrites_existing(self):                              # Test re-registration overwrites
        config_1 = Fast_API__Service__Registry__Client__Config(base_url = 'https://old.example.com')
        config_2 = Fast_API__Service__Registry__Client__Config(base_url = 'https://new.example.com')

        self.registry.register(Fake__Cache__Service__Client, config_1)
        self.registry.register(Fake__Cache__Service__Client, config_2)

        assert self.registry.config(Fake__Cache__Service__Client) is config_2

    def test__in_memory_config(self):                                           # Test IN_MEMORY mode config
        app    = FastAPI()
        config = Fast_API__Service__Registry__Client__Config(mode         = Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY,
                                                             fast_api_app = app                                                      )

        self.registry.register(Fake__Cache__Service__Client, config)

        retrieved = self.registry.config(Fake__Cache__Service__Client)
        assert retrieved.mode         == Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY
        assert retrieved.fast_api_app is app
