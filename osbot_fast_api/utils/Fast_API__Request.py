from starlette.datastructures           import Address
from fastapi                            import Request
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.utils.Misc             import str_to_bytes, lower


class Fast_API__Request(Type_Safe):
    address_host      : str = 'pytest'
    address_port      : int = 12345
    scope_headers     : dict
    scope_method      : str = 'GET'
    scope_path        : str = '/an/path'
    scope_query_string: bytes
    scope_type        : str = 'http'

    def __enter__(self):
        return self.request()

    def address(self):
        return Address(self.address_host, self.address_port)

    def request(self):
        return Request(self.scope())

    def scope(self):
        return dict(type    = self.scope_type,
                    client  = self.address(),
                    path    = self.scope_path,
                    method  = self.scope_method,
                    headers = self.create_headers(),
                    query_string=b'')

    def create_headers(self):
        headers = []
        for key,value in self.scope_headers.items():
            header = (str_to_bytes(key), str_to_bytes(value))            # in requests the headers are imported as tuples
            headers.append(header)
        return headers

    def set_cookie(self, key, value):
        self.set_header('cookie', f'{key}={value}')
        return self

    def set_cookies(self, items):
        for key, value in items:
            self.set_header('cookie', f'{key}={value}')
        return self

    def set_header(self, key, value):
        self.scope_headers[key] = value
        return self

    def set_headers(self, headers):
        for key, value in headers.items():
            self.set_header(lower(key), value)                          # header's key seem to need to be in lower case
        return self