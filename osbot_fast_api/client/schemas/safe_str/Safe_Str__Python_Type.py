import re
from osbot_utils.type_safe.Type_Safe__Primitive import Type_Safe__Primitive

# todo move to OSBot_Utils

TYPE_SAFE_STR__PYTHON__TYPE__MAX_LENGTH = 512
TYPE_SAFE_STR__PYTHON__TYPE__REGEX      = r'[^a-zA-Z0-9._]'




class Safe_Str__Python__Type(Type_Safe__Primitive, str):
    regex      = re.compile(TYPE_SAFE_STR__PYTHON__TYPE__REGEX)
    max_length = TYPE_SAFE_STR__PYTHON__TYPE__MAX_LENGTH

    # todo: add extra checks for Python Names (like it can't start with numbers