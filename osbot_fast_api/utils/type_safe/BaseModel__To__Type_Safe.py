from typing                                                                     import Type, Dict, Any, Optional, get_args, Union, List
from osbot_utils.type_safe.Type_Safe__Primitive                                 import Type_Safe__Primitive
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from osbot_utils.type_safe.type_safe_core.shared.Type_Safe__Shared__Variables   import IMMUTABLE_TYPES
from pydantic                                                                   import BaseModel
from pydantic_core                                                              import PydanticUndefined
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.type_safe_core.shared.Type_Safe__Cache               import type_safe_cache


class BaseModel__To__Type_Safe(Type_Safe):
    class_cache: Dict[Type[BaseModel], Type[Type_Safe]]                                  # Cache for mapped classes

    @type_safe
    def convert_class(self, basemodel_class : Type[BaseModel]                            # BaseModel class to convert
                       ) -> Type[Type_Safe]:                                             # Returns Type_Safe class
        if basemodel_class in self.class_cache:                                          # Check cache first
            return self.class_cache[basemodel_class]

        class_name   = basemodel_class.__name__.replace('__BaseModel', '')               # Generate class name
        if not class_name.endswith('__Type_Safe'):                                       # Ensure proper naming
            class_name = f"{class_name}__Type_Safe"

        annotations = {}                                                                  # Build Type_Safe annotations
        defaults    = {}                                                                  # Build default values

        for field_name, field_info in basemodel_class.model_fields.items():              # Process each field
            type_safe_type = self.convert_field_type(field_info.annotation)              # Convert type annotation
            annotations[field_name] = type_safe_type

            # Only add immutable defaults to class definition. Mutable defaults will be handled during instance creation
            if field_info.default is not PydanticUndefined:                              # Has an actual default
                if self.is_immutable_default(field_info.default):                        # Only immutable defaults
                    defaults[field_name] = field_info.default
                elif field_info.default is None:                                         # Explicit None is ok
                    defaults[field_name] = None
                else:
                    pass                                                                 # Skip mutable defaults like lists, dicts, sets
            elif field_info.default_factory is not None:                                 # Default factories
                pass                                                                     # Don't add to class defaults, will handle in instance creation

        type_safe_class = type(class_name           ,                                    # Create Type_Safe class
                               (Type_Safe,)         ,                                    # Base class
                               {**defaults          ,                                    # Only immutable defaults
                                '__annotations__': annotations})

        self.class_cache[basemodel_class] = type_safe_class                              # Cache the result
        return type_safe_class

    @type_safe
    def convert_instance(self, basemodel_instance : BaseModel                            # BaseModel instance to convert
                          ) -> Type_Safe:                                                # Returns Type_Safe instance
        basemodel_class = type(basemodel_instance)                                       # Get BaseModel class
        type_safe_class = self.convert_class(basemodel_class)                            # Get or create Type_Safe class

        instance_data = self.extract_basemodel_data(basemodel_instance)                  # Extract data from BaseModel

        constructor_args = {}                                                            # Separate data into constructor args and post-init assignments
        post_init_data   = {}

        for field_name, field_value in instance_data.items():
            if self.is_safe_for_constructor(field_value):                                # Simple types go to constructor
                constructor_args[field_name] = field_value
            else:                                                                        # Complex types set after init
                post_init_data[field_name] = field_value

        instance = type_safe_class(**constructor_args)                                   # Create instance with safe constructor args

        for field_name, field_value in post_init_data.items():                           # Set complex fields after initialization
            setattr(instance, field_name, field_value)

        return instance

    def is_immutable_default(self, value : Any                                           # Value to check
                            ) -> bool:                                                   # Returns True if immutable
        """Check if a value is safe to use as a class-level default in Type_Safe."""
        if value is None:
            return True
        if type(value) in IMMUTABLE_TYPES:
            return True
        if isinstance(value, IMMUTABLE_TYPES):
            return True
        return False

    def is_safe_for_constructor(self, value : Any                                        # Value to check
                                 ) -> bool:                                              # Returns True if safe
        """Check if a value is safe to pass to Type_Safe constructor."""
        if value is None:
            return True
        if isinstance(value, (str, int, float, bool, bytes)):                            # Primitives are safe
            return True
        if isinstance(value, Type_Safe):                                                 # Type_Safe instances ok
            return True
        return False                                                                     # Lists, dicts, sets not safe

    def convert_field_type(self, pydantic_type : Any                                     # Pydantic type to convert
                            ) -> Any:                                                    # Returns Type_Safe compatible type
        origin = type_safe_cache.get_origin(pydantic_type)

        if origin is list:                                                               # Handle List types
            args = get_args(pydantic_type)
            if args:
                inner_type = self.convert_field_type(args[0])
                return list[inner_type]                                                  # this has to be list (not List) , since with List we get: 'Type List cannot be instantiated; use list() instead'
            return list

        elif origin is dict:                                                             # Handle Dict types
            args = get_args(pydantic_type)
            if len(args) == 2:
                key_type   = self.convert_field_type(args[0])
                value_type = self.convert_field_type(args[1])
                return Dict[key_type, value_type]
            return dict

        elif origin is set:                                                              # Handle Set types
            args = get_args(pydantic_type)
            if args:
                inner_type = self.convert_field_type(args[0])
                from typing import Set
                return Set[inner_type]
            return set

        elif origin in (Union, Optional):                                                # Handle Union/Optional
            args           = get_args(pydantic_type)
            converted_args = tuple(self.convert_field_type(arg) for arg in args)
            if origin is Optional:
                return Optional[converted_args[0]]
            return Union[converted_args]

        if isinstance(pydantic_type, type) and issubclass(pydantic_type, BaseModel):     # Handle nested BaseModel
            return self.convert_class(pydantic_type)                                     # Recursively convert

        return pydantic_type                                                             # Return standard types as-is

    def extract_basemodel_data(self, basemodel_instance : BaseModel                      # Instance to extract from
                                ) -> Dict[str, Any]:                                     # Returns extracted data
        data = basemodel_instance.model_dump()                                           # Get all data as dict

        result = {}
        for field_name, field_value in data.items():
            if field_value is None:                                                      # Skip None values
                result[field_name] = None
            elif isinstance(field_value, dict):                                                             # Handle dict fields
                result[field_name] = self.convert_dict_field(basemodel_instance, field_name, field_value)
            elif isinstance(field_value, list):                                                             # Handle list fields
                result[field_name] = self.convert_list_field(basemodel_instance, field_name, field_value)
            elif isinstance(field_value, set):                                                              # Handle set fields
                result[field_name] = self.convert_set_field(basemodel_instance, field_name, field_value)
            else:
                result[field_name] = self.convert_value(field_value)                                        # Convert simple values

        return result

    def convert_dict_field(self, basemodel_instance : BaseModel ,                       # Parent instance
                                 field_name         : str        ,                      # Field name
                                 field_value        : dict                              # Dict value to convert
                            ) -> Any:                                                   # Returns converted dict
        field_info = basemodel_instance.model_fields.get(field_name)                    # Get field metadata
        if not field_info:
            return field_value

        origin = type_safe_cache.get_origin(field_info.annotation)
        if origin is dict:                                                               # It's a typed dict
            args = get_args(field_info.annotation)
            if len(args) == 2:
                key_type, value_type = args
                result = {}
                for k, v in field_value.items():
                    converted_key   = self.convert_value(k)
                    converted_value = self.convert_nested_value(v, value_type)
                    result[converted_key] = converted_value
                return result

        return field_value                                                               # Return as-is if not typed

    def convert_list_field(self, basemodel_instance : BaseModel ,                        # Parent instance
                                 field_name          : str        ,                      # Field name
                                 field_value         : list                              # List value to convert
                            ) -> Any:                                                    # Returns converted list
        field_info = basemodel_instance.model_fields.get(field_name)                     # Get field metadata
        if not field_info:
            return field_value

        origin = type_safe_cache.get_origin(field_info.annotation)
        if origin is list:                                                               # It's a typed list
            args = get_args(field_info.annotation)
            if args:
                item_type = args[0]
                result = []
                for item in field_value:
                    converted_item = self.convert_nested_value(item, item_type)
                    result.append(converted_item)
                return result

        return field_value                                                               # Return as-is if not typed

    def convert_set_field(self, basemodel_instance : BaseModel ,                         # Parent instance
                                field_name          : str        ,                       # Field name
                                field_value         : set                                # Set value to convert
                           ) -> Any:                                                     # Returns converted set
        field_info = basemodel_instance.model_fields.get(field_name)                     # Get field metadata
        if not field_info:
            return field_value

        origin = type_safe_cache.get_origin(field_info.annotation)
        if origin is set:                                                                # It's a typed set
            args = get_args(field_info.annotation)
            if args:
                item_type = args[0]
                result = set()
                for item in field_value:
                    converted_item = self.convert_nested_value(item, item_type)
                    result.add(converted_item)
                return result

        return field_value                                                               # Return as-is if not typed

    def convert_nested_value(self, value     : Any ,                                     # Value to convert
                                   expected_type : Any                                   # Expected type hint
                              ) -> Any:                                                  # Returns converted value
        if value is None:
            return None

        if isinstance(expected_type, type) and issubclass(expected_type, Type_Safe__Primitive):
            return expected_type(value)                                                  # Create Type_Safe__Primitive instance

        if isinstance(expected_type, type) and issubclass(expected_type, BaseModel):     # Nested BaseModel
            if isinstance(value, dict):                                                  # Dict representation
                nested_model = expected_type(**value)                                    # Create BaseModel instance
                return self.convert_instance(nested_model)                               # Convert to Type_Safe
            elif isinstance(value, BaseModel):                                           # Already BaseModel
                return self.convert_instance(value)

        if isinstance(value, dict):                                                      # Nested dict
            origin = type_safe_cache.get_origin(expected_type)
            if origin is dict:
                args = get_args(expected_type)
                if len(args) == 2:
                    key_type, value_type = args
                    result = {}
                    for k, v in value.items():
                        result[k] = self.convert_nested_value(v, value_type)
                    return result

        if isinstance(value, list):                                                      # Nested list
            origin = type_safe_cache.get_origin(expected_type)
            if origin is list:
                args = get_args(expected_type)
                if args:
                    item_type = args[0]
                    return [self.convert_nested_value(item, item_type) for item in value]

        return self.convert_value(value)                                                 # Simple value

    def convert_value(self, value : Any                                                  # Value to convert
                       ) -> Any:                                                         # Returns converted value
        if isinstance(value, BaseModel):                                                 # BaseModel instance
            return self.convert_instance(value)
        elif isinstance(value, dict):                                                    # Dict that might be BaseModel data
            if '_type' in value or '__class__' in value:                                 # Looks like serialized object
                return value                                                             # Let Type_Safe handle it
        return value                                                                     # Return simple values as-is


basemodel__to__type_safe = BaseModel__To__Type_Safe()                                    # Singleton instance for convenience