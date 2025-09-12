import re
from osbot_utils.type_safe.primitives.core.Safe_Str import Safe_Str

TYPE_SAFE_STR__FASTAPI__ROUTE__REGEX = re.compile(r'[^a-zA-Z0-9\-_/{}.:]')
TYPE_SAFE_STR__FASTAPI__ROUTE__MAX_LENGTH = 512

class Safe_Str__Fast_API__Route__Tag(Safe_Str):
    regex = TYPE_SAFE_STR__FASTAPI__ROUTE__REGEX