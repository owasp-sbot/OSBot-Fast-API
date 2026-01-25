# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Schema__Service__Client__Config
# Validates client configuration schema
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                        import TestCase
from fastapi                                                                         import FastAPI
from mgraph_ai_service_cache_client.client.requests.schemas.enums.Enum__Client__Mode import Enum__Client__Mode
from osbot_fast_api.services.schemas.registry.Schema__Service__Client__Config        import Schema__Service__Client__Config
from osbot_utils.utils.Objects                                                       import base_classes
from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe


class test_Schema__Service__Client__Config(TestCase):

    def test__init__(self):                                                     # Test auto-initialization
        with Schema__Service__Client__Config() as _:
            assert type(_)           is Schema__Service__Client__Config
            assert base_classes(_)   == [Type_Safe, object]
            assert _.mode            is None                                # Default: not configured
            assert _.fast_api_app    is None                                # Default: no app
            assert _.base_url        is None
            assert _.api_key_name    is None
            assert _.api_key_value   is None

    def test__config__in_memory_mode(self):                                     # Test IN_MEMORY configuration
        app    = FastAPI()
        config = Schema__Service__Client__Config(mode         = Enum__Client__Mode.IN_MEMORY,
                                                 fast_api_app = app                         )

        assert config.mode         == Enum__Client__Mode.IN_MEMORY
        assert config.fast_api_app is app

    def test__config__remote_mode(self):                                        # Test REMOTE configuration
        config = Schema__Service__Client__Config(mode          = Enum__Client__Mode.REMOTE      ,
                                                 base_url      = 'https://api.example.com'      ,
                                                 api_key_name  = 'X-API-KEY'                    ,
                                                 api_key_value = 'secret-key-123'               )

        assert config.mode                 == Enum__Client__Mode.REMOTE
        assert config.fast_api_app         is None
        assert str(config.base_url)        == 'https://api.example.com'
        assert str(config.api_key_name)    == 'x-api-key'
        assert str(config.api_key_value)   == 'secret-key-123'                                  # confirm auto lower-case provided by Safe_Str__Http__Header__Name
