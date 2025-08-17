from unittest                                               import TestCase
from osbot_utils.testing.test_data.const__test__data__html  import TEST__DATA__HTML__SWAGGER
from osbot_fast_api.utils.html.Html__Query__Fast_API        import Html__Query__Fast_API


class test_Html__Query__Fast_API(TestCase):

    @classmethod
    def setUpClass(cls):  # Setup test HTML samples
        cls.html_swagger        = TEST__DATA__HTML__SWAGGER

    def test_has_swagger_ui(self):                                                # Test Swagger UI detection
        with Html__Query__Fast_API(html=self.html_swagger) as query:
            assert query.has_swagger_ui is True
            assert query.openapi_url    == '/openapi.json'
            assert query.api_title      == 'Fast_API'

    def test_has_redoc(self):                                                     # Test ReDoc detection
        redoc_html = '<html><head><title>My API - ReDoc</title></head><body><script src="/static/redoc/redoc.js"></script></body></html>'
        with Html__Query__Fast_API(html=redoc_html) as query:
            assert query.has_redoc   is True
            assert query.api_title   == 'My API'

    def test_has_offline_docs(self):                                              # Test offline docs detection
        with Html__Query__Fast_API(html=self.html_swagger) as query:
            assert query.has_offline_docs() is True

        # Integration test with FastAPI docs
    def test_with_fastapi_swagger_html(self):                                     # Test with actual FastAPI Swagger HTML
        with Html__Query__Fast_API(html=self.html_swagger) as query:
            assert query.title                                                 == 'Fast_API - Swagger UI'
            assert query.has_link(href = '/static/swagger-ui/swagger-ui.css' ,
                                 rel  = 'stylesheet'                         ) is True
            assert '/static/swagger-ui/swagger-ui.css'                        in query.css_links
            assert query.has_link(href = '/static/swagger-ui/favicon.png'    ,
                                 rel  = 'shortcut icon'                      ) is True
            assert '/static/swagger-ui/swagger-ui-bundle.js'                  in query.script_sources
            assert any('SwaggerUIBundle' in script for script in query.inline_scripts)

            swagger_div = query.find_by_id('swagger-ui')
            assert swagger_div      is not None
            assert swagger_div.tag  == 'div'
            assert query.has_swagger_ui is True