from dataclasses                                         import dataclass, field, make_dataclass, Field, MISSING
from typing                                              import Type, Dict, Any, Optional, get_args, Union, List, Set
from osbot_utils.type_safe.type_safe_core.decorators.type_safe          import type_safe
from pydantic                                            import BaseModel
from pydantic_core                                       import PydanticUndefined
from osbot_utils.type_safe.Type_Safe                     import Type_Safe
from osbot_utils.type_safe.type_safe_core.shared.Type_Safe__Cache       import type_safe_cache


class BaseModel__To__Dataclass(Type_Safe):
    class_cache: Dict[Type[BaseModel], Type]                                             # Cache for generated dataclasses

    @type_safe
    def convert_class(self, basemodel_class : Type[BaseModel]                            # BaseModel class to convert
                       ) -> Type:                                                        # Returns dataclass type
        if basemodel_class in self.class_cache:                                          # Check cache first
            return self.class_cache[basemodel_class]

        class_name = basemodel_class.__name__.replace('__BaseModel', '')                 # Generate class name
        if not class_name.endswith('__Dataclass'):                                       # Ensure proper naming
            class_name = f"{class_name}__Dataclass"

        fields_list = []                                                                 # Build dataclass fields

        for field_name, field_info in basemodel_class.model_fields.items():              # Process each field
            field_type = self.convert_field_type(field_info.annotation)                  # Convert type annotation

            # Determine default value
            if field_info.default is not PydanticUndefined:                              # Has an actual default
                default_value = field_info.default

                # Check if default is mutable and needs default_factory
                if self.is_mutable_default(default_value):                               # Mutable defaults need factory
                    if isinstance(default_value, list):
                        fields_list.append((field_name, field_type, field(default_factory=list)))
                    elif isinstance(default_value, dict):
                        fields_list.append((field_name, field_type, field(default_factory=dict)))
                    elif isinstance(default_value, set):
                        fields_list.append((field_name, field_type, field(default_factory=set)))
                    else:
                        # Other mutable types - create lambda
                        fields_list.append((field_name, field_type, field(default_factory=lambda v=default_value: v.copy())))
                elif default_value is None:                                              # Explicit None
                    fields_list.append((field_name, field_type, field(default=None)))
                else:                                                                    # Immutable default
                    fields_list.append((field_name, field_type, field(default=default_value)))

            elif field_info.default_factory is not None:                                 # Has default factory
                # Use the existing default_factory
                fields_list.append((field_name, field_type, field(default_factory=field_info.default_factory)))

            else:                                                                         # Required field (no default)
                fields_list.append((field_name, field_type))

        # Create dataclass dynamically
        dataclass_type = make_dataclass(class_name     ,                                 # Class name
                                        fields_list    ,                                 # Fields with types
                                        frozen = False ,                                 # Mutable by default
                                        eq     = True  ,                                 # Enable equality
                                        repr   = True  )                                 # Enable repr

        self.class_cache[basemodel_class] = dataclass_type                               # Cache the result
        return dataclass_type

    @type_safe
    def convert_instance(self, basemodel_instance : BaseModel                            # BaseModel instance to convert
                          ) -> Any:                                                      # Returns dataclass instance
        basemodel_class = type(basemodel_instance)                                       # Get BaseModel class
        dataclass_type  = self.convert_class(basemodel_class)                            # Get or create dataclass
        instance_data   = self.extract_basemodel_data(basemodel_instance)                # Extract data from BaseModel


        try:                                                                             # Create dataclass instance
            return dataclass_type(**instance_data)                                       # Direct instantiation
        except TypeError as e:
            # Handle any type mismatches by filtering to valid fields
            valid_fields = {f.name for f in dataclass_type.__dataclass_fields__.values()}
            filtered_data = {k: v for k, v in instance_data.items() if k in valid_fields}
            return dataclass_type(**filtered_data)

    def convert_field_type(self, pydantic_type : Any                                     # Pydantic type to convert
                            ) -> Any:                                                    # Returns dataclass-compatible type
        origin = type_safe_cache.get_origin(pydantic_type)

        if origin is list:                                                               # Handle List types
            args = get_args(pydantic_type)
            if args:
                inner_type = self.convert_field_type(args[0])
                return List[inner_type]
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
                return Set[inner_type]
            return set

        elif origin in (Union, Optional):                                                # Handle Union/Optional
            args           = get_args(pydantic_type)
            converted_args = tuple(self.convert_field_type(arg) for arg in args)
            if origin is Optional:
                return Optional[converted_args[0]]
            return Union[converted_args]

        if isinstance(pydantic_type, type) and issubclass(pydantic_type, BaseModel):     # Handle nested BaseModel
            return self.convert_class(pydantic_type)                                     # Recursively convert to dataclass

        return pydantic_type                                                             # Return standard types as-is

    def extract_basemodel_data(self, basemodel_instance : BaseModel                      # Instance to extract from
                           ) -> Dict[str, Any]:                                          # Returns extracted data
        result = {}

        for field_name, field_info in basemodel_instance.model_fields.items():           # Iterate through fields
            field_value = getattr(basemodel_instance, field_name)                        # Get actual value (not dumped)

            if field_value is None:                                                      # Preserve None values
                result[field_name] = None
            elif isinstance(field_value, BaseModel):                                     # Handle nested BaseModel
                result[field_name] = self.convert_instance(field_value)                  # Convert to dataclass
            elif isinstance(field_value, dict):                                                             # Handle dicts
                result[field_name] = self.convert_dict_value(basemodel_instance, field_name, field_value)
            elif isinstance(field_value, list):                                                             # Handle lists
                result[field_name] = self.convert_list_value(basemodel_instance, field_name, field_value)
            elif isinstance(field_value, set):                                                              # Handle sets
                result[field_name] = self.convert_set_value(basemodel_instance, field_name, field_value)
            else:
                result[field_name] = field_value                                         # Simple values pass through

        return result

    def convert_dict_value(self, basemodel_instance : BaseModel ,                        # Parent instance
                                 field_name         : str        ,                       # Field name
                                 field_value        : dict                               # Dict value to convert
                            ) -> dict:                                                   # Returns converted dict
        field_info = basemodel_instance.model_fields.get(field_name)                     # Get field metadata
        if not field_info:
            return field_value

        origin = type_safe_cache.get_origin(field_info.annotation)
        if origin is dict:                                                               # Typed dict
            args = get_args(field_info.annotation)
            if len(args) == 2:
                value_type = args[1]
                result = {}
                for k, v in field_value.items():
                    result[k] = self.convert_nested_value(v, value_type)
                return result

        return field_value

    def convert_list_value(self, basemodel_instance : BaseModel ,                        # Parent instance
                                 field_name          : str        ,                      # Field name
                                 field_value         : list                              # List value to convert
                            ) -> list:                                                   # Returns converted list
        field_info = basemodel_instance.model_fields.get(field_name)                     # Get field metadata
        if not field_info:
            return field_value

        origin = type_safe_cache.get_origin(field_info.annotation)
        if origin is list:                                                               # Typed list
            args = get_args(field_info.annotation)
            if args:
                item_type = args[0]
                result = []
                for item in field_value:
                    result.append(self.convert_nested_value(item, item_type))
                return result

        return field_value

    def convert_set_value(self, basemodel_instance : BaseModel ,                         # Parent instance
                                field_name          : str        ,                       # Field name
                                field_value         : set                                # Set value to convert
                           ) -> set:                                                     # Returns converted set
        field_info = basemodel_instance.model_fields.get(field_name)                     # Get field metadata
        if not field_info:
            return field_value

        origin = type_safe_cache.get_origin(field_info.annotation)
        if origin is set:                                                                # Typed set
            args = get_args(field_info.annotation)
            if args:
                item_type = args[0]
                result = set()
                for item in field_value:
                    result.add(self.convert_nested_value(item, item_type))
                return result

        return field_value

    def convert_nested_value(self, value         : Any ,                                 # Value to convert
                                   expected_type : Any                                   # Expected type hint
                              ) -> Any:                                                  # Returns converted value
        if value is None:
            return None

        if isinstance(expected_type, type) and issubclass(expected_type, BaseModel):     # Nested BaseModel
            if isinstance(value, dict):                                                  # Dict representation
                nested_model = expected_type(**value)                                    # Create BaseModel
                return self.convert_instance(nested_model)                               # Convert to dataclass
            elif isinstance(value, BaseModel):                                           # Already BaseModel
                return self.convert_instance(value)

        if isinstance(value, dict):                                                      # Nested dict
            origin = type_safe_cache.get_origin(expected_type)
            if origin is dict:
                args = get_args(expected_type)
                if len(args) == 2:
                    value_type = args[1]
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

        return value                                                                     # Return simple values as-is

    def is_mutable_default(self, value : Any                                             # Value to check
                            ) -> bool:                                                   # Returns True if mutable
        """Check if a default value is mutable and needs default_factory."""
        if value is None:
            return False
        return isinstance(value, (list, dict, set))                                      # Common mutable types

basemodel__to__dataclass = BaseModel__To__Dataclass()                                    # Singleton instance for convenience