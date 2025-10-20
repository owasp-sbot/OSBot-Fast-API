import functools
import inspect
from typing                                                          import Callable, get_type_hints
from fastapi                                                         import HTTPException
from fastapi.exceptions                                              import RequestValidationError
from osbot_utils.type_safe.Type_Safe                                 import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe       import type_safe
from osbot_fast_api.api.routes.type_safe.Type_Safe__Route__Converter import Type_Safe__Route__Converter
from osbot_fast_api.api.schemas.routes.Schema__Route__Signature      import Schema__Route__Signature


class Type_Safe__Route__Wrapper(Type_Safe):                             # Creates wrapper functions that handle Type_Safe conversions for FastAPI routes
    converter : Type_Safe__Route__Converter

    @type_safe
    def create_wrapper(self, function  : Callable                 ,         # Original function to wrap
                             signature : Schema__Route__Signature           # Signature with conversion info
                        ) -> Callable:                                      # Returns wrapper function

        if not signature.primitive_conversions and not signature.type_safe_conversions and not signature.return_needs_conversion:
            if signature.return_type is not None:                                           # Even if no conversions needed, preserve return type for OpenAPI
                return self.create_passthrough_wrapper(function, signature)                 # Create minimal wrapper that preserves return type annotation
            return function                                                                 # No return type - return original

        if signature.has_body_params:                                                   # Different wrappers for different scenarios
            wrapper_function = self.create_body_wrapper(function, signature)
        else:
            wrapper_function = self.create_query_wrapper(function, signature)

        if signature.return_type is not None:
            wrapper_function.__original_return_type__ = signature.return_type           # Preserve original return type metadata for route extractors

        if hasattr(function, '__route_path__'):                                         # Also preserve route_path decorator if it exists
            wrapper_function.__route_path__ = function.__route_path__

        if signature.type_safe_conversions or signature.primitive_conversions:
            wrapper_function.__original_param_types__ = {}
            for param_info in signature.parameters:
                wrapper_function.__original_param_types__[str(param_info.name)] = param_info.param_type


        return wrapper_function

    @type_safe
    def create_passthrough_wrapper(self, function  : Callable                ,     # Function to wrap
                                         signature : Schema__Route__Signature      # Signature info
                                    ) -> Callable:                                 # Returns minimal wrapper that preserves annotations

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)                                        # Simply pass through to the original function

        wrapper.__signature__ = inspect.signature(function)                         # Preserve the original signature

        try:                                                                        # Build annotations dict including the return type
            type_hints              = get_type_hints(function)
            wrapper.__annotations__ = type_hints.copy()
        except:
            wrapper.__annotations__ = getattr(function, '__annotations__', {}).copy()   # Fallback to __annotations__ if get_type_hints fails

        if signature.return_type is not None and 'return' not in wrapper.__annotations__:  # Ensure return type is set
            wrapper.__annotations__['return'] = signature.return_type

        wrapper.__original_return_type__ = signature.return_type                    # Preserve original return type metadata

        if hasattr(function, '__route_path__'):                                     # Preserve route_path decorator if it exists
            wrapper.__route_path__ = function.__route_path__

        return wrapper

    @type_safe
    def create_body_wrapper(self, function  : Callable                ,     # Function to wrap
                                  signature : Schema__Route__Signature      # Signature info
                             ) -> Callable:                                 # Returns wrapper for POST/PUT/DELETE routes

        @functools.wraps(function)
        def wrapper(**kwargs):
            converted_kwargs = {}                                           # Convert each parameter

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

        new_params              = self.build_wrapper_parameters(function, signature)            # Update function signature for FastAPI
        wrapper.__signature__   = inspect.Signature(parameters=new_params)
        wrapper.__annotations__ = self.build_wrapper_annotations(function, signature)

        return wrapper

    @type_safe
    def create_query_wrapper(self, function  : Callable                 ,       # Function to wrap
                                   signature  : Schema__Route__Signature        # Signature info
                              ) -> Callable:                                    # Returns wrapper for GET routes

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            converted_kwargs   = {}
            validation_errors  = []

            for param_name, param_value in kwargs.items():                      # Convert parameters with validation error tracking
                try:
                    converted_value                = self.converter.convert_parameter_value(param_name, param_value, signature)
                    converted_kwargs[param_name]   = converted_value
                except (ValueError, TypeError) as e:
                    validation_errors.append({ 'type' : 'value_error'        ,              # Format as FastAPI validation error
                                               'loc'  : ('query', param_name),
                                               'msg'  : str(e)               ,
                                               'input': param_value          })

            if validation_errors:                                               # Raise validation errors
                raise RequestValidationError(validation_errors)

            if args:                                                            # Call with positional args if present
                result = function(*args, **converted_kwargs)
            else:
                result = function(**converted_kwargs)

            return self.converter.convert_return_value(result, signature)# Convert return value

        new_params              = self.build_wrapper_parameters(function, signature)        # Update function signature
        wrapper.__signature__   = inspect.Signature(parameters=new_params)
        wrapper.__annotations__ = self.build_wrapper_annotations(function, signature)

        return wrapper

    @type_safe
    def build_wrapper_parameters(self, function  : Callable                 ,       # Original function
                                       signature  : Schema__Route__Signature        # Signature info
                                       ):                                           # Returns list of inspect.Parameter

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

                new_params.append(inspect.Parameter(name       = param.name       ,
                                                    kind       = param.kind       ,
                                                    default    = param.default    ,
                                                    annotation = new_param_type))
            else:
                new_params.append(param)                                 # Keep unchanged

        return new_params

    @type_safe
    def build_wrapper_annotations(self, function  : Callable                 ,  # Original function
                                        signature  : Schema__Route__Signature   # Signature info
                                   ) -> dict:                                   # Returns annotations dict

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