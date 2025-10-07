import inspect
from typing import get_type_hints, Callable, Type
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.Type_Safe__Primitive                                  import Type_Safe__Primitive
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                   import type_safe
from osbot_utils.type_safe.type_safe_core.shared.Type_Safe__Cache                import type_safe_cache
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id  import Safe_Str__Id
from osbot_fast_api.api.schemas.routes.Schema__Route__Parameter                  import Schema__Route__Parameter
from osbot_fast_api.api.schemas.routes.Schema__Route__Signature                  import Schema__Route__Signature



class Type_Safe__Route__Analyzer(Type_Safe):                            # Analyzes function signatures to extract type information for route creation

    @type_safe
    def analyze_function(self, function : Callable                       # Function to analyze
                          ) -> Schema__Route__Signature:                 # Returns complete signature analysis

        function_name = Safe_Str__Id(function.__name__)
        sig           = inspect.signature(function)
        type_hints    = get_type_hints(function)

        signature = Schema__Route__Signature(function_name = function_name)

        for param_name, param in sig.parameters.items():                 # Analyze each parameter
            if param_name == 'self':                                     # Skip self parameter
                continue

            param_info = self.analyze_parameter(param_name     = param_name  ,
                                                param          = param       ,
                                                type_hints     = type_hints  )

            signature.parameters.append(param_info)

            if param_info.is_primitive:                                  # Track conversion needs
                if param_name not in signature.primitive_conversions:
                    signature.primitive_conversions[param_name] = (param_info.param_type, param_info.primitive_base)

            elif param_info.is_type_safe:
                signature.has_body_params = True                         # Type_Safe objects go in body
                if param_info.requires_conversion:
                    # Will be populated by converter
                    pass

        return_type = type_hints.get('return', None)                                    # Analyze return type
        if return_type and return_type != inspect.Parameter.empty:
            if isinstance(return_type, (type, Type)):                   # Only set return_type if it's an actual class, not a typing construct
                signature.return_type             = return_type
                signature.return_needs_conversion = self.is_type_safe_class(return_type) and not self.is_primitive_class(return_type)

        return signature

    @type_safe
    def analyze_parameter(self, param_name  : str        ,               # Parameter name
                                param       : inspect.Parameter,         # Parameter object
                                type_hints  : dict                       # Type hints dict
                           ) -> Schema__Route__Parameter:                # Returns parameter analysis

        param_type = type_hints.get(param_name, inspect.Parameter.empty)

        param_info = Schema__Route__Parameter(name        = Safe_Str__Id(param_name),
                                              param_type = param_type               )

        if param.default != inspect.Parameter.empty:                     # Check for default value
            param_info.has_default    = True
            param_info.default_value  = param.default

        if self.is_primitive_class(param_type):                          # Check if Type_Safe__Primitive
            param_info.is_primitive       = True
            param_info.requires_conversion = True
            param_info.primitive_base     = self.get_primitive_base(param_type)

        elif self.is_type_safe_class(param_type):                        # Check if Type_Safe (non-primitive)
            param_info.is_type_safe        = True
            param_info.requires_conversion = True
            param_info.nested_primitive_fields = self.extract_primitive_fields(param_type)

        return param_info

    @type_safe
    def is_primitive_class(self, param_type                              # Type to check
                            ) -> bool:                                   # Returns True if Type_Safe__Primitive
        if param_type is None or param_type == inspect.Parameter.empty:
            return False
        try:
            if inspect.isclass(param_type):
                return issubclass(param_type, Type_Safe__Primitive)
        except:
            pass
        return False

    @type_safe
    def is_type_safe_class(self, param_type                              # Type to check
                            ) -> bool:                                   # Returns True if Type_Safe
        if param_type is None or param_type == inspect.Parameter.empty:
            return False
        try:
            if inspect.isclass(param_type):
                return issubclass(param_type, Type_Safe)
        except:
            pass
        return False

    @type_safe
    def get_primitive_base(self, primitive_class                         # Type_Safe__Primitive class
                            ):                                           # Returns base type (str, int, float)

        if hasattr(primitive_class, '__primitive_base__'):
            primitive_base = primitive_class.__primitive_base__
            if primitive_base:
                return primitive_base

        for base in primitive_class.__mro__:                             # Search MRO for primitive type
            if base in (str, int, float):
                return base

        return None

    @type_safe
    def extract_primitive_fields(self, type_safe_class                   # Type_Safe class to analyze
                                   ) -> dict:                            # Returns {field_name: primitive_class}

        primitive_fields = {}
        annotations      = type_safe_cache.get_class_annotations(type_safe_class)

        for field_name, field_type in annotations:
            if isinstance(field_type, type) and issubclass(field_type, Type_Safe__Primitive):
                primitive_fields[field_name] = field_type

        return primitive_fields if primitive_fields else None