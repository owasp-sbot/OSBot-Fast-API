from dataclasses                                         import fields, is_dataclass, asdict, Field, MISSING
from typing                                              import Type, Dict, Any, Optional, get_args, Union, List, Set, get_type_hints
from osbot_utils.type_safe.type_safe_core.decorators.type_safe          import type_safe
from pydantic                                            import BaseModel, Field as PydanticField, create_model
from osbot_utils.type_safe.Type_Safe                     import Type_Safe
from osbot_utils.type_safe.type_safe_core.shared.Type_Safe__Cache       import type_safe_cache


class Dataclass__To__BaseModel(Type_Safe):
    class_cache: Dict[Type, Type[BaseModel]]                                             # Cache for generated BaseModels

    @type_safe
    def convert_class(self, dataclass_type : Type                                        # Dataclass type to convert
                       ) -> Type[BaseModel]:                                             # Returns BaseModel class
        if not is_dataclass(dataclass_type):                                             # Validate it's a dataclass
            raise ValueError(f"Expected a dataclass, but got {dataclass_type}")

        if dataclass_type in self.class_cache:                                           # Check cache first
            return self.class_cache[dataclass_type]

        class_name = dataclass_type.__name__.replace('__Dataclass', '')                  # Generate class name
        if not class_name.endswith('__BaseModel'):                                       # Ensure proper naming
            class_name = f"{class_name}__BaseModel"

        pydantic_fields = {}                                                             # Build Pydantic fields
        type_hints      = get_type_hints(dataclass_type)                                 # Get type hints

        for field_info in fields(dataclass_type):                                        # Process each field
            field_name = field_info.name
            field_type = type_hints.get(field_name, Any)                                 # Get type from hints

            pydantic_type = self.convert_field_type(field_type)                          # Convert type annotation

            # Determine default value
            if field_info.default is not MISSING:                                        # Has default value
                pydantic_fields[field_name] = (pydantic_type, field_info.default)

            elif field_info.default_factory is not MISSING:                              # Has default factory
                # Pydantic Field with default_factory
                pydantic_fields[field_name] = (pydantic_type, PydanticField(default_factory=field_info.default_factory))

            else:                                                                         # Required field
                pydantic_fields[field_name] = (pydantic_type, PydanticField(...))

        # Create BaseModel dynamically
        basemodel_class = create_model(class_name          ,                             # Model name
                                      **pydantic_fields    ,                             # Fields with types
                                      __base__ = BaseModel )                             # Base class

        self.class_cache[dataclass_type] = basemodel_class                               # Cache the result
        return basemodel_class

    @type_safe
    def convert_instance(self, dataclass_instance : Any                                  # Dataclass instance to convert
                        ) -> BaseModel:                                                   # Returns BaseModel instance
        if not is_dataclass(dataclass_instance):                                        # Validate it's a dataclass instance
            raise ValueError(f"Expected a dataclass instance, but got {type(dataclass_instance)}")

        dataclass_type  = type(dataclass_instance)                                       # Get dataclass type
        basemodel_class = self.convert_class(dataclass_type)                             # Get or create BaseModel class

        instance_data = self.extract_dataclass_data(dataclass_instance)                  # Extract data from dataclass

        return basemodel_class(**instance_data)                                          # Create BaseModel instance

    def convert_field_type(self, dataclass_type : Any                                    # Dataclass type to convert
                          ) -> Any:                                                       # Returns Pydantic-compatible type
        origin = type_safe_cache.get_origin(dataclass_type)

        if origin is list:                                                               # Handle List types
            args = get_args(dataclass_type)
            if args:
                inner_type = self.convert_field_type(args[0])
                return List[inner_type]
            return list

        elif origin is dict:                                                             # Handle Dict types
            args = get_args(dataclass_type)
            if len(args) == 2:
                key_type   = self.convert_field_type(args[0])
                value_type = self.convert_field_type(args[1])
                return Dict[key_type, value_type]
            return dict

        elif origin is set:                                                              # Handle Set types
            args = get_args(dataclass_type)
            if args:
                inner_type = self.convert_field_type(args[0])
                return Set[inner_type]
            return set

        elif origin in (Union, Optional):                                                # Handle Union/Optional
            args           = get_args(dataclass_type)
            converted_args = tuple(self.convert_field_type(arg) for arg in args)
            if origin is Optional:
                return Optional[converted_args[0]]
            return Union[converted_args]

        if isinstance(dataclass_type, type) and is_dataclass(dataclass_type):            # Handle nested dataclass
            return self.convert_class(dataclass_type)                                    # Recursively convert

        return dataclass_type                                                            # Return standard types as-is

    def extract_dataclass_data(self, dataclass_instance : Any                            # Instance to extract from
                               ) -> Dict[str, Any]:                                       # Returns extracted data
        result = {}

        for field_info in fields(dataclass_instance):                                    # Iterate through fields
            field_name  = field_info.name
            field_value = getattr(dataclass_instance, field_name)                        # Get field value

            if field_value is None:                                                      # Preserve None values
                result[field_name] = None
            elif is_dataclass(field_value):                                              # Handle nested dataclass
                result[field_name] = self.convert_instance(field_value).model_dump()     # Convert to BaseModel
            elif isinstance(field_value, list):                                          # Handle lists
                result[field_name] = self.convert_list_value(field_value)
            elif isinstance(field_value, dict):                                          # Handle dicts
                result[field_name] = self.convert_dict_value(field_value)
            elif isinstance(field_value, set):                                           # Handle sets
                result[field_name] = self.convert_set_value(field_value)
            else:
                result[field_name] = field_value                                         # Simple values pass through

        return result

    def convert_list_value(self, field_value : list                                      # List value to convert
                          ) -> list:                                                      # Returns converted list
        result = []
        for item in field_value:
            if is_dataclass(item):                                                       # Nested dataclass in list
                result.append(self.convert_instance(item).model_dump())
            elif isinstance(item, list):                                                 # Nested list
                result.append(self.convert_list_value(item))
            elif isinstance(item, dict):                                                 # Nested dict
                result.append(self.convert_dict_value(item))
            else:
                result.append(item)
        return result

    def convert_dict_value(self, field_value : dict                                      # Dict value to convert
                          ) -> dict:                                                      # Returns converted dict
        result = {}
        for key, value in field_value.items():
            if is_dataclass(value):                                                      # Nested dataclass in dict
                result[key] = self.convert_instance(value).model_dump()
            elif isinstance(value, list):                                                # Nested list
                result[key] = self.convert_list_value(value)
            elif isinstance(value, dict):                                                # Nested dict
                result[key] = self.convert_dict_value(value)
            else:
                result[key] = value
        return result

    def convert_set_value(self, field_value : set                                        # Set value to convert
                         ) -> set:                                                        # Returns converted set
        result = set()
        for item in field_value:
            if is_dataclass(item):                                                       # Can't have dataclass in set
                raise ValueError("Cannot convert dataclass instances in sets to BaseModel")
            else:
                result.add(item)
        return result


dataclass__to__basemodel = Dataclass__To__BaseModel()                                    # Singleton instance for convenience