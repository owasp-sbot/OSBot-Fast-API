# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Fast_API__Service__Registry__Client__Base
# Validates base client class and its required methods
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                  import TestCase
from osbot_fast_api.services.registry.Fast_API__Service__Registry__Client__Base                import Fast_API__Service__Registry__Client__Base
from osbot_fast_api.services.schemas.registry.Fast_API__Service__Registry__Client__Config      import Fast_API__Service__Registry__Client__Config
from osbot_utils.utils.Objects                                                                 import base_classes
from osbot_utils.type_safe.Type_Safe                                                           import Type_Safe


class test_Fast_API__Service__Registry__Client__Base(TestCase):

    def test__init__(self):                                                        # Test auto-initialization
        with Fast_API__Service__Registry__Client__Base() as _:
            assert type(_)         is Fast_API__Service__Registry__Client__Base
            assert base_classes(_) == [Type_Safe, object]
            assert type(_.config)  is Fast_API__Service__Registry__Client__Config

    def test__setup_from_env__raises_not_implemented(self):                        # Test abstract method
        with Fast_API__Service__Registry__Client__Base() as _:
            with self.assertRaises(NotImplementedError) as context:
                _.setup_from_env()
            assert "Subclass must implement setup_from_env()" in str(context.exception)

    def test__requests__raises_not_implemented(self):                              # Test abstract method
        with Fast_API__Service__Registry__Client__Base() as _:
            with self.assertRaises(NotImplementedError) as context:
                _.requests()
            assert "Subclass must implement requests()" in str(context.exception)

    def test__health__raises_not_implemented(self):                                # Test abstract method
        with Fast_API__Service__Registry__Client__Base() as _:
            with self.assertRaises(NotImplementedError) as context:
                _.health()
            assert "Subclass must implement health()" in str(context.exception)

    def test__env_vars__raises_not_implemented(self):                              # Test abstract class method
        with self.assertRaises(NotImplementedError) as context:
            Fast_API__Service__Registry__Client__Base.env_vars()
        assert "Subclass must implement env_vars()" in str(context.exception)

    def test__client_name__returns_class_name(self):                               # Test default client name
        assert Fast_API__Service__Registry__Client__Base.client_name() == 'Fast_API__Service__Registry__Client__Base'
