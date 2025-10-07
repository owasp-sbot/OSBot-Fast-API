import json
import osbot_fast_api
from typing                                     import Dict, Any, List, Optional
from fastapi                                    import Request, Response
from osbot_utils.utils.Files                    import path_combine, file_exists
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe            import Type_Safe
from osbot_utils.utils.Misc                     import random_guid


class Cookie__Config(Type_Safe):                    # Configuration for a cookie
    name        : str
    description : str           = ""
    required    : bool          = False
    secure      : bool          = True
    http_only   : bool          = True
    same_site   : str           = "strict"
    category    : str           = "general"
    validator   : str           = None              # Optional validation pattern


class Cookie__Value(Type_Safe):                     # Cookie value to set
    value       : str
    expires_in  : Optional[int] = None              # Seconds until expiration


class Cookie__Template(Type_Safe):                  # Template for common cookie configurations
    id          : str
    name        : str
    description : str
    cookies     : List[Cookie__Config]

class Cookie__Bulk_Request(Type_Safe):
    name       : str
    value      : str
    expires_in : Optional[int] = None

class Cookies__Bulk_Request(Type_Safe):
    cookies : List[Cookie__Bulk_Request]

class Routes__Admin__Cookies(Fast_API__Routes):         # API routes for cookie management
    tag        = 'admin-cookies'
    parent_app            = None                                   # Will be set by Admin_UI__Fast_API
    _templates : list     = None

    @property
    def COOKIE_TEMPLATES(self):
        if self._templates is None:
            template_path = path_combine(osbot_fast_api.path, 'admin_ui/content/templates/cookies.json')
            if file_exists(template_path):
                with open(template_path, 'r') as f:
                    data = json.load(f)
                    self._templates = data.get('templates', [])
            else:
                self._templates = []  # Fallback to empty
        return self._templates

    # # Predefined cookie templates
    # COOKIE_TEMPLATES = [                                # todo: move to .json file which can then be changed by the multiple implementations (especialy since by default we should not have have all this cookies set in the main Fast_API package)
    #     {
    #         "id": "openai",
    #         "name": "OpenAI Configuration",
    #         "description": "Cookies for OpenAI API integration",
    #         "cookies": [
    #             {
    #                 "name": "openai-api-key",
    #                 "description": "OpenAI API Key",
    #                 "required": True,
    #                 "category": "llm",
    #                 "validator": "^sk-[a-zA-Z0-9]{48}$"
    #             },
    #             {
    #                 "name": "openai-org-id",
    #                 "description": "OpenAI Organization ID",
    #                 "required": False,
    #                 "category": "llm"
    #             }
    #         ]
    #     },
    #     {
    #         "id": "anthropic",
    #         "name": "Anthropic Configuration",
    #         "description": "Cookies for Anthropic Claude API",
    #         "cookies": [
    #             {
    #                 "name": "anthropic-api-key",
    #                 "description": "Anthropic API Key",
    #                 "required": True,
    #                 "category": "llm",
    #                 "validator": "^sk-ant-[a-zA-Z0-9-]{95}$"
    #             }
    #         ]
    #     },
    #     {
    #         "id": "groq",
    #         "name": "Groq Configuration",
    #         "description": "Cookies for Groq API",
    #         "cookies": [
    #             {
    #                 "name": "groq-api-key",
    #                 "description": "Groq API Key",
    #                 "required": True,
    #                 "category": "llm"
    #             }
    #         ]
    #     },
    #     {
    #         "id": "auth",
    #         "name": "Authentication",
    #         "description": "Authentication cookies",
    #         "cookies": [
    #             {
    #                 "name": "auth-token",
    #                 "description": "Authentication token",
    #                 "required": False,
    #                 "category": "auth"
    #             },
    #             {
    #                 "name": "api-key",
    #                 "description": "API Key for protected endpoints",
    #                 "required": False,
    #                 "category": "auth"
    #             }
    #         ]
    #     }
    # ]

    def api__cookies_list(self, request: Request) -> List[Dict[str, Any]]:                  # Get list of all cookies with their current values
        cookies = []

        all_cookie_configs = {}                                                             # Get all cookie configurations from templates
        for template in self.COOKIE_TEMPLATES:
            for cookie_config in template['cookies']:
                if cookie_config['name'] not in all_cookie_configs:
                    all_cookie_configs[cookie_config['name']] = cookie_config

        for cookie_name, config in all_cookie_configs.items():                              # Add current values from request
            current_value = request.cookies.get(cookie_name)
            cookies.append({ "name"         : cookie_name                               ,
                             "description"  : config.get('description', ''             ),
                             "category"     : config.get('category'   , 'general'      ),
                             "required"     : config.get('required'   , False          ),
                             "has_value"    : current_value is not None                 ,
                             "value_length" : len(current_value) if current_value else 0,
                             "is_valid"     : self._validate_cookie_value(current_value, config.get('validator'))})

        return cookies

    def api__cookies_templates(self) -> List[Dict[str, Any]]:           # Get available cookie templates
        return self.COOKIE_TEMPLATES                                    # todo: see note above in COOKIE_TEMPLATES

    def api__cookie_get__cookie_name(self, cookie_name: str, request: Request) -> Dict[str, Any]:                                    # Get a specific cookie value
        value = request.cookies.get(cookie_name)

        config = None                                                                                                   # Find cookie config
        for template in self.COOKIE_TEMPLATES:
            for cookie_config in template['cookies']:
                if cookie_config['name'] == cookie_name:
                    config = cookie_config
                    break

        return {    "name"    : cookie_name      ,                                                                      # todo: convert this to a Schema_* class
                    "value"   : value            ,
                    "exists"  : value is not None,
                    "config"  : config           ,
                    "is_valid": self._validate_cookie_value(value, config.get('validator') if config else None) }

    def api__cookie_set__cookie_name(self, cookie_name   : str           ,
                                           cookie_value  : Cookie__Value ,
                                           request       : Request       ,
                                           response      : Response
                                      ) -> Dict[str, Any]:                                                                           # Set a cookie value
        config = None                                                       # Find cookie config
        for template in self.COOKIE_TEMPLATES:
            for cookie_config in template['cookies']:
                if cookie_config['name'] == cookie_name:
                    config = cookie_config
                    break

        if not config:                                                      # Allow setting unknown cookies with defaults
            config = {  "secure"    : request.url.scheme == 'https',        # todo: convert this to a Schema_* class
                        "http_only" : True                         ,
                        "same_site" : "strict"                     }

        if config.get('validator') and not self._validate_cookie_value(cookie_value.value, config['validator']):        # Validate if validator exists
            return {    "success": False,
                        "error": f"Value does not match required pattern: {config['validator']}" }                      # todo: convert this to a Schema_* class

        # Set the cookie
        response.set_cookie(key      = cookie_name                       ,
                            value    = cookie_value.value                ,
                            httponly = config.get('http_only', True     ),
                            secure   = config.get('secure'   , True     ),
                            samesite = config.get('same_site', 'strict' ),
                            max_age  = cookie_value.expires_in if cookie_value.expires_in else None)

        return { "success"  : True                          ,                                                           # todo: convert this to a Schema_* class
                 "name"     : cookie_name                   ,                                                           #       we also need to standardise the return object/class
                 "value_set": len(cookie_value.value) > 0   }

    def api__cookie_delete__cookie_name(self, cookie_name: str, response: Response) -> Dict[str, Any]:                               # Delete a cookie
        response.delete_cookie(key=cookie_name)

        return { "success"  : True       ,                                                                              # todo: convert this to a Schema_* class
                 "name"     : cookie_name,
                 "deleted"  : True       }

    def api__cookies_bulk_set(self, bulk_request : Cookies__Bulk_Request, #cookies: List[Dict[str, str]],
                                    request      : Request           ,
                                    response     : Response
                               ) -> Dict[str, Any]:        # Set multiple cookies at once"""
        results = []

        for cookie_data in bulk_request.cookies:
            cookie_name       = cookie_data.name
            cookie_value      = Cookie__Value(value=cookie_data.value , expires_in=cookie_data.expires_in)

            if cookie_name:
                result = self.api__cookie_set__cookie_name(cookie_name, cookie_value, request, response)
                results.append(result)

        return {
            "success": all(r.get('success') for r in results),
            "results": results
        }

    def api__generate_value__value_type(self, value_type: str = "uuid") -> Dict[str, str]:
        """Generate a value for cookies (UUID, random string, etc.)"""
        if value_type == "uuid":
            return {"value": random_guid(), "type": "uuid"}
        elif value_type == "api_key":
            # Generate a mock API key format
            import random
            import string
            prefix = "sk-"
            random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=48))
            return {"value": f"{prefix}{random_part}", "type": "api_key"}
        else:
            return {"value": random_guid(), "type": "default"}

    def _validate_cookie_value(self, value: Optional[str], pattern: Optional[str]) -> bool:
        """Validate a cookie value against a pattern"""
        if not pattern or not value:
            return True

        try:
            import re
            return bool(re.match(pattern, value))
        except:
            return True

    def setup_routes(self):
        self.add_route_get   (self.api__cookies_list              )
        self.add_route_get   (self.api__cookies_templates         )
        self.add_route_get   (self.api__cookie_get__cookie_name   )
        self.add_route_post  (self.api__cookie_set__cookie_name   )
        self.add_route_delete(self.api__cookie_delete__cookie_name)
        self.add_route_post  (self.api__cookies_bulk_set          )
        self.add_route_get   (self.api__generate_value__value_type            )
