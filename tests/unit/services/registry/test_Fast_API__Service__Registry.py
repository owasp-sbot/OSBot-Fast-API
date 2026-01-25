# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Fast_API__Service__Registry
# Validates service client registration and discovery
# No mocks - uses real test double implementations
# ═══════════════════════════════════════════════════════════════════════════════
import re
import pytest
from unittest                                                                                          import TestCase
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                      import Fast_API__Service__Registry
from osbot_fast_api.services.schemas.registry.collections.Dict__Fast_API__Service__Clients_By_Type     import Dict__Fast_API__Service__Clients_By_Type
from osbot_fast_api.services.schemas.registry.collections.List__Fast_API__Service__Client_Types        import List__Fast_API__Service__Client_Types
from tests.unit.services.registry.test_clients.Fake__Client__Alpha                                     import Fake__Client__Alpha
from tests.unit.services.registry.test_clients.Fake__Client__Beta                                      import Fake__Client__Beta


# ═══════════════════════════════════════════════════════════════════════════════
# Fast_API__Service__Registry Tests
# ═══════════════════════════════════════════════════════════════════════════════

class test_Fast_API__Service__Registry(TestCase):

    def setUp(self):                                                               # Isolate each test
        self.registry = Fast_API__Service__Registry()

    def test__clients__auto_initialized(self):                                     # Test Type_Safe auto-initialization
        with Fast_API__Service__Registry() as _:
            assert type(_.clients) is Dict__Fast_API__Service__Clients_By_Type     # Type_Safe creates it
            assert len(_.clients)  == 0                                            # Starts empty

    def test__register__valid_client(self):                                        # Test registering a valid client
        with Fast_API__Service__Registry() as _:
            client = Fake__Client__Alpha()

            _.register(client)

            assert _.is_registered(Fake__Client__Alpha) is True
            assert _.client(Fake__Client__Alpha)        is client

    def test__register__none__raises_value_error(self):                            # Test None rejection
        with Fast_API__Service__Registry() as _:
            error_message = "Parameter 'client' is not optional but got None"
            with pytest.raises(ValueError, match=re.escape(error_message)):
                _.register(None)

    def test__register__invalid_type__raises_type_error(self):                     # Test non-client rejection
        with Fast_API__Service__Registry() as _:
            error_message = "Parameter 'client' expected type <class 'osbot_fast_api.services.registry.Fast_API__Service__Registry__Client__Base.Fast_API__Service__Registry__Client__Base'>, but got <class 'str'>"
            with pytest.raises(ValueError, match=re.escape(error_message)):
                _.register("not a client")

    def test__client__not_registered__returns_none(self):                          # Test unregistered client lookup
        with Fast_API__Service__Registry() as _:
            result = _.client(Fake__Client__Alpha)
            assert result is None

    def test__client__registered__returns_client(self):                            # Test registered client lookup
        with Fast_API__Service__Registry() as _:
            client = Fake__Client__Alpha()
            _.register(client)

            result = _.client(Fake__Client__Alpha)

            assert result is client

    def test__is_registered__false_when_not_registered(self):                      # Test registration check (false)
        with Fast_API__Service__Registry() as _:
            assert _.is_registered(Fake__Client__Alpha) is False

    def test__is_registered__true_when_registered(self):                           # Test registration check (true)
        with Fast_API__Service__Registry() as _:
            client = Fake__Client__Alpha()
            _.register(client)

            assert _.is_registered(Fake__Client__Alpha) is True

    def test__clear__resets_registry(self):                                        # Test clearing the registry
        with Fast_API__Service__Registry() as _:
            client = Fake__Client__Alpha()
            _.register(client)
            assert _.is_registered(Fake__Client__Alpha) is True

            _.clear()

            assert len(_.clients)                       == 0                       # Clients dict is empty
            assert _.is_registered(Fake__Client__Alpha) is False

    def test__registered_types__returns_all_types(self):                           # Test listing registered types
        with Fast_API__Service__Registry() as _:
            client_alpha = Fake__Client__Alpha()
            client_beta  = Fake__Client__Beta()
            _.register(client_alpha)
            _.register(client_beta)

            types = _.registered_types()

            assert type(types)           is List__Fast_API__Service__Client_Types
            assert len(types)            == 2
            assert Fake__Client__Alpha   in types
            assert Fake__Client__Beta    in types

    def test__registered_types__empty_when_none_registered(self):                  # Test empty registry
        with Fast_API__Service__Registry() as _:
            types = _.registered_types()

            assert type(types) is List__Fast_API__Service__Client_Types
            assert len(types)  == 0

    def test__multiple_clients__different_types(self):                             # Test multiple client types
        with Fast_API__Service__Registry() as _:
            client_alpha = Fake__Client__Alpha()
            client_beta  = Fake__Client__Beta()

            _.register(client_alpha)
            _.register(client_beta)

            assert _.client(Fake__Client__Alpha) is client_alpha
            assert _.client(Fake__Client__Beta)  is client_beta

    def test__register__overwrites_existing(self):                                 # Test re-registration overwrites
        with Fast_API__Service__Registry() as _:
            client_1 = Fake__Client__Alpha()
            client_2 = Fake__Client__Alpha()
            _.register(client_1)

            _.register(client_2)                                                   # Register second instance

            assert _.client(Fake__Client__Alpha) is client_2                       # Last one wins
            assert _.client(Fake__Client__Alpha) is not client_1


# todo: add a new set of integration tests that actually simulates a FastAPI environment
#       and tests that check that the in memory mode and remote works as expected (leverage OSBot_Utils Temp_Web_Server)
