from fastapi                                        import Request, status
from starlette.middleware.base                      import BaseHTTPMiddleware
from starlette.responses                            import Response
from osbot_utils.utils.Env                          import get_env
from osbot_utils.utils.Json                         import to_json_str
from osbot_utils.utils.Status                       import status_error
from osbot_fast_api.api.schemas.consts.consts__Fast_API import AUTH__EXCLUDED_PATHS

ERROR_MESSAGE__NO_KEY_NAME_SETUP   = f"Server does not have API key name setup"
ERROR_MESSAGE__NO_KEY_VALUE_SETUP  = f"Server does not have API key value setup"
ERROR_MESSAGE__API_KEY_MISSING     = f"Client API key is missing, you need to set it on a header or cookie"
ERROR_MESSAGE__API_KEY_INVALID     = "Invalid API key value"



class Middleware__Check_API_Key(BaseHTTPMiddleware):

    def __init__(self, app, env_var__api_key__name,
                       env_var__api_key__value    ,
                       allow_cors : bool          = False):

        super().__init__(app)
        self.api_key__name  = get_env(env_var__api_key__name )
        self.api_key__value = get_env(env_var__api_key__value)
        self.allow_cors     = allow_cors

    def return_error(self, error_message):
        content = to_json_str(status_error(error_message))
        return Response(content     = content                       ,
                        status_code = status.HTTP_401_UNAUTHORIZED  ,
                        media_type  = "application/json"            )

    async def dispatch(self, request: Request, call_next) -> Response:

        if request.url.path in AUTH__EXCLUDED_PATHS:                                                 # allow for the seeing the docs and accessing the methods to set the cookie
            return await call_next(request)
        if request.method == 'OPTIONS' and self.allow_cors:
            return self.create_allow_cors_response(request=request)

        if not self.api_key__name:
            return self.return_error(ERROR_MESSAGE__NO_KEY_NAME_SETUP)
        api_key_header = request.headers.get(self.api_key__name)                                     # Check for API key in headers
        api_key_cookie = request.cookies.get(self.api_key__name) if not api_key_header else None     # Check for API key in cookies as fallback
        api_key        = api_key_header or api_key_cookie

        if not self.api_key__value:
            return self.return_error(ERROR_MESSAGE__NO_KEY_VALUE_SETUP)

        if not api_key:                                                                             # If the API key is missing or invalid, return appropriate error response
            return self.return_error(ERROR_MESSAGE__API_KEY_MISSING)

        if api_key != self.api_key__value:
            return self.return_error(ERROR_MESSAGE__API_KEY_INVALID)

        response = await call_next(request)                                                         # If API key is valid, continue with the request
        return response


    def create_allow_cors_response(self, request: Request):
        origin = request.headers.get('origin', '*')
        return Response(status_code = 204,
                        headers     = { 'Access-Control-Allow-Origin'   : origin                                          ,
                                        'Access-Control-Allow-Methods'  : 'GET, POST, PUT, DELETE, OPTIONS'               ,
                                        'Access-Control-Allow-Headers'  : 'api-key__for__mgraph-ai__service, content-type',
                                        'Access-Control-Max-Age'        : '86400'                                         })
