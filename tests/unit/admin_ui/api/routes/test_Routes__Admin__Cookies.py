from unittest                                                   import TestCase
from osbot_fast_api.admin_ui.api.routes.Routes__Admin__Cookies  import Routes__Admin__Cookies, Cookie__Config, Cookie__Value, Cookie__Template
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Objs    import setup__admin_ui_test_objs, cleanup_admin_ui_test_objs
from osbot_fast_api.api.routes.Fast_API__Routes                 import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe                            import Type_Safe
from osbot_utils.utils.Objects                                  import base_types


class test_Routes__Admin__Cookies(TestCase):                # Test Routes__Admin__Cookies class directly

    @classmethod
    def setUpClass(cls):
        """Setup routes instance"""
        cls.test_objs = setup__admin_ui_test_objs(with_parent=True)
        cls.routes_cookies = Routes__Admin__Cookies()
        cls.routes_cookies.parent_app = cls.test_objs.parent_fast_api

    @classmethod
    def tearDownClass(cls):
        """Cleanup"""
        cleanup_admin_ui_test_objs(cls.test_objs)

    def test_01_setUpClass(self):
        """Verify class setup and inheritance"""
        with self.routes_cookies as _:
            assert type(_)          is Routes__Admin__Cookies
            assert Fast_API__Routes in base_types(_)
            assert Type_Safe        in base_types(_)
            assert _.tag            == 'admin-cookies'

    def test_02_cookie_templates(self):
        """Test predefined cookie templates"""
        templates = self.routes_cookies.COOKIE_TEMPLATES

        assert len(templates) == 1

        # Check template structure
        template_ids = [t['id'] for t in templates]
        assert 'openai' in template_ids
        #assert 'anthropic' in template_ids
        #assert 'groq' in template_ids
        #assert 'auth' in template_ids

        # Verify OpenAI template
        openai_template = next(t for t in templates if t['id'] == 'openai')
        assert openai_template['name'] == 'OpenAI Configuration'
        assert len(openai_template['cookies']) == 1

        # Check OpenAI API key config
        openai_key = openai_template['cookies'][0]
        assert openai_key['name'     ] == 'openai-api-key'
        assert openai_key['required' ] is True
        assert openai_key['category' ] == 'llm'
        assert openai_key['validator'] == '^sk-[a-zA-Z0-9]{48}$'

    def test_03__bug__api__cookies_templates(self):
        """Test getting cookie templates"""
        result = self.routes_cookies.api__cookies_templates()

        assert result      == self.routes_cookies.COOKIE_TEMPLATES
        assert len(result) == 1

        # Verify immutability (templates should not be modified)
        result[0]['id'] = 'modified'                                            # BUG: todo: see if this actually a valid test when making the changes directly in the object
        fresh_result    = self.routes_cookies.api__cookies_templates()
        #assert fresh_result[0]['id'] != 'modified'                             # BUG:
        assert fresh_result[0]['id'] == 'modified'                              # BUG: todo: check if this is the correct result

    def test_04_validate_cookie_value(self):
        """Test cookie value validation"""
        routes = self.routes_cookies

        # Test with OpenAI pattern
        openai_pattern = '^sk-[a-zA-Z0-9]{48}$'

        # Valid OpenAI key
        valid_key = 'sk-' + 'a' * 48
        assert routes._validate_cookie_value(valid_key, openai_pattern) is True

        # Invalid OpenAI key (too short)
        invalid_key = 'sk-abc123'
        assert routes._validate_cookie_value(invalid_key, openai_pattern) is False

        # No pattern - always valid
        assert routes._validate_cookie_value('anything', None) is True

        # No value - always valid
        assert routes._validate_cookie_value(None, openai_pattern) is True

        # Test with Anthropic pattern
        anthropic_pattern = '^sk-ant-[a-zA-Z0-9-]{95}$'
        valid_anthropic = 'sk-ant-' + 'a' * 95
        assert routes._validate_cookie_value(valid_anthropic, anthropic_pattern) is True

    def test_05_api__generate_value(self):
        """Test value generation"""
        routes = self.routes_cookies

        # Test UUID generation
        result = routes.api__generate_value__value_type('uuid')
        assert result['type'] == 'uuid'
        assert len(result['value']) == 36  # UUID length
        assert '-' in result['value']

        # Test API key generation
        result = routes.api__generate_value__value_type('api_key')
        assert result['type'] == 'api_key'
        assert result['value'].startswith('sk-')
        assert len(result['value']) == 51  # sk- + 48 chars

        # Test default generation
        result = routes.api__generate_value__value_type('unknown')
        assert result['type'] == 'default'
        assert len(result['value']) == 36  # Falls back to UUID

    def test_06_cookie_config_schema(self):
        """Test Cookie__Config Type_Safe schema"""
        config = Cookie__Config(
            name='test-cookie',
            description='A test cookie',
            required=True,
            secure=False,
            http_only=True,
            same_site='lax',
            category='test',
            validator='^test-.*$'
        )

        assert config.name == 'test-cookie'
        assert config.description == 'A test cookie'
        assert config.required is True
        assert config.secure is False
        assert config.http_only is True
        assert config.same_site == 'lax'
        assert config.category == 'test'
        assert config.validator == '^test-.*$'

    def test_07_cookie_value_schema(self):
        """Test Cookie__Value Type_Safe schema"""
        value = Cookie__Value(
            value='test-value-123',
            expires_in=3600
        )

        assert value.value == 'test-value-123'
        assert value.expires_in == 3600

        # Test without expiration
        value2 = Cookie__Value(value='test-value')
        assert value2.value == 'test-value'
        assert value2.expires_in is None


