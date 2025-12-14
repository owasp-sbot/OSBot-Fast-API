from typing                                                         import Type, Dict, Any, get_args, Union, Optional, Tuple
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from osbot_utils.type_safe.Type_Safe__Primitive                     import Type_Safe__Primitive
from osbot_utils.type_safe.primitives.core.Safe_Str                 import Safe_Str
from osbot_utils.type_safe.primitives.core.Safe_Int                 import Safe_Int
from osbot_utils.type_safe.primitives.core.Safe_Float               import Safe_Float
from osbot_utils.type_safe.type_safe_core.decorators.type_safe      import type_safe
from osbot_utils.type_safe.type_safe_core.shared.Type_Safe__Cache   import type_safe_cache


class Type_Safe__To__Json(Type_Safe):       # Converts Type_Safe classes to JSON Schema (draft-07 compatible)
    schema_cache     : Dict[Tuple[Type, bool], Dict[str, Any]]
    include_defaults : bool = True
    include_examples : bool = False
    strict_mode      : bool = False                                             # If True, includes all Type_Safe constraints

    # todo: the @type_safe here breaks some of the cache behaviour below since the @type_safe will
    #       convert the Dict to Type_Safe__Dict which means the returned objects are not the same (but from the cached value, so the performance implications might not be that big)
    #       (see if this has any side effects or main performance implications)
    @type_safe
    def convert_class(self, type_safe_class : Type[Type_Safe]        ,          # Type_Safe class to convert
                            title           : str             = None ,          # Optional schema title
                            description     : str             = None ,          # Optional schema description
                            is_nested       : bool            = False
                       ) -> Dict[str, Any]:                                     # Returns JSON Schema


        cache_key = (type_safe_class, is_nested)                                            # Create a cache key that includes whether it's nested

        if cache_key in self.schema_cache:
            return self.schema_cache[cache_key]

        if type_safe_class in self.schema_cache:                                            # Check cache first
            return self.schema_cache[type_safe_class]

        schema = { "type"                 : "object"                                  ,
                   "title"                : title or type_safe_class.__name__         ,
                   "additionalProperties" : False                                     }     # Type_Safe classes are strict

        if not is_nested:
            schema["$schema"] = "http://json-schema.org/draft-07/schema#"                   # Only add $schema for root level (non-nested) objects

        if description:
            schema["description"] = description

        properties = {}
        required   = []

        annotations = type_safe_cache.get_class_annotations(type_safe_class)
        cls_kwargs  = type_safe_class.__cls_kwargs__()

        for field_name, field_type in annotations:
            property_schema         = self.convert_field_type(field_type)
            properties[field_name] = property_schema

            if hasattr(type_safe_class, '__annotations_comments__'):                                # Add description from docstring if available
                comments = type_safe_class.__annotations_comments__
                if field_name in comments:
                    property_schema["description"] = comments[field_name]

            if field_name not in cls_kwargs:                                                        # Check if field is required (no default value)
                required.append(field_name)
            else:
                default_value = cls_kwargs[field_name]
                if self.include_defaults and default_value is not None:
                    if isinstance(default_value, (str, int, float, bool)):                          # Add default to schema if it's a simple type
                        property_schema["default"] = default_value

        schema["properties"] = properties
        if required:
            schema["required"] = required

        self.schema_cache[cache_key] = schema
        return schema

    @type_safe
    def convert_field_type(self, field_type : Any                               # Field type to convert
                           ) -> Dict[str, Any]:                                 # Returns JSON Schema for field

        origin = type_safe_cache.get_origin(field_type)

        if field_type is str:                                                   # Handle primitive types
            return {"type": "string"}
        elif field_type is int:
            return {"type": "integer"}
        elif field_type is float:
            return {"type": "number"}
        elif field_type is bool:
            return {"type": "boolean"}

        if isinstance(field_type, type) and issubclass(field_type, Type_Safe__Primitive):           # Handle Type_Safe__Primitive subclasses with their constraints
            schema = self.extract_primitive_schema(field_type)
            return schema

        if origin is list:                                                                          # Handle list/array types
            args = get_args(field_type)
            if args:
                return { "type"  : "array"                           ,
                        "items" : self.convert_field_type(args[0])   }
            return {"type": "array"}

        if origin is dict:
            args = get_args(field_type)                                                             # Handle dict/object types
            if len(args) == 2:
                return { "type"                 : "object"                      ,                   # JSON Schema doesn't support typed dict keys, so we use additionalProperties
                        "additionalProperties" : self.convert_field_type(args[1]) }
            return {"type": "object"}

        if origin is set:                                                                           # Handle set types (convert to array with uniqueItems)
            args = get_args(field_type)
            schema = { "type"        : "array" ,
                      "uniqueItems" : True      }
            if args:
                schema["items"] = self.convert_field_type(args[0])
            return schema

        if origin in (Union, Optional):                                         # Handle Union/Optional types
            args = get_args(field_type)

            if type(None) in args:                                                      # Special case for Optional (Union with None)
                non_none_args = [arg for arg in args if arg is not type(None)]
                if len(non_none_args) == 1:
                    schema            = self.convert_field_type(non_none_args[0])       # Optional single type
                    schema["nullable"] = True                                           # JSON Schema draft-07 style
                    return schema

            return { "oneOf": [self.convert_field_type(arg) for arg in args] }          # General Union case

        if isinstance(field_type, type) and issubclass(field_type, Type_Safe):          # This will register it in components_cache and return a $ref
            return self.convert_class(field_type, is_nested=True)                       # Call convert_class with is_nested=True for nested objects

        return {"type": "object"}                                                       # Default fallback

    @type_safe
    def extract_primitive_schema(self, primitive_class : Type[Type_Safe__Primitive]     # Primitive class to analyze
                                  ) -> Dict[str, Any]:                                  # Returns schema with constraints

        base_type = primitive_class.__primitive_base__

        if base_type is str:                                                            # Start with base type schema
            schema = {"type": "string"}
        elif base_type is int:
            schema = {"type": "integer"}
        elif base_type is float:
            schema = {"type": "number"}
        else:
            schema = {"type": "string"}                                                 # Default fallback

        if issubclass(primitive_class, Safe_Str):                                       # Extract constraints from Safe_Str types
            if hasattr(primitive_class, 'max_length'):
                schema['maxLength'] = primitive_class.max_length
            if hasattr(primitive_class, 'regex') and self.strict_mode:
                if hasattr(primitive_class.regex, 'pattern'):                           # Only include regex pattern in strict mode
                    schema['pattern'] = primitive_class.regex.pattern

        if issubclass(primitive_class, Safe_Int):                                       # Extract constraints from Safe_Int types
            if hasattr(primitive_class, 'min_value') and primitive_class.min_value is not None:
                schema['minimum'] = primitive_class.min_value
            if hasattr(primitive_class, 'max_value') and primitive_class.max_value is not None:
                schema['maximum'] = primitive_class.max_value

        if issubclass(primitive_class, Safe_Float):                                     # Extract constraints from Safe_Float types
            if hasattr(primitive_class, 'min_value') and primitive_class.min_value is not None:
                schema['minimum'] = primitive_class.min_value
            if hasattr(primitive_class, 'max_value') and primitive_class.max_value is not None:
                schema['maximum'] = primitive_class.max_value

        return schema

    @type_safe
    def convert_to_json_schema_string(self, type_safe_class : Type[Type_Safe]   # Class to convert
                                      ) -> str:                                 # Returns JSON Schema as string
        import json
        schema = self.convert_class(type_safe_class)
        return json.dumps(schema, indent=2)

    @type_safe
    def validate_against_schema(self, instance : Type_Safe         ,           # Instance to validate
                                      schema   : Dict[str, Any]                # Schema to validate against
                                ) -> bool:                                     # Returns True if valid  | Validate a Type_Safe instance against a JSON schema
        try:
            import jsonschema
            instance_data = instance.json()
            jsonschema.validate(instance_data, schema)
            return True
        except ImportError:
            raise ImportError("jsonschema package required for validation")
        except jsonschema.ValidationError:
            return False

type_safe__to__json = Type_Safe__To__Json()                                    # Singleton instance