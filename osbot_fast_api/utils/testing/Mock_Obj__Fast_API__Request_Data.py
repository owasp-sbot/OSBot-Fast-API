from osbot_fast_api.events.Fast_API__Http_Event                        import Fast_API__Http_Event
from osbot_fast_api.events.schemas.Schema__Fast_API__Http_Event__Info  import Schema__Fast_API__Http_Event__Info
from osbot_utils.type_safe.Type_Safe                                   import Type_Safe
from fastapi                                                           import Request
from starlette.responses                                               import Response
from starlette.datastructures                                          import Address
from osbot_utils.utils.Misc                                            import str_to_bytes

HEADER_NAME__CITY    = 'cloudfront-viewer-city'
HEADER_NAME__COUNTRY = 'cloudfront-viewer-country'
HEADER_NAME__DOMAIN  = 'cloudfront-domain'

class Mock_Obj__Fast_API__Request_Data(Type_Safe):
    address          : Address                = None
    city             : str
    content_type     : str
    country          : str
    domain           : str
    fast_api_name    : str
    hostname         : str
    ip_address       : str
    method           : str
    path             : str
    port             : int
    querystring      : bytes
    req_headers      : list
    req_headers_data : dict
    request          : Request                = None
    request_data     : Fast_API__Http_Event = None
    res_content      : bytes
    res_headers      : dict
    res_status_code  : int
    response         : Response               = None
    url              : str
    scope            : dict
    type             : str


    def setup(self):
        self.city               = 'an city'
        self.country            = 'an country'
        self.content_type       = "application/json"
        self.domain             = 'the.cloudfront.domain'
        self.ip_address         = "pytest"
        self.fast_api_name      = 'pytest-fast-api'
        self.req_headers_data   = { HEADER_NAME__CITY   : self.city    ,
                                    HEADER_NAME__COUNTRY: self.country ,
                                    HEADER_NAME__DOMAIN : self.domain  }
        self.res_content        = b'this is the response content'
        self.res_headers        = {"content-type"             : self.content_type }
        self.res_status_code    = 201
        self.port               = 213
        self.hostname           = 'localhost-pytest'
        self.path               = '/an-path'
        self.method             = 'GET'
        self.address            = Address(self.ip_address, self.port)
        self.url                = f'http://{self.hostname}:{self.port}{self.path}'
        self.type               = 'http'
        self.querystring        = b''
        self.create_req_headers ()
        self.create_scope       ()
        self.create_request     ()
        self.create_response    ()
        return self

    def create(self):
        self.setup()
        self.create_request_data()
        return self.request_data

    def create_req_headers(self):
        req_headers = []
        for key,value in self.req_headers_data.items():
            header = (str_to_bytes(key), str_to_bytes(value))   # in requests the headers are imported as tuples
            req_headers.append(header)
        self.req_headers    =  req_headers
        # res_headers = []
        # for key, value in self.res_headers_data.items():
        #     header = (str_to_bytes(key), str_to_bytes(value))  # in requests the headers are imported as tuples
        #     res_headers.append(header)
        # self.res_headers = res_headers

    def create_request(self):
        self.request = Request(self.scope)

    def create_request_data(self):
        kwargs          = dict(fast_api_name=self.fast_api_name)
        http_event_info = Schema__Fast_API__Http_Event__Info(**kwargs)
        with Fast_API__Http_Event(http_event_info=http_event_info) as _:
            self.request_data = _
            _.on_request(self.request)
            _.on_response(self.response)
        return self

    def create_response(self):
        kwargs = dict(content     = self.res_content    ,
                      headers     = self.res_headers    ,
                      status_code = self.res_status_code)
        self.response = Response(**kwargs)

    def create_scope(self):
        self.scope = dict(type         = self.type        ,
                          client       = self.address     ,
                          hostname     = self.hostname    ,           # todo: see if this is needed  (since I think this is ignored) in the request object)
                          path         = self.url         ,           # request scope uses this to get the hostname in the request headers
                          method       = self.method      ,
                          headers      = self.req_headers ,
                          query_string = self.querystring )

