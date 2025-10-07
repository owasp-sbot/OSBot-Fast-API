
from osbot_utils.type_safe.Type_Safe                              import Type_Safe
from osbot_utils.type_safe.Type_Safe__Primitive                   import Type_Safe__Primitive
from osbot_utils.type_safe.type_safe_core.decorators.type_safe    import type_safe
from osbot_fast_api.api.transformers.Type_Safe__To__BaseModel     import type_safe__to__basemodel
from osbot_fast_api.api.schemas.routes.Schema__Route__Signature   import Schema__Route__Signature


class Type_Safe__Route__Converter(Type_Safe):                           # Handles conversion between Type_Safe and BaseModel for FastAPI routes

    @type_safe
    def enrich_signature_with_conversions(self, signature : Schema__Route__Signature  # Signature to enrich
                                            ) -> Schema__Route__Signature:            # Returns enriched signature

        for param_info in signature.parameters:                          # Convert Type_Safe classes to BaseModel
            if param_info.is_type_safe and not param_info.is_primitive:
                basemodel_class              = type_safe__to__basemodel.convert_class(param_info.param_type)
                param_info.converted_type    = basemodel_class
                param_name                   = str(param_info.name)

                signature.type_safe_conversions[param_name] = (param_info.param_type, basemodel_class)

        if signature.return_needs_conversion:                            # Convert return type to BaseModel
            basemodel_return                   = type_safe__to__basemodel.convert_class(signature.return_type)
            signature.return_converted_type    = basemodel_return

        return signature

    @type_safe
    def convert_parameter_value(self, param_name  : str                 ,# Parameter name
                                      param_value                        ,# Value to convert
                                      signature   : Schema__Route__Signature# Signature with conversion info
                                 ):                                      # Returns converted value

        if param_name in signature.primitive_conversions:                # Handle Type_Safe__Primitive conversion
            type_safe_primitive_class, _ = signature.primitive_conversions[param_name]
            return type_safe_primitive_class(param_value)

        elif param_name in signature.type_safe_conversions:              # Handle Type_Safe class conversion
            type_safe_class, _ = signature.type_safe_conversions[param_name]

            if isinstance(param_value, dict):                            # From JSON dict
                param_info = self.find_parameter(signature, param_name)
                if param_info and param_info.nested_primitive_fields:    # Convert nested primitive fields
                    for field_name, primitive_class in param_info.nested_primitive_fields.items():
                        if field_name in param_value:
                            param_value[field_name] = primitive_class(param_value[field_name])

                return type_safe_class(**param_value)

            else:                                                        # From BaseModel instance
                data = param_value.model_dump()
                param_info = self.find_parameter(signature, param_name)
                if param_info and param_info.nested_primitive_fields:    # Convert nested primitive fields
                    for field_name, primitive_class in param_info.nested_primitive_fields.items():
                        if field_name in data:
                            data[field_name] = primitive_class(data[field_name])

                return type_safe_class(**data)

        return param_value                                               # No conversion needed

    @type_safe
    def convert_return_value(self, result                                ,# Return value to convert
                                  signature : Schema__Route__Signature  # Signature with conversion info
                              ):                                         # Returns converted value

        if signature.return_needs_conversion and isinstance(result, Type_Safe):
            return type_safe__to__basemodel.convert_instance(result).model_dump()

        if isinstance(result, Type_Safe__Primitive):                     # Convert primitive to base type
            primitive_base = result.__primitive_base__ or type(result).__bases__[0]
            return primitive_base(result)

        return result                                                    # No conversion needed

    @type_safe
    def find_parameter(self, signature   : Schema__Route__Signature    ,# Signature to search
                            param_name   : str                          # Parameter name to find
                        ):                                              # Returns Schema__Route__Parameter or None

        for param_info in signature.parameters:
            if str(param_info.name) == param_name:
                return param_info
        return None