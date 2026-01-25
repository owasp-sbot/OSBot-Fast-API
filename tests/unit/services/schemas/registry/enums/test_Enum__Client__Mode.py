# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Enum__Client__Mode
# Validates client mode enumeration
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from mgraph_ai_service_cache_client.client.requests.schemas.enums.Enum__Client__Mode import Enum__Client__Mode


class test_Enum__Client__Mode(TestCase):

    def test__values(self):                                                     # Test enum has expected values
        assert Enum__Client__Mode.IN_MEMORY.value == 'in_memory'
        assert Enum__Client__Mode.REMOTE.value    == 'remote'

    def test__members(self):                                                    # Test enum has exactly two members
        members = list(Enum__Client__Mode)
        assert len(members) == 2
        assert Enum__Client__Mode.IN_MEMORY in members
        assert Enum__Client__Mode.REMOTE    in members
