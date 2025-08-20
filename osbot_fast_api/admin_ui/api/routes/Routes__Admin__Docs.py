import json
from typing                                     import Dict, Any, List

import osbot_fast_api
from osbot_utils.utils.Files import path_combine, file_exists

from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes


class Routes__Admin__Docs(Fast_API__Routes):                                # API routes for documentation access
    tag        = 'admin-docs'
    parent_app = None                                                       # Will be set by Admin_UI__Fast_API

    def api__docs_endpoints(self) -> List[Dict[str, Any]]:
        """Get all available documentation endpoints"""
        base_url = ""  # Relative URLs

        docs = [                                                                                # todo: this needs to be moved to a separate file and/or be calculated dynamically
            {
                "name": "Swagger UI",
                "description": "Interactive API documentation with Swagger UI",
                "url": f"{base_url}/docs",
                "type": "swagger",
                "icon": "swagger"
            },
            {
                "name": "ReDoc",
                "description": "Alternative API documentation with ReDoc",
                "url": f"{base_url}/redoc",
                "type": "redoc",
                "icon": "redoc"
            },
            {
                "name": "OpenAPI JSON",
                "description": "Raw OpenAPI specification in JSON format",
                "url": f"{base_url}/openapi.json",
                "type": "openapi",
                "icon": "json"
            },
            {
                "name": "Python Client",
                "description": "Auto-generated Python client code",
                "url": f"{base_url}/config/openapi.py",
                "type": "client",
                "icon": "python"
            },
            {
                "name": "Routes HTML",
                "description": "HTML view of all application routes",
                "url": f"{base_url}/config/routes/html",
                "type": "routes",
                "icon": "html"
            }
        ]

        # Add admin UI itself
        docs.append({
            "name": "Admin UI",
            "description": "This administration interface",
            "url": "/admin",
            "type": "admin",
            "icon": "admin"
        })

        return docs

    def api__client_examples(self) -> Dict[str, Any]:           # Get client code examples for different languages

        base_url = "http://localhost:8000"  # This should be configurable

        examples = {                                                                # todo: this should be inside json files in the ./admin-ui/content folder
            "curl": {
                "name": "cURL",
                "description": "Command line HTTP client",
                "example": f"""# Get server status
curl {base_url}/config/status

# Set a cookie value
curl -X POST {base_url}/admin/api/cookie/set/api-key \\
  -H "Content-Type: application/json" \\
  -d '{{"value": "your-api-key"}}'

# Get all routes
curl {base_url}/admin/api/routes"""
            },
            "python": {
                "name": "Python",
                "description": "Python with requests library",
                "example": f"""import requests

# Get server status
response = requests.get('{base_url}/config/status')
print(response.json())

# Set a cookie value
response = requests.post(
    '{base_url}/admin/api/cookie/set/api-key',
    json={{'value': 'your-api-key'}}
)
print(response.json())"""
            },
            "javascript": {
                "name": "JavaScript",
                "description": "JavaScript with Fetch API",
                "example": f"""// Get server status
fetch('{base_url}/config/status')
  .then(response => response.json())
  .then(data => console.log(data));

// Set a cookie value
fetch('{base_url}/admin/api/cookie/set/api-key', {{
  method: 'POST',
  headers: {{
    'Content-Type': 'application/json',
  }},
  body: JSON.stringify({{value: 'your-api-key'}}),
}})
  .then(response => response.json())
  .then(data => console.log(data));"""
            }
        }

        return examples

    def api__api_info(self) -> Dict[str, Any]:                                                                          # Get API metadata and information

        openapi = self.parent_app.open_api_json()

        return { "openapi_version"  : openapi.get("openapi", "3.0.0"),                                                  # todo: question: shouldn't we get this data from the Routes__Admin_Info (or even better  Services__Admin_Info)
                 "api_title"        : openapi.get("info", {}).get("title", "API"),
                 "api_version"      : openapi.get("info", {}).get("version", "1.0.0"),
                 "api_description"  : openapi.get("info", {}).get("description"),
                 "servers"          : openapi.get("servers", []),
                 "total_paths"      : len(openapi.get("paths", {})),
                 "total_schemas"    : len(openapi.get("components", {}).get("schemas", {})),
                 "tags"             : self._extract_tags(openapi)    }

    def _extract_tags(self, openapi: Dict) -> List[Dict[str, Any]]:                                                     # Extract tags from OpenAPI spec
        tags = {}

        # Get tags from paths
        for path, methods in openapi.get("paths", {}).items():                                                          # todo: review this logic, since a) it doesn't make sense to be here (should be in a Service_* class) and b) why are we calculating this on the docs section?
            for method, operation in methods.items():
                if isinstance(operation, dict):
                    for tag in operation.get("tags", []):
                        if tag not in tags:
                            tags[tag] = {"name": tag, "count": 0, "paths": []}
                        tags[tag]["count"] += 1
                        tags[tag]["paths"].append(f"{method.upper()} {path}")

        # Get tag descriptions from root level tags
        for tag_info in openapi.get("tags", []):
            tag_name = tag_info.get("name")
            if tag_name in tags:
                tags[tag_name]["description"] = tag_info.get("description")

        return list(tags.values())

    def api__content__doc_id(self, doc_id: str) -> Dict[str, Any]:  # Serve documentation content from markdown/JSON files

        # Map doc_id to content files
        content_path = path_combine(osbot_fast_api.path, f'admin_ui/content/docs/{doc_id}.md')
        json_path = path_combine(osbot_fast_api.path, f'admin_ui/content/docs/{doc_id}.json')

        # Try markdown first
        if file_exists(content_path):
            with open(content_path, 'r', encoding='utf-8') as f:  # Add encoding
                content = f.read()
                return {
                    "markdown": content,
                    "format": "markdown",
                    "doc_id": doc_id
                }

        # Try JSON
        elif file_exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:  # Add encoding
                data = json.load(f)
                return {
                    "sections": data.get("sections", []),
                    "format": "json",
                    "doc_id": doc_id
                }

        # Return error (not default content - let frontend handle it)
        return {
            "error": "Content not found",
            "doc_id": doc_id,
            "format": "error"
        }

    def setup_routes(self):
        self.add_route_get(self.api__docs_endpoints)
        self.add_route_get(self.api__client_examples)
        self.add_route_get(self.api__api_info)
        self.add_route_get(self.api__content__doc_id)