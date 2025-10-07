import functools
import inspect
from typing                                                      import Callable
from fastapi                                                     import HTTPException
from fastapi.exceptions                                          import RequestValidationError
from osbot_utils.type_safe.Type_Safe                             import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe   import type_safe
from osbot_fast_api.api.routes.Type_Safe__Route__Converter       import Type_Safe__Route__Converter
from osbot_fast_api.api.schemas.routes.Schema__Route__Signature  import Schema__Route__Signature


class Type_Safe__Route__Wrapper(Type_Safe):                             # Creates wrapper functions that handle Type_Safe conversions for FastAPI routes
    converter : Type_Safe__Route__Converter

    @type_safe
    def create_wrapper(self, function  : Callable                       ,# Original function to wrap
                            signature  : Schema__Route__Signature       # Signature with conversion info
                         ) -> Callable:                                 # Returns wrapper function

        if not signature.primitive_conversions and not signature.type_safe_conversions and not signature.return_needs_conversion:
            return function                                              # No conversion needed - return original

        if signature.has_body_params:                                    # Different wrappers for different scenarios
            return self.create_body_wrapper(function, signature)
        else:
            return self.create_query_wrapper(function, signature)

    @type_safe
    def create_body_wrapper(self, function  : Callable                  ,# Function to wrap
                                 signature  : Schema__Route__Signature  # Signature info
                              ) -> Callable:                            # Returns wrapper for POST/PUT/DELETE routes

        @functools.wraps(function)
        def wrapper(**kwargs):
            converted_kwargs = {}                                        # Convert each parameter

            for param_name, param_value in kwargs.items():
                converted_value                = self.converter.convert_parameter_value(param_name, param_value, signature)
                converted_kwargs[param_name]   = converted_value

            try:                                                         # Execute original function
                result = function(**converted_kwargs)
            except HTTPException:
                raise                                                    # Re-raise HTTP exceptions
            except RequestValidationError:
                raise                                                    # Re-raise validation errors
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"{type(e).__name__}: {e}")

            return self.converter.convert_return_value(result, signature)# Convert return value

        new_params = self.build_wrapper_parameters(function, signature) # Update function signature for FastAPI
        wrapper.__signature__   = inspect.Signature(parameters=new_params)
        wrapper.__annotations__ = self.build_wrapper_annotations(function, signature)

        return wrapper

    @type_safe
    def create_query_wrapper(self, function  : Callable                 ,# Function to wrap
                                  signature  : Schema__Route__Signature # Signature info
                               ) -> Callable:                           # Returns wrapper for GET routes

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            converted_kwargs   = {}
            validation_errors  = []

            for param_name, param_value in kwargs.items():               # Convert parameters with validation error tracking
                try:
                    converted_value                = self.converter.convert_parameter_value(param_name, param_value, signature)
                    converted_kwargs[param_name]   = converted_value
                except (ValueError, TypeError) as e:
                    validation_errors.append({                           # Format as FastAPI validation error
                        'type' : 'value_error'  ,
                        'loc'  : ('query', param_name),
                        'msg'  : str(e)         ,
                        'input': param_value
                    })

            if validation_errors:                                        # Raise validation errors
                raise RequestValidationError(validation_errors)

            if args:                                                     # Call with positional args if present
                result = function(*args, **converted_kwargs)
            else:
                result = function(**converted_kwargs)

            return self.converter.convert_return_value(result, signature)# Convert return value

        new_params = self.build_wrapper_parameters(function, signature) # Update function signature
        wrapper.__signature__   = inspect.Signature(parameters=new_params)
        wrapper.__annotations__ = self.build_wrapper_annotations(function, signature)

        return wrapper

    @type_safe
    def build_wrapper_parameters(self, function  : Callable             ,# Original function
                                       signature  : Schema__Route__Signature# Signature info
                                  ):                                    # Returns list of inspect.Parameter

        sig        = inspect.signature(function)
        new_params = []

        for param in sig.parameters.values():
            if param.name == 'self':
                continue

            param_info = self.converter.find_parameter(signature, param.name)

            if param_info:
                if param_info.is_primitive:                              # Replace Type_Safe__Primitive with base type
                    new_param_type = param_info.primitive_base
                elif param_info.is_type_safe:                            # Replace Type_Safe with BaseModel
                    new_param_type = param_info.converted_type
                else:
                    new_param_type = param.annotation

                new_params.append(inspect.Parameter(
                    name       = param.name       ,
                    kind       = param.kind       ,
                    default    = param.default    ,
                    annotation = new_param_type
                ))
            else:
                new_params.append(param)                                 # Keep unchanged

        return new_params

    @type_safe
    def build_wrapper_annotations(self, function  : Callable            ,# Original function
                                        signature  : Schema__Route__Signature# Signature info
                                     ) -> dict:                         # Returns annotations dict

        from typing import get_type_hints

        type_hints  = get_type_hints(function)
        annotations = {}

        for param_name, param_type in type_hints.items():                # Update parameter annotations
            if param_name == 'return':
                continue

            param_info = self.converter.find_parameter(signature, param_name)

            if param_info:
                if param_info.is_primitive:
                    annotations[param_name] = param_info.primitive_base
                elif param_info.is_type_safe:
                    annotations[param_name] = param_info.converted_type
                else:
                    annotations[param_name] = param_type
            else:
                annotations[param_name] = param_type

        if signature.return_needs_conversion:                            # Update return annotation
            annotations['return'] = signature.return_converted_type
        elif 'return' in type_hints:
            annotations['return'] = type_hints['return']

        return annotations