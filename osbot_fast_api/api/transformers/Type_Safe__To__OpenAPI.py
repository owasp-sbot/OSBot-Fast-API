import json
from typing                                                       import Type, Dict, Any, List, Optional
from osbot_utils.type_safe.Type_Safe                              import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe    import type_safe
from osbot_utils.type_safe.type_safe_core.shared.Type_Safe__Cache import type_safe_cache
from osbot_utils.utils.Toml                                       import toml_dict_to_file
from osbot_fast_api.api.transformers.Type_Safe__To__Json          import type_safe__to__json


class Type_Safe__To__OpenAPI(Type_Safe):                        # Converts Type_Safe classes to OpenAPI 3.0 schema components

    components_cache : Dict[str, Dict[str, Any]]
    include_examples : bool = True
    api_version      : str  = "3.0.0"                                          # OpenAPI version

    @type_safe
    def convert_class(self, type_safe_class : Type[Type_Safe]       ,          # Type_Safe class to convert
                            component_name  : str             = None ,          # Name in components/schemas
                            example         : Dict[str, Any]  = None            # Optional example
                      ) -> Dict[str, Any]:                                      # Returns OpenAPI schema

        component_name = component_name or type_safe_class.__name__

        if component_name in self.components_cache:
            return {"$ref": f"#/components/schemas/{component_name}"}

        # Build OpenAPI schema with proper references
        annotations = type_safe_cache.get_class_annotations(type_safe_class)
        properties = {}

        for field_name, field_type in annotations:
            properties[field_name] = self.convert_field_type(field_type)

        openapi_schema = { "type"                 : "object"                           ,
                           "properties"            : properties                         ,
                           "required"              : []                                 ,  # Type_Safe doesn't have required fields
                           "additionalProperties"  : False                              }


        # Add example if provided
        if example and self.include_examples:
            openapi_schema["example"] = example

        # Convert nullable fields (JSON Schema draft-07 to OpenAPI 3.0)
        self._convert_nullable_fields(openapi_schema)

        # Store in cache
        self.components_cache[component_name] = openapi_schema

        return {"$ref": f"#/components/schemas/{component_name}"}

    def _convert_nullable_fields(self, schema : Dict[str, Any]                 # Schema to process
                                 ) -> None:                                     # Modifies schema in place
        """Convert JSON Schema nullable to OpenAPI nullable"""
        if "nullable" in schema:
            # Already in OpenAPI format
            return

        if "properties" in schema:
            for prop_schema in schema["properties"].values():
                if isinstance(prop_schema, dict):
                    self._convert_nullable_fields(prop_schema)

        if "items" in schema and isinstance(schema["items"], dict):
            self._convert_nullable_fields(schema["items"])

    @type_safe
    def convert_field_type(self, field_type : Any                               # Field type to convert
                           ) -> Dict[str, Any]:                                 # Returns OpenAPI schema for field
        """Convert field types, handling Type_Safe classes as references"""

        if isinstance(field_type, type) and issubclass(field_type, Type_Safe):      # Handle nested Type_Safe classes
            return self.convert_class(field_type)                                   # Register as component and return ref , This adds to components_cache and returns $ref

        return type_safe__to__json.convert_field_type(field_type)                   # For all other types, use the JSON converter

    @type_safe
    def create_operation(self, method_name  : str                        ,          # Operation ID
                               summary       : str                        ,         # Short summary
                               description   : str                 = None ,         # Long description
                               request_body  : Type[Type_Safe]     = None ,         # Request body type
                               response      : Type[Type_Safe]     = None ,         # Response type
                               parameters    : List[Dict[str, Any]] = None ,        # Query/path params
                               tags          : List[str]           = None           # Operation tags
                          ) -> Dict[str, Any]:                                      # Returns OpenAPI operation

        operation = { "operationId" : method_name ,
                     "summary"     : summary      }

        if description:
            operation["description"] = description

        if tags:
            operation["tags"] = tags

        if parameters:
            operation["parameters"] = parameters

        if request_body:
            schema_ref = self.convert_class(request_body)
            operation["requestBody"] = { "required" : True                                ,
                                        "content"  : { "application/json": { "schema": schema_ref } } }

        # Responses
        responses = {}

        if response:
            schema_ref = self.convert_class(response)
            responses["200"] = { "description" : "Successful response"                        ,
                               "content"     : { "application/json": { "schema": schema_ref } } }
        else:
            responses["200"] = { "description": "Successful response" }

        # Add default error responses
        responses["400"] = { "description": "Bad request"           }
        responses["500"] = { "description": "Internal server error" }

        operation["responses"] = responses

        return operation

    @type_safe
    def create_parameter(self, name         : str                        ,      # Parameter name
                              location      : str                        ,      # in: query, path, header, cookie
                              param_type    : Type                       ,      # Parameter type
                              required      : bool               = False ,      # Is required
                              description   : str                = None  ,      # Parameter description
                              example       : Any                = None          # Example value
                        ) -> Dict[str, Any]:                                    # Returns OpenAPI parameter

        parameter = { "name"     : name     ,
                     "in"       : location ,
                     "required" : required }

        if description:
            parameter["description"] = description

        # Convert type to schema
        schema = type_safe__to__json.convert_field_type(param_type)
        parameter["schema"] = schema

        if example and self.include_examples:
            parameter["example"] = example

        return parameter

    @type_safe
    def create_openapi_spec(self, title       : str                        ,    # API title
                                  version     : str                        ,    # API version
                                  description : str                 = None ,    # API description
                                  servers     : List[Dict[str, str]] = None     # Server URLs
                           ) -> Dict[str, Any]:                                 # Returns full OpenAPI spec

        spec = { "openapi" : self.api_version                      ,
                "info"    : { "title"   : title   ,
                             "version" : version }                ,
                "paths"   : {}                                    ,
                "components" : { "schemas": self.components_cache } }

        if description:
            spec["info"]["description"] = description

        if servers:
            spec["servers"] = servers
        else:
            spec["servers"] = [{"url": "/"}]

        return spec

    @type_safe
    def add_path(self, spec       : Dict[str, Any]         ,                   # OpenAPI spec to modify
                      path       : str                     ,                   # Path template
                      method     : str                     ,                   # HTTP method
                      operation  : Dict[str, Any]                              # Operation object
                ) -> None:                                                     # Modifies spec in place
        """Add a path operation to the OpenAPI spec"""
        if "paths" not in spec:
            spec["paths"] = {}

        if path not in spec["paths"]:
            spec["paths"][path] = {}

        spec["paths"][path][method.lower()] = operation

    @type_safe
    def export_to_file(self, spec     : Dict[str, Any]         ,               # OpenAPI spec
                            filepath  : str                    ,               # Output file path
                            format    : str            = "json"                # json or toml
                       ) -> None:                                              # Writes to file

        if format == "toml":
            toml_dict_to_file(filepath, spec)
        else:  # default to json
            with open(filepath, 'w') as f:
                json.dump(spec, f, indent=2)

    # todo: QUESTION: Why do we need this, isn't this what FastAPI already creates?

    @type_safe
    def generate_from_fast_api_routes(self, fast_api_instance : Any            # Fast_API instance
                                       ) -> Dict[str, Any]:                     # Returns OpenAPI spec
        """Generate OpenAPI spec from Fast_API routes"""
        from osbot_fast_api.api.Fast_API import Fast_API

        if not isinstance(fast_api_instance, Fast_API):
            raise ValueError("Instance must be a Fast_API object")

        # Create base spec
        spec = self.create_openapi_spec(title       = fast_api_instance.name        or "API"     ,
                                        version     = fast_api_instance.version     or "1.0.0"   ,
                                        description = fast_api_instance.description              )

        # Process routes
        routes = fast_api_instance.routes(include_default=False)

        for route_info in routes:
            path        = route_info.get('http_path')
            methods     = route_info.get('http_methods', [])
            method_name = route_info.get('method_name')

            for method in methods:
                operation = { "operationId" : method_name                    ,
                            "summary"     : f"{method} {path}"              ,
                            "responses"   : { "200": { "description": "Success" } } }

                self.add_path(spec, path, method, operation)

        return spec


type_safe__to__openapi = Type_Safe__To__OpenAPI()                             # Singleton instance