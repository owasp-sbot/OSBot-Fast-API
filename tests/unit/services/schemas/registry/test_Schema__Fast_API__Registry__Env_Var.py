# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Schema__Fast_API__Registry__Env_Var
# Validates environment variable schema
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                              import TestCase
from osbot_fast_api.services.schemas.registry.Schema__Fast_API__Registry__Env_Var          import Schema__Fast_API__Registry__Env_Var
from osbot_fast_api.services.schemas.registry.safe_str.Safe_Str__Env_Var__Name             import Safe_Str__Env_Var__Name
from osbot_utils.utils.Objects                                                             import base_classes
from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe


class test_Schema__Fast_API__Registry__Env_Var(TestCase):

    def test__init__(self):                                                        # Test auto-initialization
        with Schema__Fast_API__Registry__Env_Var() as _:
            assert type(_)          is Schema__Fast_API__Registry__Env_Var
            assert base_classes(_)  == [Type_Safe, object]
            assert type(_.name)     is Safe_Str__Env_Var__Name                     # Uses new type-safe env var name
            assert _.required       is True                                        # Default value

    def test__with_values(self):                                                   # Test with explicit values
        env_var = Schema__Fast_API__Registry__Env_Var(name     = 'URL__TARGET_SERVER__CACHE',
                                                       required = True                        )

        assert str(env_var.name) == 'URL__TARGET_SERVER__CACHE'
        assert env_var.required  is True

    def test__optional_env_var(self):                                              # Test optional env var
        env_var = Schema__Fast_API__Registry__Env_Var(name     = 'API_KEY__OPTIONAL',
                                                       required = False               )

        assert str(env_var.name) == 'API_KEY__OPTIONAL'
        assert env_var.required  is False
