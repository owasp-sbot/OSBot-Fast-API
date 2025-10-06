from unittest                                           import TestCase
from osbot_utils.utils.Misc                             import list_set
from osbot_fast_api.api.Fast_API                        import Fast_API
from osbot_fast_api.schemas.Schema__Fast_API__Config    import Schema__Fast_API__Config
from osbot_fast_api.utils.Version                       import version__osbot_fast_api
from osbot_utils.helpers.html.utils.Html__Query         import Html__Query
from osbot_fast_api.api.Fast_API__Offline_Docs          import Fast_API__Offline_Docs, URL__SWAGGER__JS, URL__STATIC__DOCS, URL__REDOC__JS, URL__REDOC__FAVICON, URL__SWAGGER__CSS, URL__SWAGGER__FAVICON
from tests.unit.fast_api__for_tests                     import fast_api, fast_api_client


class test_Fast_API__Offline_Docs(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fast_api              = fast_api
        cls.client                = fast_api_client
        cls.fast_api_offline_docs = Fast_API__Offline_Docs()


    def test_setup_offline_docs(self):  # Test offline documentation setup using Html__Query for structured HTML validation"""
        with self.fast_api as _:
            assert _.config.docs_offline is True

            # Get the HTML response
            response = _.client().get('/docs')
            assert response.status_code == 200

            # Use Html__Query to parse and validate the HTML structure
            with Html__Query(html=response.text) as query:

                assert query.title == 'Fast_API - Swagger UI'                                   # Validate page title

                # Validate CSS and favicon links
                assert query.has_link(href = '/static-docs/swagger-ui/swagger-ui.css',
                                      rel  = 'stylesheet'), "Swagger UI CSS link not found"

                assert query.has_link(
                    href='/static-docs/swagger-ui/favicon.png',
                    rel='shortcut icon'
                ), "Favicon link not found"

                # Validate JavaScript resources
                assert query.has_script(
                    src='/static-docs/swagger-ui/swagger-ui-bundle.js'
                ), "Swagger UI bundle script not found"

                # Validate the Swagger UI container div exists
                swagger_div = query.find_by_id('swagger-ui')
                assert swagger_div is not None, "Swagger UI container div not found"
                assert swagger_div.tag == 'div'

                # Validate inline script configuration
                inline_scripts = query.inline_scripts
                assert len(inline_scripts) > 0, "No inline scripts found"

                # Check for SwaggerUIBundle configuration in inline script
                swagger_config_script = inline_scripts[0]
                assert 'SwaggerUIBundle' in swagger_config_script
                assert "url: '/openapi.json'" in swagger_config_script
                assert '"dom_id": "#swagger-ui"' in swagger_config_script
                assert '"layout": "BaseLayout"' in swagger_config_script
                assert '"deepLinking": true' in swagger_config_script
                assert '"showExtensions": true' in swagger_config_script
                assert '"showCommonExtensions": true' in swagger_config_script

                # Verify presets configuration
                assert 'SwaggerUIBundle.presets.apis' in swagger_config_script
                assert 'SwaggerUIBundle.SwaggerUIStandalonePreset' in swagger_config_script

                # Additional structural validations
                assert query.head is not None, "Head element not found"
                assert query.body is not None, "Body element not found"

                # Validate all expected resources are present
                expected_resources = {
                    'css': ['/static-docs/swagger-ui/swagger-ui.css'],
                    'js': ['/static-docs/swagger-ui/swagger-ui-bundle.js'],
                    'favicon': '/static-docs/swagger-ui/favicon.png'
                }

                assert set(query.css_links) == set(expected_resources['css'])
                assert set(query.script_sources) == set(expected_resources['js'])
                assert query.favicon == expected_resources['favicon']


    def test_setup_redoc_docs(self):        #   Test ReDoc documentation setup using Html__Query
        # note: annoyingly there is still one small svg that is downloaded here ("https://cdn.redoc.ly/redoc/logo-mini.svg")
        #       this is downloaded from inside the f"/redoc/redoc.standalone.js"
        #       todo: see if we should patch that file on download to remove that include
        with self.fast_api as _:
            assert _.config.docs_offline is True

            # Get the ReDoc HTML response
            response = _.client().get('/redoc')
            assert response.status_code == 200

            # Use Html__Query to parse and validate the ReDoc HTML
            with Html__Query(html=response.text) as query:

                # Validate page title
                assert query.title == 'Fast_API - ReDoc'

                # Validate favicon
                assert query.has_link(href = '/static-docs/redoc/favicon.png',
                                     rel   = 'shortcut icon'), "ReDoc favicon not found"

                # Validate JavaScript resources
                assert query.has_script(src='/static-docs/redoc/redoc.standalone.js'), "ReDoc standalone script not found"

                # Validate inline script with OpenAPI URL
                # todo: fix this, since the openapi.json link is loaded using
                #       <redoc spec-url="/openapi.json"></redoc>
                # inline_scripts = query.inline_scripts
                # assert len(inline_scripts) > 0, "No inline scripts found for ReDoc"
                #
                # redoc_script = inline_scripts[0]
                # assert '/openapi.json' in redoc_script, "OpenAPI URL not found in ReDoc script"

                # Additional structure validation
                assert query.head is not None
                assert query.body is not None


    def test_compare_docs_and_redoc_structure(self):
        """Compare the HTML structure of both Swagger UI and ReDoc using Html__Query"""
        with self.fast_api as _:
            # Get both responses
            swagger_response = _.client().get('/docs')
            redoc_response = _.client().get('/redoc')

            # Parse both with Html__Query
            with Html__Query(html=swagger_response.text) as swagger_query:
                swagger_structure = {
                    'title': swagger_query.title,
                    'has_favicon': swagger_query.favicon is not None,
                    'css_count': len(swagger_query.css_links),
                    'js_count': len(swagger_query.script_sources),
                    'inline_script_count': len(swagger_query.inline_scripts),
                    'has_container_div': swagger_query.find_by_id('swagger-ui') is not None
                }

            with Html__Query(html=redoc_response.text) as redoc_query:
                redoc_structure = { 'title'              : redoc_query.title                ,
                                    'has_favicon'        : redoc_query.favicon is not None  ,
                                    'css_count'          : len(redoc_query.css_links        ),
                                    'js_count'           : len(redoc_query.script_sources   ),
                                    'inline_script_count': len(redoc_query.inline_scripts   ),
                                    'has_container_div'  : False                            } # ReDoc uses a different structure

            # Assertions about structure differences
            assert swagger_structure['has_favicon'] == redoc_structure['has_favicon']
            assert swagger_structure['title'].endswith('Swagger UI')
            assert redoc_structure[  'title'].endswith('ReDoc')
            assert swagger_structure['has_container_div'] is True
            assert swagger_structure['css_count'    ] == 1  # Swagger has CSS
            assert redoc_structure[  'css_count'    ] == 0    # ReDoc doesn't use external CSS


    def test_validate_offline_assets_configuration(self):       # Validate that offline asset URLs match expected versions
        with self.fast_api as _:
            offline_docs = Fast_API__Offline_Docs()

            # Test Swagger UI configuration
            swagger_response = _.client().get('/docs')
            with Html__Query(html=swagger_response.text) as query:
                # Verify the static paths are correctly configured
                assert query.has_script(src='/static-docs/swagger-ui/swagger-ui-bundle.js')
                assert query.has_link(href='/static-docs/swagger-ui/swagger-ui.css')

                # Check version consistency if needed
                # You could extend this to verify the actual version numbers
                # if they're embedded in the HTML or accessible via the API

            # Test ReDoc configuration
            redoc_response = _.client().get('/redoc')
            with Html__Query(html=redoc_response.text) as query:
                assert query.has_script(src='/static-docs/redoc/redoc.standalone.js')

                # Verify versions match configuration
                assert offline_docs.SWAGGER_UI_VERSION == "5.9.0"
                assert offline_docs.REDOC_VERSION == "2.1.3"


    def test_html_structure_integrity(self):
        """Test that the HTML structure can be parsed and reconstructed without loss"""
        from osbot_utils.helpers.html.transformers.Html__To__Html_Dict import Html__To__Html_Dict
        from osbot_utils.helpers.html.transformers.Html_Dict__To__Html import Html_Dict__To__Html

        with self.fast_api as _:
            response = _.client().get('/docs')
            original_html = response.text

            # Convert HTML to dictionary structure
            parser = Html__To__Html_Dict(original_html)
            html_dict = parser.convert()

            # Validate dictionary structure
            assert html_dict['tag'] == 'html'
            assert 'nodes' in html_dict

            # Find head and body in nodes
            head_node = next((n for n in html_dict['nodes'] if n.get('tag') == 'head'), None)
            body_node = next((n for n in html_dict['nodes'] if n.get('tag') == 'body'), None)

            assert head_node is not None, "Head node not found in HTML structure"
            assert body_node is not None, "Body node not found in HTML structure"

            # Validate head contains expected elements
            head_children = head_node.get('nodes', [])
            link_tags = [n for n in head_children if n.get('tag') == 'link']
            title_tag = next((n for n in head_children if n.get('tag') == 'title'), None)

            assert len(link_tags) == 2, f"Expected 2 link tags, found {len(link_tags)}"
            assert title_tag is not None, "Title tag not found"

            # Validate body structure
            body_children = body_node.get('nodes', [])
            div_tags = [n for n in body_children if n.get('tag') == 'div']
            script_tags = [n for n in body_children if n.get('tag') == 'script']

            assert len(div_tags) >= 1, "No div tags found in body"
            assert len(script_tags) >= 2, "Expected at least 2 script tags"

            # Test round-trip conversion
            converter = Html_Dict__To__Html(html_dict)
            reconstructed_html = converter.convert()

            # Parse reconstructed HTML to verify integrity
            with Html__Query(html=reconstructed_html) as query:
                assert query.title == 'Fast_API - Swagger UI'
                assert query.find_by_id('swagger-ui') is not None

    def test__confirm_that_static_resources_are_available(self):
        assert self.client.get('/openapi.json'                               ).status_code == 200
        assert self.client.get('/AAAAAAA.json'                               ).status_code == 404
        assert self.client.get(f'{URL__STATIC__DOCS}/ping.txt'               ).status_code == 200
        assert self.client.get(f'{URL__STATIC__DOCS}{URL__REDOC__JS}'       ).status_code == 200
        assert self.client.get(f'{URL__STATIC__DOCS}{URL__REDOC__FAVICON}'  ).status_code == 200
        assert self.client.get(f'{URL__STATIC__DOCS}{URL__SWAGGER__JS}'     ).status_code == 200
        assert self.client.get(f'{URL__STATIC__DOCS}{URL__SWAGGER__CSS}'    ).status_code == 200
        assert self.client.get(f'{URL__STATIC__DOCS}{URL__SWAGGER__FAVICON}').status_code == 200

    def test_save_resources_to_static_folder(self):
        with self.fast_api_offline_docs as _:
            _.save_resources_to_static_folder()

    def test_bug__offline_docs_disabled(self):                                            # Test with offline docs disabled
        config = Schema__Fast_API__Config(docs_offline=False)
        with Fast_API(config=config).setup() as _:
            client = _.client()
            response = client.get('/docs')

            # Should still work but with CDN resources
            #assert response.status_code == 200                                          # BUG
            assert response.status_code == 404                                           # BUG

            # with Html__Query(html=response.text) as query:
            #     # Should use CDN URLs, not local
            #     for script_src in query.script_sources:
            #         assert not script_src.startswith('/static-docs')

    def test_static_docs_mount_exists(self):                                         # Test static mount configuration
        with self.fast_api as _:
            # Find static-docs mount
            static_docs_mounts = [r for r in _.app().routes
                                 if hasattr(r, 'path') and r.path == '/static-docs']

            assert len(static_docs_mounts) == 1
            mount = static_docs_mounts[0]

            # Verify it's a StaticFiles mount
            from starlette.staticfiles import StaticFiles
            assert isinstance(mount.app, StaticFiles)

    def test__bug__cache_headers_for_static_resources(self):                                # Test caching headers
        response = self.client.get(f'{URL__STATIC__DOCS}{URL__SWAGGER__JS}')
        headers_list = [ 'accept-ranges'      ,
                         'content-length'     ,
                         'content-type'       ,
                         'etag'               ,
                         'fast-api-request-id',
                         'last-modified'      ]
        assert response.status_code == 200
        #if not_in_github_action():                                                              # weirdly, this only fails locally
        assert list_set(response.headers) == headers_list
        assert 'cache-control' not in response.headers                                      # BUG: todo: see if we should be setting these
            #assert 'max-age='         in response.headers['cache-control']                    # BUG: todo: see if we should be setting these
        # else:
        #     headers_list.append('cache-control')                                                # todo: figure out why this work in GitHub Actions and not locally
        #
        #     assert list_set(response.headers)  == sorted(headers_list)
        #     assert 'max-age='                  in response.headers['cache-control']

    def test_openapi_json_structure(self):                                                  # Test OpenAPI spec structure
        response = self.client.get('/openapi.json')

        assert response.status_code == 200
        openapi_spec = response.json()

        assert 'openapi' in openapi_spec
        assert 'info' in openapi_spec
        assert 'paths' in openapi_spec
        assert openapi_spec['info']['title'] == 'Fast_API'
        assert openapi_spec['info']['version'] == version__osbot_fast_api