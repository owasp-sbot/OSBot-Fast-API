from typing                                     import Optional
from osbot_utils.helpers.html.utils.Html__Query import Html__Query


class Html__Query__Fast_API(Html__Query):

    @property
    def has_swagger_ui(self) -> bool:                                             # Check if page has Swagger UI setup
        return (self.find_by_id('swagger-ui') is not None and
                any('SwaggerUIBundle' in s for s in self.inline_scripts))

    @property
    def has_redoc(self) -> bool:                                                  # Check if page has ReDoc setup
        return any('redoc' in src.lower() for src in self.script_sources)

    @property
    def openapi_url(self) -> Optional[str]:                                       # Extract OpenAPI URL from Swagger config
        for script in self.inline_scripts:
            if 'SwaggerUIBundle' in script:
                import re
                match = re.search(r"url:\s*['\"]([^'\"]+)['\"]", script)
                if match:
                    return match.group(1)
        return None

    @property
    def api_title(self) -> Optional[str]:                                         # Extract API title from page
        if self.title:
            # Remove common suffixes
            return self.title.replace(' - Swagger UI', '').replace(' - ReDoc', '')
        return None

    def has_offline_docs(self) -> bool:                                           # Check if using offline documentation
        for src in self.script_sources:
            if '/static/' in src or src.startswith('/'):                         # Local/static paths indicate offline
                return True
        return False