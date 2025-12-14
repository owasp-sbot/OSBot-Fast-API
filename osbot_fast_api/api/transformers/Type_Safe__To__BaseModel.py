from typing                                                           import Type, Dict, Any, Optional, get_args, Union, List
from osbot_utils.type_safe.Type_Safe__Primitive                       import Type_Safe__Primitive
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict import Type_Safe__Dict
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List import Type_Safe__List
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Set  import Type_Safe__Set
from osbot_utils.type_safe.type_safe_core.decorators.type_safe        import type_safe
from pydantic                                                         import BaseModel, Field, create_model
from osbot_utils.type_safe.Type_Safe                                  import Type_Safe
from osbot_utils.type_safe.type_safe_core.shared.Type_Safe__Cache     import type_safe_cache


class Type_Safe__To__BaseModel(Type_Safe):
    model_cache: Dict[Type, Type[BaseModel]]                                        # Cache for generated models

    @type_safe
    def convert_class(self, type_safe_class: Type[Type_Safe]                        # Type_Safe class to convert
                       ) -> Type[BaseModel]:                                        # Returns Pydantic BaseModel class
        if type_safe_class in self.model_cache:                                     # Check cache first
            return self.model_cache[type_safe_class]

        annotations     = type_safe_cache.get_class_annotations(type_safe_class)    # Get class annotations (using type_safe_cache)
        pydantic_fields = {}                                                        # Build Pydantic fields
        cls_kwargs      = type_safe_class.__cls_kwargs__()                          # Get class kwargs with defaults once

        for field_name, field_type in annotations:
            pydantic_type = self.convert_type(field_type)                           # Convert Type_Safe types to Pydantic
            has_default   = field_name in cls_kwargs                                # Check if field has any default (including None)

            if has_default:
                default_value = cls_kwargs[field_name]
                default_value = self.normalize_default_value(default_value)         # Normalize collections

                if default_value is None:                                           # Explicit None default - make Optional
                    pydantic_type = Optional[pydantic_type]
                    pydantic_fields[field_name] = (pydantic_type, None)
                else:
                    pydantic_fields[field_name] = (pydantic_type, default_value)
            else:                                                                   # No default - required field
                pydantic_fields[field_name] = (pydantic_type, Field(...))

        model_name = f"{type_safe_class.__name__}__BaseModel"                       # Generate model name
        base_model_class = create_model(model_name        ,                         # Create BaseModel dynamically
                                        **pydantic_fields ,
                                        __base__=BaseModel)

        if not hasattr(base_model_class, 'model_dump'):                             # Add model_dump() method for Pydantic v1 compatibility
            def model_dump(self):
                return self.dict()

            base_model_class.model_dump = model_dump
        self.model_cache[type_safe_class] = base_model_class                        # Add to cache
        return base_model_class

    @type_safe
    def convert_instance(self, type_safe_instance: Type_Safe                # Type_Safe instance to convert
                          ) -> BaseModel:                                   # Returns BaseModel instance
        base_model_class = self.convert_class(type(type_safe_instance))     # Get or create BaseModel class
        instance_data    = self.extract_instance_data(type_safe_instance)   # Get instance data
        return base_model_class(**instance_data)                            # Create and return BaseModel

    def convert_type(self, type_safe_type: Any                              # Type annotation to convert
                      ) -> Any:                                             # Returns Pydantic-compatible type
        origin = type_safe_cache.get_origin(type_safe_type)

        if origin is list:                                                  # Handle Type_Safe collection types
            args = get_args(type_safe_type)
            if args:
                inner_type = self.convert_type(args[0])
                return List[inner_type]
            return list

        elif origin is dict:
            args = get_args(type_safe_type)
            if len(args) == 2:
                key_type   = self.convert_type(args[0])
                value_type = self.convert_type(args[1])
                return Dict[key_type, value_type]
            return dict

        elif origin is set:
            args = get_args(type_safe_type)
            if args:
                inner_type = self.convert_type(args[0])
                return List[inner_type]                                     # Pydantic doesn't have Set, use List
            return list

        elif origin in (Union, Optional):
            args           = get_args(type_safe_type)
            converted_args = tuple(self.convert_type(arg) for arg in args)
            if origin is Optional:
                return Optional[converted_args[0]]
            return Union[converted_args]

        if isinstance(type_safe_type, type) and issubclass(type_safe_type, Type_Safe__Primitive):       # Type_Safe__Primitive should map to its base primitive type for Pydantic
            if type_safe_type.__primitive_base__:                                                       # if __primitive_base__ is set
                return type_safe_type.__primitive_base__                                                # return it


        if isinstance(type_safe_type, type) and issubclass(type_safe_type, Type_Safe):  # Handle Type_Safe classes
            return self.convert_class(type_safe_type)                                   # Recursively convert

        return type_safe_type                                                           # Return as-is for standard types

    def get_default_value(self, type_safe_class: Type[Type_Safe],                   # Class to get default from
                                field_name: str                                     # Field name to check
                           ) -> Any:                                                # Returns default value or None
        cls_kwargs = type_safe_class.__cls_kwargs__()                               # Get class kwargs with defaults

        if field_name in cls_kwargs:
            return self.normalize_default_value(cls_kwargs[field_name])

        return None


    def extract_instance_data(self, type_safe_instance: Type_Safe                       # Instance to extract data from
                               ) -> Dict[str, Any]:                                     # Returns dict of instance data
        data = {}
        instance_locals = type_safe_instance.__locals__()                               # Get all fields from instance

        for field_name, field_value in instance_locals.items():
            if isinstance(field_value, Type_Safe__Primitive):                           # Convert Type_Safe__Primitive to its base type value
                data[field_name] = field_value.__primitive_base__(field_value)
            elif isinstance(field_value, Type_Safe__List):                                # Convert Type_Safe collections
                data[field_name] = self.convert_list(field_value)
            elif isinstance(field_value, Type_Safe__Dict):
                data[field_name] = self.convert_dict(field_value)
            elif isinstance(field_value, Type_Safe__Set):
                data[field_name] = list(field_value)                                    # Convert to list for Pydantic
            elif isinstance(field_value, Type_Safe):
                data[field_name] = self.convert_instance(field_value).model_dump()      # Recursively convert nested
            else:
                data[field_name] = field_value

        return data

    def convert_list(self, type_safe_list: Type_Safe__List                              # List to convert
                      ) -> list:                                                        # Returns regular list
        result = []
        for item in type_safe_list:
            if isinstance(item, Type_Safe):
                result.append(self.convert_instance(item).dict())
            elif isinstance(item, Type_Safe__List):
                result.append(self.convert_list(item))
            elif isinstance(item, Type_Safe__Dict):
                result.append(self.convert_dict(item))
            else:
                result.append(item)
        return result

    def convert_dict(self, type_safe_dict: Type_Safe__Dict                              # Dict to convert
                      ) -> dict:                                                        # Returns regular dict
        result = {}
        for key, value in type_safe_dict.items():
            if isinstance(key, Type_Safe):                                              # Convert key if needed
                key = str(key)                                                          # Simple string conversion

            if isinstance(value, Type_Safe):                                            # Convert value
                result[key] = self.convert_instance(value).model_dump()
            elif isinstance(value, Type_Safe__List):
                result[key] = self.convert_list(value)
            elif isinstance(value, Type_Safe__Dict):
                result[key] = self.convert_dict(value)
            else:
                result[key] = value

        return result

    def normalize_default_value(self, value: Any                                   # Default value to normalize
                                  ) -> Any:                                         # Returns normalized value
        if isinstance(value, Type_Safe__List):                                      # Convert Type_Safe collections
            return list(value)
        elif isinstance(value, Type_Safe__Dict):
            return dict(value)
        elif isinstance(value, Type_Safe__Set):
            return list(value)                                                      # Convert set to list for Pydantic
        return value


type_safe__to__basemodel = Type_Safe__To__BaseModel()                                   # Singleton instance for convenience (and to have a more global model_cache)