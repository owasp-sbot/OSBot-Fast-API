# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Service__Client__Base
# Validates base client class and its required methods
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from osbot_fast_api.services.registry.Service__Client__Base                     import Service__Client__Base
from osbot_fast_api.services.schemas.registry.Schema__Service__Client__Config   import Schema__Service__Client__Config
from osbot_utils.utils.Objects                                                  import base_classes
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe


class test_Service__Client__Base(TestCase):

    def test__init__(self):                                                     # Test auto-initialization
        with Service__Client__Base() as _:
            assert type(_)         is Service__Client__Base
            assert base_classes(_) == [Type_Safe, object]
            assert type(_.config)  is Schema__Service__Client__Config

    def test__setup_from_env__raises_not_implemented(self):                     # Test abstract method
        with Service__Client__Base() as _:
            with self.assertRaises(NotImplementedError) as context:
                _.setup_from_env()
            assert "Subclass must implement setup_from_env()" in str(context.exception)

    def test__requests__raises_not_implemented(self):                           # Test abstract method
        with Service__Client__Base() as _:
            with self.assertRaises(NotImplementedError) as context:
                _.requests()
            assert "Subclass must implement requests()" in str(context.exception)

    def test__health__raises_not_implemented(self):                             # Test abstract method
        with Service__Client__Base() as _:
            with self.assertRaises(NotImplementedError) as context:
                _.health()
            assert "Subclass must implement health()" in str(context.exception)

    def test__env_vars__raises_not_implemented(self):                           # Test abstract class method
        with self.assertRaises(NotImplementedError) as context:
            Service__Client__Base.env_vars()
        assert "Subclass must implement env_vars()" in str(context.exception)

    def test__client_name__returns_class_name(self):                            # Test default client name
        assert Service__Client__Base.client_name() == 'Service__Client__Base'
