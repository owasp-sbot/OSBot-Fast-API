# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Enum__Fast_API__Service__Registry__Client__Mode
# Validates client mode enumeration
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                       import TestCase
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode import Enum__Fast_API__Service__Registry__Client__Mode


class test_Enum__Fast_API__Service__Registry__Client__Mode(TestCase):

    def test__values(self):                                                     # Test enum has expected values
        assert Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY.value == 'in_memory'
        assert Enum__Fast_API__Service__Registry__Client__Mode.REMOTE.value    == 'remote'

    def test__members(self):                                                    # Test enum has exactly two members
        members = list(Enum__Fast_API__Service__Registry__Client__Mode)
        assert len(members) == 2
        assert Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY in members
        assert Enum__Fast_API__Service__Registry__Client__Mode.REMOTE    in members
