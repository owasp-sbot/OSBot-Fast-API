from typing                                                  import Type, Dict, Any
from dataclasses                                             import is_dataclass
from osbot_utils.type_safe.type_safe_core.decorators.type_safe              import type_safe
from osbot_utils.type_safe.Type_Safe                         import Type_Safe
from osbot_fast_api.api.transformers.BaseModel__To__Type_Safe import basemodel__to__type_safe
from osbot_fast_api.api.transformers.Dataclass__To__BaseModel import dataclass__to__basemodel


class Dataclass__To__Type_Safe(Type_Safe):
    class_cache: Dict[Type, Type[Type_Safe]]                                             # Cache for generated Type_Safe classes

    @type_safe
    def convert_class(self, dataclass_type : Type                                        # Dataclass type to convert
                       ) -> Type[Type_Safe]:                                             # Returns Type_Safe class
        if not is_dataclass(dataclass_type):                                             # Validate it's a dataclass
            raise ValueError(f"Expected a dataclass, but got {dataclass_type}")

        if dataclass_type in self.class_cache:                                           # Check cache first
            return self.class_cache[dataclass_type]

        # Use composition: Dataclass → BaseModel → Type_Safe
        basemodel_class = dataclass__to__basemodel.convert_class(dataclass_type)         # Convert to BaseModel first
        type_safe_class = basemodel__to__type_safe.convert_class(basemodel_class)        # Then to Type_Safe

        # Rename to maintain consistent naming
        original_name = dataclass_type.__name__
        if original_name.endswith('__Dataclass'):
            original_name = original_name.replace('__Dataclass', '')
        if not original_name.endswith('__Type_Safe'):
            type_safe_class.__name__ = f"{original_name}__Type_Safe"

        self.class_cache[dataclass_type] = type_safe_class                               # Cache the result
        return type_safe_class

    @type_safe
    def convert_instance(self, dataclass_instance : Any                                  # Dataclass instance to convert
                        ) -> Type_Safe:                                                   # Returns Type_Safe instance
        if not is_dataclass(dataclass_instance):                                         # Validate it's a dataclass instance
            raise ValueError(f"Expected a dataclass instance, but got {type(dataclass_instance)}")

        # Use composition: Dataclass instance → BaseModel instance → Type_Safe instance
        basemodel_instance = dataclass__to__basemodel.convert_instance(dataclass_instance)  # Convert to BaseModel
        type_safe_instance = basemodel__to__type_safe.convert_instance(basemodel_instance)  # Then to Type_Safe

        return type_safe_instance


dataclass__to__type_safe = Dataclass__To__Type_Safe()                                    # Singleton instance for convenience