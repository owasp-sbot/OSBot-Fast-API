def route_path(path: str):  # Decorator to explicitly set the route path for a function
    def decorator(func):
        func.__route_path__ = path                                                      # Store path as function attribute
        return func
    return decorator