from enum import Enum


class Enum__Route__Type(str, Enum):
    API_ROUTE   = "api_route"
    MOUNT       = "mount"
    WEBSOCKET   = "websocket"
    STATIC      = "static"
    WSGI        = "wsgi"