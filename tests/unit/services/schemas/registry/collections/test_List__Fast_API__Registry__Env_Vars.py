from unittest                                                                                      import TestCase
from osbot_utils.utils.Objects                                                                     import base_classes
from osbot_fast_api.services.schemas.registry.Schema__Fast_API__Registry__Env_Var                  import Schema__Fast_API__Registry__Env_Var
from osbot_fast_api.services.schemas.registry.collections.List__Fast_API__Registry__Env_Vars       import List__Fast_API__Registry__Env_Vars
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List                              import Type_Safe__List



class test_List__Fast_API__Registry__Env_Vars(TestCase):

    def test__init__(self):                                                        # Test auto-initialization
        with List__Fast_API__Registry__Env_Vars() as _:
            assert type(_)              is List__Fast_API__Registry__Env_Vars
            assert Type_Safe__List      in base_classes(_)                         # Inherits from Type_Safe__List
            assert len(_)               == 0

    def test__append_valid_item(self):                                             # Test appending valid items
        env_vars = List__Fast_API__Registry__Env_Vars()
        env_var  = Schema__Fast_API__Registry__Env_Var(name='TEST_VAR', required=True)

        env_vars.append(env_var)

        assert len(env_vars)   == 1
        assert env_vars[0]     is env_var

    def test__init_with_list(self):                                                # Test initialization with list
        env_vars = List__Fast_API__Registry__Env_Vars([Schema__Fast_API__Registry__Env_Var(name='VAR_1', required=True ),
                                                        Schema__Fast_API__Registry__Env_Var(name='VAR_2', required=False)])

        assert len(env_vars)            == 2
        assert str(env_vars[0].name)    == 'VAR_1'
        assert str(env_vars[1].name)    == 'VAR_2'
        assert env_vars[0].required     is True
        assert env_vars[1].required     is False
