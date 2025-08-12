import re
from typing import Optional, List
from unittest                           import TestCase

import pytest
from fastapi.exceptions import FastAPIError
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.Type_Safe__Primitive import Type_Safe__Primitive
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Objects import __
from pydantic import BaseModel

from osbot_fast_api.api.Fast_API        import Fast_API
from osbot_utils.helpers.Random_Guid    import Random_Guid
from osbot_fast_api.api.Fast_API_Routes import Fast_API_Routes


class test__type_safe__Fast_API_Routes__support(TestCase):

    def test__1__type_safe_primitive__on_get_requests(self):
        class To_Lower(Type_Safe__Primitive, str):              # example of a Type_Safe__Primitive class
            def __new__(cls, value):
                lower_value = value.lower()                     # which just converts a string to lower
                return str.__new__(cls, lower_value)

        class GET_Routes(Fast_API_Routes):
            tag = 'get'

            def with_primitive(self, to_lower: To_Lower):
                return to_lower

            def without_primitive(self, to_lower: str):
                return to_lower

            def setup_routes(self):
                self.add_route_get(self.with_primitive)
                self.add_route_get(self.without_primitive)

        class An_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(GET_Routes)

        an_fast_api = An_Fast_API().setup()
        assert an_fast_api.routes_paths() == ['/get/with-primitive', '/get/without-primitive']

        test_value = "aBBccDD"
        response_1 = an_fast_api.client().get('/get/with-primitive?to_lower=' + test_value)
        response_2 = an_fast_api.client().get('/get/without-primitive?to_lower=' + test_value)
        assert response_1.status_code == 200
        assert response_1.json()      == 'abbccdd' == test_value.lower()
        assert response_2.json()      == test_value

    def test__2__type_safe_primitive__with_validation(self):
        class Email(Type_Safe__Primitive, str):
            """Email address with validation"""
            def __new__(cls, value):
                if '@' not in value:
                    raise ValueError(f"Invalid email: {value}")
                return str.__new__(cls, value.lower())

        class Port_Number(Type_Safe__Primitive, int):
            """Port number with range validation"""
            def __new__(cls, value):
                port = int(value)
                if not (1 <= port <= 65535):
                    raise ValueError(f"Port must be between 1 and 65535, got {port}")
                return int.__new__(cls, port)

        class API_Routes(Fast_API_Routes):
            tag = 'api'

            def validate_email(self, email: Email):
                return {"email": email, "domain": str(email).split('@')[1]}

            def validate_port(self, port: Port_Number):
                return {"port": port, "is_privileged": port < 1024}

            def setup_routes(self):
                self.add_route_get(self.validate_email)
                self.add_route_get(self.validate_port)

        class API_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(API_Routes)

        api = API_Fast_API().setup()

        # Test valid email
        response = api.client().get('/api/validate-email?email=User@Example.COM')
        assert response.status_code == 200
        assert response.json() == {"email": "user@example.com", "domain": "example.com"}

        # Test invalid email (should fail at FastAPI validation level)
        response = api.client().get('/api/validate-email?email=notanemail')
        assert response.status_code == 400  # Validation error
        assert response.json() == {'detail': [{ 'input': 'notanemail',
                                                'loc' : ['query', 'email'],
                                                'msg' : 'Invalid email: notanemail',
                                                'type': 'value_error'}]}
        # Test valid port
        response = api.client().get('/api/validate-port?port=8080')
        assert response.status_code == 200
        assert response.json() == {"port": 8080, "is_privileged": False}

        # Test privileged port
        response = api.client().get('/api/validate-port?port=80')
        assert response.status_code == 200
        assert response.json() == {"port": 80, "is_privileged": True}

    def test__3__random_guid_example(self):
        """Test that Random_Guid works as a Type_Safe__Primitive"""

        class GUID_Routes(Fast_API_Routes):
            tag = 'guid'

            def validate_guid(self, guid: Random_Guid):
                return {"guid": str(guid), "is_valid": True}

            def setup_routes(self):
                self.add_route_get(self.validate_guid)

        class GUID_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(GUID_Routes)

        api = GUID_Fast_API().setup()

        # Test with valid GUID
        test_guid = "123e4567-e89b-12d3-a456-426614174000"
        response  = api.client().get(f'/guid/validate-guid?guid={test_guid}')
        assert response.status_code == 200
        assert response.json() == {"guid": test_guid, "is_valid": True}

        bad_guid = test_guid + 'a'
        response  = api.client().get(f'/guid/validate-guid?guid={bad_guid}')
        assert response.status_code == 400
        assert response.json() =={'detail': [{'input': '123e4567-e89b-12d3-a456-426614174000a',
                                              'loc'  : ['query', 'guid'],
                                              'msg'  : 'in Random_Guid: value provided was not a Guid: '
                                                       '123e4567-e89b-12d3-a456-426614174000a',
                                              'type'  : 'value_error'}]}

    def test__4__type_safe__on_post_requests__simple_example(self):
        class The_Request(Type_Safe):           # Type_Safe model for request
            an_str: str

        class The_Response(Type_Safe):           # Type_Safe model for request
            an_int: int
            an_str: str

        class POST_Routes(Fast_API_Routes):
            tag = 'post'

            def with_type_safe(self, the_request: The_Request) -> The_Response:
                an_str = the_request.an_str + ' world'
                return The_Response(an_int=42, an_str=an_str)


            def setup_routes(self):
                self.add_route_post(self.with_type_safe)

        class An_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(POST_Routes)

        an_fast_api = An_Fast_API().setup()
        assert an_fast_api.routes_paths() == ['/post/with-type-safe']

        post_data  = The_Request(an_str='hello').json()
        response_1 = an_fast_api.client().post('/post/with-type-safe', json=post_data)
        assert post_data              == {'an_str': 'hello'}
        assert response_1.status_code == 200
        assert response_1.json()      == {'an_int': 42, 'an_str': 'hello world'}


            # expected_error = ("Invalid args for response field! Hint: check that "
        #                   "<class 'test__type_safe__Fast_API_Routes__support.test__type_safe__Fast_API_Routes__support"
        #                   ".test__4__type_safe__on_post_requests__simple_example.<locals>.The_Request'> "
        #                   "is a valid Pydantic field type. If you are using a return type annotation that "
        #                   "is not a valid Pydantic field (e.g. Union[Response, dict, None]) "
        #                   "you can disable generating the response model from the type annotation with the path "
        #                   "operation decorator parameter response_model=None. "
        #                   "Read more: https://fastapi.tiangolo.com/tutorial/response-model/")
        # with pytest.raises(FastAPIError, match=re.escape(expected_error)):
        #     An_Fast_API().setup()


    def test__5__type_safe__on_post_requests(self):

        class UserRequest(Type_Safe):  # Type_Safe model for request
            username: str
            email   : str
            age     : Optional[int] = None
            tags    : List    [str]

        class UserResponse(Type_Safe):  # Type_Safe model for response
            id      : int
            username: str
            email   : str
            age     : Optional[int]
            tags    : List[str]
            status  : str = "active"

        class POST_Routes(Fast_API_Routes):
            tag = 'users'

            def create_user(self, user: UserRequest) -> UserResponse:  # Using Type_Safe classes directly
                # Business logic with Type_Safe instance

                assert type(user).__name__== 'UserRequest'

                assert isinstance(user, UserRequest )   is True
                assert isinstance(user.username, str)   is True
                assert isinstance(user.tags, list   )   is True
                assert user.obj()                       == __( age      = 30                    ,
                                                               username = 'JohnDoe'             ,
                                                               email    = 'John@Example.COM'    ,
                                                               tags     = ['developer', 'python'])

                # Create response using Type_Safe
                response = UserResponse( id         = 123                  ,
                                         username   = user.username.lower(),  # Some business logic
                                         email      = user.email   .lower(),
                                         age        = user.age             ,
                                         tags       = user.tags            ,
                                         status     = "active"             )
                return response

            def setup_routes(self):
                self.add_route_post(self.create_user)

        class An_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(POST_Routes)

        # Test the implementation
        an_fast_api = An_Fast_API().setup()
        assert an_fast_api.routes_paths() == ['/users/create-user']

        # Test POST with Type_Safe
        user_data = { 'username': 'JohnDoe'              ,
                      'email'   : 'John@Example.COM'     ,
                      'age'     : 30                     ,
                      'tags'    : ['developer', 'python']}

        response = an_fast_api.client().post('/users/create-user', json=user_data)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data == {'id'       : 123,
                                 'username' : 'johndoe',                # Lowercased by business logic
                                 'email'    : 'john@example.com',       # Lowercased by business logic
                                 'age'      : 30,
                                 'tags'     : ['developer', 'python'],
                                 'status'   : 'active'}

        # expected_error = "Invalid args for response field! Hint: check that <class 'test__type_safe__Fast_API_Routes__support.test__type_safe__Fast_API_Routes__support.test__1__type_safe_primitive__on_get_requests.<locals>.To_Lower'> is a valid Pydantic field type. If you are using a return type annotation that is not a valid Pydantic field (e.g. Union[Response, dict, None]) you can disable generating the response model from the type annotation with the path operation decorator parameter response_model=None. Read more: https://fastapi.tiangolo.com/tutorial/response-model/"
        # with pytest.raises(FastAPIError, match=re.escape(expected_error)):
        #    An_Fast_API().setup()
        #
        # return
        #assert an_fast_api.client().get('/get/an-class').json() == 'pong'

