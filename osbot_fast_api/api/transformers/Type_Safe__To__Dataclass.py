from typing                                                    import Type, Dict, Any
from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe
from osbot_utils.type_safe.Type_Safe                           import Type_Safe
from osbot_fast_api.api.transformers.BaseModel__To__Dataclass  import basemodel__to__dataclass
from osbot_fast_api.api.transformers.Type_Safe__To__BaseModel  import type_safe__to__basemodel


class Type_Safe__To__Dataclass(Type_Safe):
    class_cache: Dict[Type[Type_Safe], Type]                                             # Cache for generated dataclasses

    @type_safe
    def convert_class(self, type_safe_class : Type[Type_Safe]                            # Type_Safe class to convert
                       ) -> Type:                                                        # Returns dataclass type
        if type_safe_class in self.class_cache:                                          # Check cache first
            return self.class_cache[type_safe_class]

        # Use composition: Type_Safe → BaseModel → Dataclass
        basemodel_class = type_safe__to__basemodel.convert_class(type_safe_class)        # Convert to BaseModel first
        dataclass_type  = basemodel__to__dataclass.convert_class(basemodel_class)        # Then to dataclass

        # Rename to maintain consistent naming
        original_name = type_safe_class.__name__
        if not original_name.endswith('__Dataclass'):
            dataclass_type.__name__ = f"{original_name}__Dataclass"

        self.class_cache[type_safe_class] = dataclass_type                               # Cache the result
        return dataclass_type

    @type_safe
    def convert_instance(self, type_safe_instance : Type_Safe                            # Type_Safe instance to convert
                          ) -> Any:                                                      # Returns dataclass instance
        # Use composition: Type_Safe instance → BaseModel instance → Dataclass instance
        basemodel_instance = type_safe__to__basemodel.convert_instance(type_safe_instance)  # Convert to BaseModel
        dataclass_instance = basemodel__to__dataclass.convert_instance(basemodel_instance)  # Then to dataclass

        return dataclass_instance


type_safe__to__dataclass = Type_Safe__To__Dataclass()                                    # Singleton instance for convenience