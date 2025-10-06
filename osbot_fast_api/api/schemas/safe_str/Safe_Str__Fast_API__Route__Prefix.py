from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Tag import Safe_Str__Fast_API__Route__Tag


class Safe_Str__Fast_API__Route__Prefix(Safe_Str__Fast_API__Route__Tag):
    """
    FastAPI route prefix derived from tag.
    Ensures:
    - Always starts with single '/'
    - Converts to lowercase
    - No double slashes

    Examples:
    - "users" → "/users"
    - "API/V2/Users" → "/api/v2/users"
    - "/users" → "/users" (no double slash)
    - "a/b/c" → "/a/b/c"
    - "/a/b/c/" → "/a/b/c" (trailing slash removed)
    """

    def __new__(cls, value: str = None):
        instance = super().__new__(cls, value)                      # First apply parent sanitization
        result = str(instance).lower()                              # Convert to lowercase

        result = result.lstrip('/')                                 # Remove any leading slashes to avoid double slash
        result = result.rstrip('/')                                 # Remove any trailing slashes for consistency

        while '//' in result:                                       # Clean up any double slashes in the middle
            result = result.replace('//', '/')

        if result and not result.startswith('/'):                   # Always ensure it starts with exactly one slash
            result = '/' + result
        elif not result:
            result = '/'                                            # Default to root if empty

        return str.__new__(cls, result)