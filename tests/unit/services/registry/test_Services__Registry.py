# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Services__Registry
# Validates service client registration and discovery
# No mocks - uses real test double implementations
# ═══════════════════════════════════════════════════════════════════════════════
import re
import pytest
from unittest                                                                       import TestCase
from osbot_fast_api.services.registry.Services__Registry                            import Services__Registry
from osbot_fast_api.services.schemas.registry.collections.Dict__Clients__By_Type    import Dict__Clients__By_Type
from osbot_fast_api.services.schemas.registry.collections.List__Client_Types        import List__Client_Types
from tests.unit.services.registry.mock_clients.Mock__Client__Alpha                  import Mock__Client__Alpha
from tests.unit.services.registry.mock_clients.Mock__Client__Beta                   import Mock__Client__Beta


# ═══════════════════════════════════════════════════════════════════════════════
# Services__Registry Tests
# ═══════════════════════════════════════════════════════════════════════════════

class test_Services__Registry(TestCase):

    def setUp(self):                                                            # Isolate each test
        Services__Registry.clear()

    def tearDown(self):                                                         # Cleanup after each test
        Services__Registry.clear()

    def test__clients__lazy_init(self):                                         # Test lazy initialization
        assert Services__Registry._clients is None                              # Not yet initialized
        clients = Services__Registry.clients()
        assert type(clients)               is Dict__Clients__By_Type
        assert Services__Registry._clients is clients                           # Now initialized

    def test__register__valid_client(self):                                     # Test registering a valid client
        client = Mock__Client__Alpha()

        Services__Registry.register(client)

        assert Services__Registry.is_registered(Mock__Client__Alpha) is True
        assert Services__Registry.client(Mock__Client__Alpha)        is client

    def test__register__none__raises_value_error(self):                         # Test None rejection
        error_message = "Parameter 'client' is not optional but got None"
        with pytest.raises(ValueError, match=re.escape(error_message)):
            Services__Registry.register(None)

    def test__register__invalid_type__raises_type_error(self):                  # Test non-client rejection
        error_message = "Parameter 'client' expected type <class 'osbot_fast_api.services.registry.Service__Client__Base.Service__Client__Base'>, but got <class 'str'>"
        with pytest.raises(ValueError, match=re.escape(error_message)):
            Services__Registry.register("not a client")

    def test__client__not_registered__returns_none(self):                       # Test unregistered client lookup
        result = Services__Registry.client(Mock__Client__Alpha)
        assert result is None

    def test__client__registered__returns_client(self):                         # Test registered client lookup
        client = Mock__Client__Alpha()
        Services__Registry.register(client)

        result = Services__Registry.client(Mock__Client__Alpha)

        assert result is client

    def test__is_registered__false_when_not_registered(self):                   # Test registration check (false)
        assert Services__Registry.is_registered(Mock__Client__Alpha) is False

    def test__is_registered__true_when_registered(self):                        # Test registration check (true)
        client = Mock__Client__Alpha()
        Services__Registry.register(client)

        assert Services__Registry.is_registered(Mock__Client__Alpha) is True

    def test__clear__resets_registry(self):                                     # Test clearing the registry
        client = Mock__Client__Alpha()
        Services__Registry.register(client)
        assert Services__Registry.is_registered(Mock__Client__Alpha) is True

        Services__Registry.clear()

        assert Services__Registry._clients                           is None
        assert Services__Registry.is_registered(Mock__Client__Alpha) is False

    def test__registered_types__returns_all_types(self):                        # Test listing registered types
        client_alpha = Mock__Client__Alpha()
        client_beta  = Mock__Client__Beta()
        Services__Registry.register(client_alpha)
        Services__Registry.register(client_beta)

        types = Services__Registry.registered_types()

        assert type(types)            is List__Client_Types
        assert len(types)             == 2
        assert Mock__Client__Alpha    in types
        assert Mock__Client__Beta     in types

    def test__registered_types__empty_when_none_registered(self):               # Test empty registry
        types = Services__Registry.registered_types()

        assert type(types) is List__Client_Types
        assert len(types)  == 0

    def test__multiple_clients__different_types(self):                          # Test multiple client types
        client_alpha = Mock__Client__Alpha()
        client_beta  = Mock__Client__Beta()

        Services__Registry.register(client_alpha)
        Services__Registry.register(client_beta)

        assert Services__Registry.client(Mock__Client__Alpha) is client_alpha
        assert Services__Registry.client(Mock__Client__Beta)  is client_beta

    def test__register__overwrites_existing(self):                              # Test re-registration overwrites
        client_1 = Mock__Client__Alpha()
        client_2 = Mock__Client__Alpha()
        Services__Registry.register(client_1)

        Services__Registry.register(client_2)                                   # Register second instance

        assert Services__Registry.client(Mock__Client__Alpha) is client_2       # Last one wins
        assert Services__Registry.client(Mock__Client__Alpha) is not client_1


# todo: add a new set of integration tests (here and for each of the Mock_Client*_) that actually simulates a Fast_API environment
#       and tests that check that the in memory mode and remote works as expected (leverage OSBot_Utils Temp_Web_Server)