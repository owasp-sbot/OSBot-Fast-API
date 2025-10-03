from enum import Enum


class Enum__Route__Type(str, Enum):
    API_ROUTE   = "api_route"
    MOUNT       = "mount"
    ROUTE       = "route"
    STATIC      = "static"
    WEBSOCKET   = "websocket"
    WSGI        = "wsgi"