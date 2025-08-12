import functools
import inspect
from typing                                     import get_type_hints
from fastapi                                    import APIRouter, FastAPI
from osbot_utils.type_safe.Type_Safe            import Type_Safe
from osbot_utils.decorators.lists.index_by      import index_by
from osbot_utils.type_safe.Type_Safe__Primitive import Type_Safe__Primitive
from fastapi.exceptions                         import RequestValidationError
from osbot_utils.utils.Dev import pprint
from pydantic_core                              import ErrorDetails

from osbot_fast_api.utils.type_safe.BaseModel__To__Type_Safe import basemodel__to__type_safe
from osbot_fast_api.utils.type_safe.Type_Safe__To__BaseModel import type_safe__to__basemodel


class Fast_API_Routes(Type_Safe):       # refactor to Fast_API__Routes
    router : APIRouter
    app    : FastAPI = None
    prefix : str
    tag    : str

    def __init__(self, **kwargs):
        from osbot_utils.utils.Str import str_safe
        from osbot_utils.utils.Misc import lower

        super().__init__(**kwargs)
        self.prefix = f'/{lower(str_safe(self.tag))}'

    def add_route(self,function, methods):
        path = self.parse_function_name(function.__name__)
        self.router.add_api_route(path=path, endpoint=function, methods=methods)
        return self

    def add_route_with_body(self, function, methods):
        sig        = inspect.signature(function)
        type_hints = get_type_hints(function)

        # Find Type_Safe parameters and convert them to BaseModel classes
        type_safe_conversions = {}

        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            param_type = type_hints.get(param_name)
            if param_type and inspect.isclass(param_type):
                if issubclass(param_type, Type_Safe) and not issubclass(param_type, Type_Safe__Primitive):
                    basemodel_class = type_safe__to__basemodel.convert_class(param_type)
                    type_safe_conversions[param_name] = (param_type, basemodel_class)

        if type_safe_conversions:
            @functools.wraps(function)
            def wrapper(**kwargs):
                converted_kwargs = {}
                for param_name, param_value in kwargs.items():
                    if param_name in type_safe_conversions:
                        type_safe_class, _ = type_safe_conversions[param_name]
                        if isinstance(param_value, dict):
                            converted_kwargs[param_name] = type_safe_class(**param_value)
                        else:
                            data = param_value.model_dump()                         # Get the data from BaseModel
                            converted_kwargs[param_name] = type_safe_class(**data)  # Create instance of original Type_Safe class
                    else:
                        converted_kwargs[param_name] = param_value

                result = function(**converted_kwargs)

                if isinstance(result, Type_Safe):
                    return type_safe__to__basemodel.convert_instance(result).model_dump()
                return result

            # Build new parameters with BaseModel types
            new_params = []
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                if param_name in type_safe_conversions:
                    _, basemodel_class = type_safe_conversions[param_name]
                    new_params.append(inspect.Parameter(
                        name=param_name,
                        kind=param.kind,
                        default=param.default,
                        annotation=basemodel_class
                    ))
                else:
                    new_params.append(param)

            # Set the new signature on the wrapper
            wrapper.__signature__ = inspect.Signature(parameters=new_params)

            # Also update annotations for FastAPI
            wrapper.__annotations__ = {}
            for param_name, param_type in type_hints.items():
                if param_name in type_safe_conversions:
                    _, basemodel_class = type_safe_conversions[param_name]
                    wrapper.__annotations__[param_name] = basemodel_class
                else:
                    wrapper.__annotations__[param_name] = param_type

            path = self.parse_function_name(function.__name__)
            self.router.add_api_route(path=path, endpoint=wrapper, methods=methods)
            return self
        else:
            return self.add_route(function=function, methods=methods)

    def add_route_delete(self, function):
        #return self.add_route(function=function, methods=['DELETE'])

        return self.add_route_with_body(function, methods=['DELETE'])

    def add_route_get(self, function):
        import functools
        sig        = inspect.signature(function)
        type_hints = get_type_hints(function)

        primitive_conversions = {}                                  # Check for Type_Safe__Primitive parameters

        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            param_type = type_hints.get(param_name)
            if param_type and inspect.isclass(param_type):
                if issubclass(param_type, Type_Safe__Primitive):
                    primitive_base = param_type.__primitive_base__
                    if primitive_base is None:
                        for base in param_type.__mro__:
                            if base in (str, int, float):
                                primitive_base = base
                                break

                    if primitive_base:
                        primitive_conversions[param_name] = (param_type, primitive_base)

        if primitive_conversions:
            # Create a wrapper that preserves the exact signature
            @functools.wraps(function)
            def wrapper(*args, **kwargs):
                # Convert primitive values to Type_Safe__Primitive instances
                converted_kwargs  = {}
                validation_errors = []
                for param_name, param_value in kwargs.items():
                    if param_name in primitive_conversions:
                        type_safe_primitive_class, _ = primitive_conversions[param_name]
                        try:
                            converted_kwargs[param_name] = type_safe_primitive_class(param_value)
                        except (ValueError, TypeError) as e:
                            # Create validation error in FastAPI format
                            validation_errors.append({'type': 'value_error',
                                                      'loc' : ('query', param_name),
                                                      'msg' : str(e),
                                                      'input': param_value})
                    else:
                        converted_kwargs[param_name] = param_value

                # If there were validation errors, raise them
                if validation_errors:
                    raise RequestValidationError(validation_errors)

                # Call with self if it's in args
                if args:
                    result = function(*args, **converted_kwargs)
                else:
                    result = function(**converted_kwargs)

                # Convert result if needed
                if isinstance(result, Type_Safe__Primitive):
                    return result.__primitive_base__(result)
                return result

            # Build new parameter list with primitive types
            new_params = []
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue  # Skip self
                if param_name in primitive_conversions:
                    _, primitive_type = primitive_conversions[param_name]
                    # Replace with primitive type parameter
                    new_params.append(inspect.Parameter(
                        name=param_name,
                        kind=param.kind,
                        default=param.default,
                        annotation=primitive_type
                    ))
                else:
                    new_params.append(param)

            # Create new signature
            wrapper.__signature__ = inspect.Signature(parameters=new_params)

            return self.add_route(function=wrapper, methods=['GET'])
        else:
            return self.add_route(function=function, methods=['GET'])

    def add_route_post(self, function):
        return self.add_route_with_body(function, methods=['POST'])

    def add_route_put(self, function):
        return self.add_route_with_body(function, methods=['PUT'])

    def fast_api_utils(self):
        from osbot_fast_api.utils.Fast_API_Utils import Fast_API_Utils
        return Fast_API_Utils(self.app)

    def parse_function_name(self, function_name):                           # added support for routes that have resource ids in the path
        parts = function_name.split('__')
        path_segments = []

        for i, part in enumerate(parts):
            if i == 0:                                                  # First part is always literal
                path_segments.append(part.replace('_', '-'))
            else:
                if '_' in part:                                         # After __, check if it's a parameter or literal
                    subparts = part.split('_', 1)                       # Contains underscore, split into param and literal
                    path_segments.append('{' + subparts[0] + '}')
                    path_segments.append(subparts[1].replace('_', '-'))
                else:
                    path_segments.append('{' + part + '}')              # Just a parameter

        return '/' + '/'.join(path_segments)

    @index_by
    def routes(self):
        return self.fast_api_utils().fastapi_routes(router=self.router)

    def routes_methods(self):
        return list(self.routes(index_by='method_name'))

    def routes_paths(self):
        return list(self.routes(index_by='http_path'))

    def setup(self):
        self.setup_routes()
        self.app.include_router(self.router, prefix=self.prefix, tags=[self.tag])
        return self

    def setup_routes(self):     # overwrite this to add routes to self.router
        pass



    # def routes_list(self):
    #     items = []
    #     for route in self.routes():
    #         for http_methods in route.get('http_methods'):
    #             item = f'{http_methods:4} | {route.get("method_name"):14} | {route.get("http_path")}'
    #             items.append(item)
    #     return items