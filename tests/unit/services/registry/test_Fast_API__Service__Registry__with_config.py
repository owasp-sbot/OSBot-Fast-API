from unittest                                                                                           import TestCase
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import Fast_API__Service__Registry
from osbot_fast_api.services.schemas.registry.Fast_API__Service__Registry__Client__Config               import Fast_API__Service__Registry__Client__Config
from tests.unit.services.registry.test_Fast_API__Service__Registry import Fake__Cache__Service__Client, Fake__Html__Service__Client


# ═══════════════════════════════════════════════════════════════════════════════
# Context Manager Tests - with_config
# ═══════════════════════════════════════════════════════════════════════════════

class test_Fast_API__Service__Registry__with_config(TestCase):

    def setUp(self):
        self.registry = Fast_API__Service__Registry()

    def test__with_config__overrides_single_client(self):                       # Test with_config overrides one
        original_config = Fast_API__Service__Registry__Client__Config(base_url = 'https://original.example.com')
        override_config = Fast_API__Service__Registry__Client__Config(base_url = 'https://override.example.com')

        self.registry.register(Fake__Cache__Service__Client, original_config)

        with self.registry.with_config(Fake__Cache__Service__Client, override_config):
            assert self.registry.config(Fake__Cache__Service__Client) is override_config

        assert self.registry.config(Fake__Cache__Service__Client) is original_config

    def test__with_config__preserves_other_clients(self):                       # Test other clients unchanged
        cache_config = Fast_API__Service__Registry__Client__Config(base_url = 'https://cache.example.com'   )
        html_config  = Fast_API__Service__Registry__Client__Config(base_url = 'https://html.example.com'    )
        new_cache    = Fast_API__Service__Registry__Client__Config(base_url = 'https://new-cache.example.com')

        self.registry.register(Fake__Cache__Service__Client, cache_config)
        self.registry.register(Fake__Html__Service__Client , html_config )


        # confirm they are there before
        assert self.registry.config(Fake__Cache__Service__Client) is cache_config
        assert self.registry.config(Fake__Html__Service__Client)  is html_config

        with self.registry.with_config(Fake__Cache__Service__Client, new_cache):

            assert self.registry.config(Fake__Cache__Service__Client) is new_cache          # Cache changed
            assert self.registry.config(Fake__Html__Service__Client ) is html_config        # Html unchanged

        # Both restored
        assert self.registry.config(Fake__Cache__Service__Client) is cache_config
        assert self.registry.config(Fake__Html__Service__Client)  is html_config

    def test__with_config__adds_new_client(self):                               # Test adding new client temporarily
        new_config = Fast_API__Service__Registry__Client__Config(base_url = 'https://new.example.com')

        assert self.registry.is_registered(Fake__Cache__Service__Client) is False

        with self.registry.with_config(Fake__Cache__Service__Client, new_config):
            assert self.registry.is_registered(Fake__Cache__Service__Client) is True
            assert self.registry.config(Fake__Cache__Service__Client)        is new_config

        assert self.registry.is_registered(Fake__Cache__Service__Client) is False

    def test__with_config__restores_on_exception(self):                         # Test restore on exception
        original_config = Fast_API__Service__Registry__Client__Config(base_url = 'https://original.example.com')
        override_config = Fast_API__Service__Registry__Client__Config(base_url = 'https://override.example.com')

        self.registry.register(Fake__Cache__Service__Client, original_config)

        try:
            with self.registry.with_config(Fake__Cache__Service__Client, override_config):
                assert self.registry.config(Fake__Cache__Service__Client) is override_config
                raise ValueError("Test exception")
        except ValueError:
            pass

        assert self.registry.config(Fake__Cache__Service__Client) is original_config

    def test__with_config__yields_self(self):                                   # Test yields registry
        config = Fast_API__Service__Registry__Client__Config()

        with self.registry.with_config(Fake__Cache__Service__Client, config) as yielded:
            assert yielded is self.registry
