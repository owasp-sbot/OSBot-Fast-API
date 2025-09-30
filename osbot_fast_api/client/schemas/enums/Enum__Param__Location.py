from enum import Enum

# todo: improve name so that it is more explicy about that the 'Param' actually is

class Enum__Param__Location(str, Enum):
    PATH   = "path"                                       # Parameters in URL path: /users/{id}
    QUERY  = "query"                                      # Parameters after ?: /users?limit=10
    HEADER = "header"                                     # Parameters in HTTP headers
    BODY   = "body"                                       # Request body content

