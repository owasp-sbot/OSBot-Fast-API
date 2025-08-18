from typing                                                             import Type, Dict, Any, List, Optional
from osbot_utils.type_safe.Type_Safe                                    import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe          import type_safe
from osbot_utils.type_safe.type_safe_core.shared.Type_Safe__Cache       import type_safe_cache
from osbot_fast_api.api.transformers.Type_Safe__To__Json                import type_safe__to__json


class Type_Safe__To__LLM_Tools(Type_Safe):  # Converts Type_Safe classes to LLM function/tool definitions for various platforms"""

    include_descriptions : bool = True
    include_examples     : bool = True
    strict_validation    : bool = False                                        # Include all Type_Safe constraints

    @type_safe
    def to_openai_function(self, type_safe_class : Type[Type_Safe]       ,     # Type_Safe class
                                 function_name   : str                    ,     # Function name
                                 description     : str                           # Function description
                           ) -> Dict[str, Any]:                                # Returns OpenAI function schema
        """Convert to OpenAI function calling format (GPT-4, GPT-3.5-turbo)"""

        json_schema = type_safe__to__json.convert_class(type_safe_class)

        # OpenAI function format
        function_def = { "name"        : function_name                                    ,
                        "description" : description                                      ,
                        "parameters"  : { "type"       : "object"                                ,
                                         "properties" : json_schema.get("properties", {})       ,
                                         "required"   : json_schema.get("required", [])         } }

        # Add parameter descriptions if available
        if self.include_descriptions:
            self._add_parameter_descriptions(type_safe_class, function_def["parameters"]["properties"])

        return function_def

    @type_safe
    def to_anthropic_tool(self, type_safe_class : Type[Type_Safe]       ,      # Type_Safe class
                               tool_name        : str                    ,      # Tool name
                               description      : str                           # Tool description
                          ) -> Dict[str, Any]:                                 # Returns Anthropic tool schema
        """Convert to Anthropic Claude tool format"""

        json_schema = type_safe__to__json.convert_class(type_safe_class)

        # Anthropic Claude tool format
        tool_def = { "name"         : tool_name                                          ,
                    "description"  : description                                        ,
                    "input_schema" : { "type"       : "object"                                  ,
                                      "properties" : json_schema.get("properties", {})         ,
                                      "required"   : json_schema.get("required", [])           } }

        # Add parameter descriptions
        if self.include_descriptions:
            self._add_parameter_descriptions(type_safe_class, tool_def["input_schema"]["properties"])

        return tool_def

    @type_safe
    def to_langchain_tool(self, type_safe_class : Type[Type_Safe]       ,      # Type_Safe class
                                name            : str                    ,      # Tool name
                                description     : str                    ,      # Tool description
                                return_direct   : bool          = False         # LangChain specific
                          ) -> Dict[str, Any]:                                 # Returns LangChain tool schema
        """Convert to LangChain tool format"""

        json_schema = type_safe__to__json.convert_class(type_safe_class)

        # LangChain tool format
        tool_def = { "name"          : name                ,
                    "description"   : description          ,
                    "args_schema"   : json_schema          ,
                    "return_direct" : return_direct        }

        return tool_def

    @type_safe
    def to_gemini_function(self, type_safe_class : Type[Type_Safe]       ,     # Type_Safe class
                                 function_name   : str                    ,     # Function name
                                 description     : str                           # Function description
                           ) -> Dict[str, Any]:                                # Returns Gemini function schema
        """Convert to Google Gemini function calling format"""

        json_schema = type_safe__to__json.convert_class(type_safe_class)

        # Gemini function format
        function_def = { "name"        : function_name                                    ,
                        "description" : description                                      ,
                        "parameters"  : { "type"       : "object"                                ,
                                         "properties" : json_schema.get("properties", {})       ,
                                         "required"   : json_schema.get("required", [])         } }

        # Gemini has slightly different type names
        self._convert_types_for_gemini(function_def["parameters"]["properties"])

        return function_def

    @type_safe
    def to_bedrock_tool(self, type_safe_class : Type[Type_Safe]       ,        # Type_Safe class
                              tool_name       : str                    ,        # Tool name
                              description     : str                             # Tool description
                        ) -> Dict[str, Any]:                                   # Returns AWS Bedrock tool schema
        """Convert to AWS Bedrock tool format"""

        json_schema = type_safe__to__json.convert_class(type_safe_class)

        # AWS Bedrock tool format
        tool_def = { "toolSpec" : { "name"        : tool_name                                   ,
                                   "description" : description                                  ,
                                   "inputSchema" : { "json" : { "type"       : "object"                        ,
                                                               "properties" : json_schema.get("properties", {}) ,
                                                               "required"   : json_schema.get("required", [])   } } } }

        return tool_def

    @type_safe
    def create_function_description(self, type_safe_class : Type[Type_Safe]  ,  # Class to describe
                                          function_name   : str       = None     # Optional function name
                                    ) -> str:                                   # Returns human-readable description
        """Generate human-readable function description for documentation"""

        annotations = type_safe_cache.get_class_annotations(type_safe_class)
        cls_kwargs  = type_safe_class.__cls_kwargs__()

        lines = []
        function_name = function_name or type_safe_class.__name__
        lines.append(f"Function: {function_name}")
        lines.append("Parameters:")

        for field_name, field_type in annotations:
            required     = field_name not in cls_kwargs
            required_str = " (required)" if required else " (optional)"
            type_str     = self._type_to_string(field_type)
            lines.append(f"  - {field_name}: {type_str}{required_str}")

            # Add default value if exists
            if field_name in cls_kwargs:
                default = cls_kwargs[field_name]
                if default is not None:
                    lines.append(f"    default: {default}")

        return "\n".join(lines)

    @type_safe
    def create_example_call(self, type_safe_class : Type[Type_Safe]       ,    # Class to create example for
                                  function_name   : str             = None      # Optional function name
                            ) -> Dict[str, Any]:                                # Returns example call data
        """Generate example function call with sample data"""

        annotations = type_safe_cache.get_class_annotations(type_safe_class)
        cls_kwargs  = type_safe_class.__cls_kwargs__()

        example = {}

        for field_name, field_type in annotations:
            # Generate appropriate example based on type
            example_value = self._generate_example_value(field_type)
            if example_value is not None:
                example[field_name] = example_value
            elif field_name in cls_kwargs:
                # Use default value as example
                example[field_name] = cls_kwargs[field_name]

        return { "function" : function_name or type_safe_class.__name__ ,
                "args"     : example                                   }

    def _type_to_string(self, field_type : Any                                 # Type to convert
                        ) -> str:                                               # Returns readable string
        """Convert type to readable string"""
        if hasattr(field_type, '__name__'):
            return field_type.__name__
        return str(field_type).replace('typing.', '')

    def _add_parameter_descriptions(self, type_safe_class : Type[Type_Safe]   ,  # Source class
                                          properties      : Dict[str, Any]        # Properties to update
                                    ) -> None:                                   # Modifies properties in place
        """Add descriptions to parameters from class metadata"""
        if hasattr(type_safe_class, '__annotations_comments__'):
            comments = type_safe_class.__annotations_comments__
            for field_name, schema in properties.items():
                if field_name in comments and isinstance(schema, dict):
                    schema["description"] = comments[field_name]

    def _convert_types_for_gemini(self, properties : Dict[str, Any]            # Properties to convert
                                  ) -> None:                                    # Modifies in place
        """Convert JSON Schema types to Gemini-compatible types"""
        for prop_schema in properties.values():
            if isinstance(prop_schema, dict):
                if prop_schema.get("type") == "integer":
                    prop_schema["type"] = "number"
                if "properties" in prop_schema:
                    self._convert_types_for_gemini(prop_schema["properties"])
                if "items" in prop_schema and isinstance(prop_schema["items"], dict):
                    self._convert_types_for_gemini({"item": prop_schema["items"]})

    def _generate_example_value(self, field_type : Any                         # Type to generate example for
                               ) -> Any:                                       # Returns example value
        """Generate example value based on type"""
        origin = type_safe_cache.get_origin(field_type)

        # Basic types
        if field_type is str:
            return "example_string"
        elif field_type is int:
            return 42
        elif field_type is float:
            return 3.14
        elif field_type is bool:
            return True

        # Collections
        elif origin is list:
            return ["item1", "item2"]
        elif origin is dict:
            return {"key": "value"}
        elif origin is set:
            return ["unique1", "unique2"]

        # Type_Safe classes
        elif isinstance(field_type, type) and issubclass(field_type, Type_Safe):
            # Create minimal example
            return {"example": "data"}

        return None

    @type_safe
    def create_multi_tool_spec(self, tools : List[Dict[str, Any]]              # List of tool definitions
                              ) -> Dict[str, Any]:                              # Returns combined spec
        """Create a specification with multiple tools for batch registration"""

        return { "tools"   : tools                        ,
                "version" : "1.0"                         ,
                "count"   : len(tools)                    }


type_safe__to__llm_tools = Type_Safe__To__LLM_Tools()                         # Singleton instance