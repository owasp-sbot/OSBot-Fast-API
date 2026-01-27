from unittest                                                                                           import TestCase
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import Fast_API__Service__Registry
from osbot_fast_api.services.schemas.registry.Fast_API__Service__Registry__Client__Config               import Fast_API__Service__Registry__Client__Config
from tests.unit.services.registry.test_Fast_API__Service__Registry                                      import Fake__Html__Service__Client, Fake__Cache__Service__Client, Fake__LLM__Service__Client


# ═══════════════════════════════════════════════════════════════════════════════
# Context Manager Tests - with_registry
# ═══════════════════════════════════════════════════════════════════════════════

class test_Fast_API__Service__Registry__with_registry(TestCase):

    def setUp(self):
        self.registry = Fast_API__Service__Registry()

    def test__with_registry__uses_other_configs(self):                          # Test with_registry swaps configs
        # Setup original registry
        original_config = Fast_API__Service__Registry__Client__Config(base_url = 'https://original.example.com')
        self.registry.register(Fake__Cache__Service__Client, original_config)

        # Setup other registry
        other_registry = Fast_API__Service__Registry()
        other_config   = Fast_API__Service__Registry__Client__Config(base_url = 'https://other.example.com')
        other_registry.register(Fake__Html__Service__Client, other_config)

        with self.registry.with_registry(other_registry):
            # Inside context - uses other registry's configs
            assert self.registry.is_registered(Fake__Cache__Service__Client) is False
            assert self.registry.is_registered(Fake__Html__Service__Client)  is True
            assert self.registry.config(Fake__Html__Service__Client)         is other_config

        # Outside context - original configs restored
        assert self.registry.is_registered(Fake__Cache__Service__Client) is True
        assert self.registry.is_registered(Fake__Html__Service__Client)  is False
        assert self.registry.config(Fake__Cache__Service__Client)        is original_config

    def test__with_registry__restores_on_exception(self):                       # Test restore on exception
        original_config = Fast_API__Service__Registry__Client__Config(base_url = 'https://original.example.com')
        self.registry.register(Fake__Cache__Service__Client, original_config)

        other_registry = Fast_API__Service__Registry()

        try:
            with self.registry.with_registry(other_registry):
                assert self.registry.is_registered(Fake__Cache__Service__Client) is False
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Original configs restored despite exception
        assert self.registry.is_registered(Fake__Cache__Service__Client) is True
        assert self.registry.config(Fake__Cache__Service__Client)        is original_config

    def test__with_registry__yields_self(self):                                 # Test yields registry
        other_registry = Fast_API__Service__Registry()

        with self.registry.with_registry(other_registry) as yielded:
            assert yielded is self.registry

    def test__with_registry__nested(self):                                      # Test nested with_registry
        registry_a = Fast_API__Service__Registry()
        registry_b = Fast_API__Service__Registry()

        config_main = Fast_API__Service__Registry__Client__Config(base_url = 'https://main.example.com')
        config_a    = Fast_API__Service__Registry__Client__Config(base_url = 'https://a.example.com'   )
        config_b    = Fast_API__Service__Registry__Client__Config(base_url = 'https://b.example.com'   )

        self.registry.register(Fake__Cache__Service__Client, config_main)
        registry_a.register(Fake__Html__Service__Client, config_a)
        registry_b.register(Fake__LLM__Service__Client , config_b)

        with self.registry.with_registry(registry_a):
            assert self.registry.is_registered(Fake__Html__Service__Client) is True

            with self.registry.with_registry(registry_b):
                assert self.registry.is_registered(Fake__Html__Service__Client) is False
                assert self.registry.is_registered(Fake__LLM__Service__Client)  is True

            # Back to registry_a
            assert self.registry.is_registered(Fake__Html__Service__Client) is True
            assert self.registry.is_registered(Fake__LLM__Service__Client)  is False

        # Back to original
        assert self.registry.is_registered(Fake__Cache__Service__Client) is True
        assert self.registry.is_registered(Fake__Html__Service__Client)  is False

