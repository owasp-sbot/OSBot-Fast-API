from unittest                                                                                           import TestCase
from fastapi                                                                                            import FastAPI
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import Fast_API__Service__Registry
from osbot_fast_api.services.schemas.registry.Fast_API__Service__Registry__Client__Config               import Fast_API__Service__Registry__Client__Config
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode     import Enum__Fast_API__Service__Registry__Client__Mode
from tests.unit.services.registry.test_Fast_API__Service__Registry import Fake__Cache__Service__Client, Fake__Html__Service__Client


# ═══════════════════════════════════════════════════════════════════════════════
# Real-World Usage Pattern Tests
# ═══════════════════════════════════════════════════════════════════════════════

class test_Fast_API__Service__Registry__usage_patterns(TestCase):

    def test__setup_teardown_pattern(self):                                     # Test setUp/tearDown pattern
        from osbot_fast_api.services.registry.Fast_API__Service__Registry import fast_api__service__registry

        # Simulate setUpClass
        fast_api__service__registry.configs__save()
        fast_api__service__registry.clear()

        test_config = Fast_API__Service__Registry__Client__Config(
            mode     = Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY,
            fast_api_app = FastAPI()
        )
        fast_api__service__registry.register(Fake__Cache__Service__Client, test_config)

        # Test can use the registered config
        assert fast_api__service__registry.is_registered(Fake__Cache__Service__Client) is True

        # Simulate tearDownClass
        fast_api__service__registry.configs__restore()

    def test__hot_swap_to_in_memory(self):                                      # Test hot-swap for debugging
        registry = Fast_API__Service__Registry()

        # Production config
        prod_config = Fast_API__Service__Registry__Client__Config(
            mode     = Enum__Fast_API__Service__Registry__Client__Mode.REMOTE,
            base_url = 'https://prod.example.com'
        )
        registry.register(Fake__Cache__Service__Client, prod_config)

        # Hot-swap to IN_MEMORY for debugging
        debug_config = Fast_API__Service__Registry__Client__Config(
            mode         = Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY,
            fast_api_app = FastAPI()
        )

        with registry.with_config(Fake__Cache__Service__Client, debug_config):
            config = registry.config(Fake__Cache__Service__Client)
            assert config.mode == Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY

        # Back to production
        config = registry.config(Fake__Cache__Service__Client)
        assert config.mode == Enum__Fast_API__Service__Registry__Client__Mode.REMOTE

    def test__test_isolation_with_different_registries(self):                   # Test isolation between test classes
        from osbot_fast_api.services.registry.Fast_API__Service__Registry import fast_api__service__registry

        # Test class A sets up its own registry
        test_registry_a = Fast_API__Service__Registry()
        test_registry_a.register(Fake__Cache__Service__Client,
                                 Fast_API__Service__Registry__Client__Config(base_url='https://test-a.example.com'))

        # Test class B sets up its own registry
        test_registry_b = Fast_API__Service__Registry()
        test_registry_b.register(Fake__Html__Service__Client,
                                 Fast_API__Service__Registry__Client__Config(base_url='https://test-b.example.com'))

        # Each test class uses with_registry for isolation
        with fast_api__service__registry.with_registry(test_registry_a):
            assert fast_api__service__registry.is_registered(Fake__Cache__Service__Client) is True
            assert fast_api__service__registry.is_registered(Fake__Html__Service__Client)  is False

        with fast_api__service__registry.with_registry(test_registry_b):
            assert fast_api__service__registry.is_registered(Fake__Cache__Service__Client) is False
            assert fast_api__service__registry.is_registered(Fake__Html__Service__Client)  is True