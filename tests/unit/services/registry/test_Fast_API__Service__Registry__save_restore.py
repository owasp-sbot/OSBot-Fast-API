from unittest                                                                                           import TestCase
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import Fast_API__Service__Registry
from osbot_fast_api.services.schemas.registry.Fast_API__Service__Registry__Client__Config               import Fast_API__Service__Registry__Client__Config
from tests.unit.services.registry.test_Fast_API__Service__Registry                                      import Fake__Cache__Service__Client


# ═══════════════════════════════════════════════════════════════════════════════
# Save / Restore Tests
# ═══════════════════════════════════════════════════════════════════════════════

class test_Fast_API__Service__Registry__save_restore(TestCase):

    def setUp(self):
        self.registry = Fast_API__Service__Registry()

    def test__configs__save__adds_to_stack(self):                               # Test save adds to stack
        assert self.registry.configs__stack_size() == 0

        self.registry.configs__save()

        assert self.registry.configs__stack_size() == 1

    def test__configs__save__captures_current_configs(self):                    # Test save captures configs
        config = Fast_API__Service__Registry__Client__Config(base_url = 'https://saved.example.com')
        self.registry.register(Fake__Cache__Service__Client, config)

        self.registry.configs__save()

        # Verify stack has the config
        assert self.registry.configs__stack_size()            == 1
        assert Fake__Cache__Service__Client in self.registry.configs_stack[0]

    def test__configs__restore__pops_from_stack(self):                          # Test restore pops from stack
        self.registry.configs__save()
        assert self.registry.configs__stack_size() == 1

        self.registry.configs__restore()

        assert self.registry.configs__stack_size() == 0

    def test__configs__restore__restores_configs(self):                         # Test restore brings back configs
        config = Fast_API__Service__Registry__Client__Config(base_url = 'https://original.example.com')
        self.registry.register(Fake__Cache__Service__Client, config)
        self.registry.configs__save()

        # Modify configs
        self.registry.clear()
        assert self.registry.is_registered(Fake__Cache__Service__Client) is False

        self.registry.configs__restore()

        # Original config is back
        assert self.registry.is_registered(Fake__Cache__Service__Client) is True
        assert self.registry.config(Fake__Cache__Service__Client) is config

    def test__configs__restore__on_empty_stack__does_nothing(self):             # Test restore on empty stack
        self.registry.configs__restore()                                        # Should not raise
        assert self.registry.configs__stack_size() == 0

    def test__configs__save_restore__multiple_levels(self):                     # Test nested save/restore
        config_1 = Fast_API__Service__Registry__Client__Config(base_url = 'https://level1.example.com')
        config_2 = Fast_API__Service__Registry__Client__Config(base_url = 'https://level2.example.com')

        # Level 1
        self.registry.register(Fake__Cache__Service__Client, config_1)
        self.registry.configs__save()

        # Level 2
        self.registry.register(Fake__Cache__Service__Client, config_2)
        self.registry.configs__save()

        # Level 3 - clear
        self.registry.clear()

        assert self.registry.configs__stack_size() == 2
        assert self.registry.is_registered(Fake__Cache__Service__Client) is False

        # Restore to level 2
        self.registry.configs__restore()
        assert self.registry.config(Fake__Cache__Service__Client) is config_2

        # Restore to level 1
        self.registry.configs__restore()
        assert self.registry.config(Fake__Cache__Service__Client) is config_1

    def test__configs__stack_size(self):                                        # Test stack size tracking
        assert self.registry.configs__stack_size() == 0

        self.registry.configs__save()
        assert self.registry.configs__stack_size() == 1

        self.registry.configs__save()
        assert self.registry.configs__stack_size() == 2

        self.registry.configs__restore()
        assert self.registry.configs__stack_size() == 1
