from unittest                                                                   import TestCase
from dataclasses                                                                import dataclass
from typing                                                                     import Optional, List

from osbot_fast_api.schemas.Schema__Fast_API__Config import Schema__Fast_API__Config
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path  import Safe_Str__File__Path
from osbot_utils.utils.Objects                                                  import __
from pydantic                                                                   import BaseModel
from osbot_fast_api.api.routes.Fast_API__Routes                                 import Fast_API__Routes
from osbot_fast_api.api.Fast_API                                                import Fast_API


class test_Fast_API__Routes__with_Type_Safe(TestCase):

    def test__1__current_get_support(self):

        class GET_Routes(Fast_API__Routes):
            tag = 'get'

            def ping(self):
                return 'pong'

            def setup_routes(self):
                self.add_route_get(self.ping)

        class An_Fast_API(Fast_API):
            def setup_routes(self):
                self.add_routes(GET_Routes)
        config      = Schema__Fast_API__Config(default_routes=False)
        an_fast_api = An_Fast_API(config=config).setup()
        assert an_fast_api.routes_paths()                   == ['/get/ping']
        assert an_fast_api.client().get('/get/ping').json() == 'pong'

    def test__2__current_post_support__json(self):

        class POST_Routes(Fast_API__Routes):
            tag = 'post'

            def post_data(self, data: dict):
                return data

            def setup_routes(self):
                self.add_route_post(self.post_data)

        class An_Fast_API(Fast_API):
            def setup_routes(self):
                self.add_routes(POST_Routes)

        config      = Schema__Fast_API__Config(default_routes=False)
        an_fast_api = An_Fast_API(config=config).setup()
        assert an_fast_api.routes_paths()                   == ['/post/post-data']


        post_data = {'answer': 42}
        response = an_fast_api.client().post('/post/post-data', json=post_data)
        assert response.status_code == 200
        assert response.json()      == post_data


    def test__3__with_dataclass_type_safety(self): # Using Python dataclasses for request/response type safety

        @dataclass
        class UserRequest:                          #   Request model using dataclass"""
            username: str
            email   : str
            age     : Optional[int] = None
            tags    : List    [str] = None

            def __post_init__(self):
                if self.tags is None:
                    self.tags = []

        @dataclass
        class UserResponse:             # Response model using dataclass"""
            id      : int
            username: str
            email   : str
            age     : Optional[int]
            tags    : List[str]
            status  : str = "active"

        class User_Routes(Fast_API__Routes):
            tag = 'users'

            def create_user(self, user: UserRequest):                   # Create a new user with dataclass validation
                user_response = UserResponse(id       = 123          ,       # Simulate user creation with ID assignment
                                             username = user.username,
                                             email    = user.email   ,
                                             age      = user.age     ,
                                             tags     = user.tags    ,
                                             status   = "active"     )
                return user_response

            def get_user(self, user_id: int) -> UserResponse:            # Get user by ID with typed response"""

                return UserResponse(id       = user_id                  ,  # Simulate fetching user
                                    username = "test_user"              ,
                                    email    = "test@example.com"       ,
                                    age      = 25                       ,
                                    tags     = ["developer", "python"])

            def setup_routes(self):
                self.add_route_post(self.create_user)
                self.add_route_get(self.get_user)

        class An_Fast_API(Fast_API):
            def setup_routes(self):
                self.add_routes(User_Routes)

        # Test the implementation
        config      = Schema__Fast_API__Config(default_routes=False)
        an_fast_api = An_Fast_API(config=config).setup()
        assert an_fast_api.routes_paths() == ['/users/create-user', '/users/get-user']

        # Test POST with dataclass
        user_data = { 'username': 'john_doe'            ,
                      'email'   : 'john@example.com'    ,
                      'age'     : 30                    ,
                      'tags'    : ['admin', 'moderator']}
        response = an_fast_api.client().post('/users/create-user', json=user_data)
        assert response.status_code == 200
        result = response.json()
        assert result['username'] == 'john_doe'
        assert result['email'   ] == 'john@example.com'
        assert result['id'      ] == 123
        assert result['status'  ] == 'active'

        # Test GET with typed response
        response = an_fast_api.client().get('/users/get-user', params={'user_id': 456})
        assert response.status_code == 200
        result = response.json()
        assert result['id'      ] == 456
        assert result['username'] == 'test_user'


    def test__4__with_pydantic_type_safety(self): # Using Pydantic for request/response type safety

        class UserRequest(BaseModel):                          #   Request model using Pydantic
            username: str
            email   : str
            age     : Optional[int] = None
            tags    : List    [str] = None

            def __init__(self, **data):
                super().__init__(**data)
                if self.tags is None:
                    self.tags = []

        class UserResponse(BaseModel):             # Response model using Pydantic
            id      : int
            username: str
            email   : str
            age     : Optional[int]
            tags    : List[str]
            status  : str = "active"

        class User_Routes(Fast_API__Routes):
            tag = 'users'

            def create_user(self, user: UserRequest):                   # Create a new user with Pydantic validation
                user_response = UserResponse(id       = 123          ,       # Simulate user creation with ID assignment
                                             username = user.username,
                                             email    = user.email   ,
                                             age      = user.age     ,
                                             tags     = user.tags    ,
                                             status   = "active"     )
                return user_response

            def get_user(self, user_id: int) -> UserResponse:            # Get user by ID with typed response"""

                return UserResponse(id       = user_id                  ,  # Simulate fetching user
                                    username = "test_user"              ,
                                    email    = "test@example.com"       ,
                                    age      = 25                       ,
                                    tags     = ["developer", "python"])

            def setup_routes(self):
                self.add_route_post(self.create_user)
                self.add_route_get(self.get_user)

        class An_Fast_API(Fast_API):
            def setup_routes(self):
                self.add_routes(User_Routes)

        # Test the implementation
        config      = Schema__Fast_API__Config(default_routes=False)
        an_fast_api = An_Fast_API(config=config).setup()
        assert an_fast_api.routes_paths() == ['/users/create-user', '/users/get-user']

        # Test POST with dataclass
        user_data = { 'username': 'john_doe'            ,
                      'email'   : 'john@example.com'    ,
                      'age'     : 30                    ,
                      'tags'    : ['admin', 'moderator']}
        response = an_fast_api.client().post('/users/create-user', json=user_data)
        assert response.status_code == 200
        result = response.json()
        assert result['username'] == 'john_doe'
        assert result['email'   ] == 'john@example.com'
        assert result['id'      ] == 123
        assert result['status'  ] == 'active'

        # Test GET with typed response
        response = an_fast_api.client().get('/users/get-user', params={'user_id': 456})
        assert response.status_code == 200
        result = response.json()
        assert result['id'      ] == 456
        assert result['username'] == 'test_user'

    def test__5__with_Type_Safe__indirect_support(self): # Using Pydantic for request/response type safety

        class UserRequest(Type_Safe):                          #   Request model using Type_Safe
            username: str
            email   : str
            age     : Optional[int] = None
            tags    : List    [str]

        class UserResponse(Type_Safe):                        # Response model using Type_Safe
            id      : int
            username: str
            email   : str
            age     : Optional[int]
            tags    : List[str]
            status  : str = "active"

        class User_Routes(Fast_API__Routes):
            tag = 'users'

            def create_user(self, data: dict):                                         # Create a new user
                user          = UserRequest.from_json(data)
                user_response = UserResponse(id       = 123          ,                  # Simulate user creation with ID assignment
                                             username = user.username,
                                             email    = user.email   ,
                                             age      = user.age     ,
                                             tags     = user.tags    ,
                                             status   = "active"     )
                return user_response.json()

            def get_user(self, user_id: int) -> dict:

                return UserResponse(id       = user_id                  ,               # Simulate fetching user
                                    username = "test_user"              ,
                                    email    = "test@example.com"       ,
                                    age      = 25                       ,
                                    tags     = ["developer", "python"]).json()

            def setup_routes(self):
                self.add_route_post(self.create_user)
                self.add_route_get (self.get_user)

        class An_Fast_API(Fast_API):
            def setup_routes(self):
                self.add_routes(User_Routes)

        # Test the implementation
        config      = Schema__Fast_API__Config(default_routes=False)
        an_fast_api = An_Fast_API(config=config).setup()
        assert an_fast_api.routes_paths() == ['/users/create-user', '/users/get-user']

        # Test POST
        user_data       = { 'username': 'john_doe'            ,
                            'email'   : 'john@example.com'    ,
                            'age'     : 30                    ,
                            'tags'    : ['admin', 'moderator']}
        response_1      = an_fast_api.client().post('/users/create-user', json=user_data)
        user_response_1 = UserResponse.from_json(response_1.json())

        assert response_1.status_code == 200
        assert user_response_1.obj()  == __( status   = 'active'               ,
                                             id        = 123                   ,
                                             username  = 'john_doe'            ,
                                             email     = 'john@example.com'    ,
                                             age       = 30                    ,
                                             tags      = ['admin', 'moderator'])

        # Test GET with typed response
        response_2      = an_fast_api.client().get('/users/get-user', params={'user_id': 456})
        user_response_2 = UserResponse.from_json(response_1.json())

        assert response_2.status_code  == 200
        assert user_response_2.json()  == { 'age'     : 30                    ,
                                            'email'   : 'john@example.com'    ,
                                            'id'      : 123                   ,
                                            'status'  : 'active'              ,
                                            'tags'    : ['admin', 'moderator'],
                                            'username': 'john_doe'            }


    def test__6__with_Type_Safe__direct_support(self):              # todo: need to add support for supporting Type_Safe return values

        class An_Class(Type_Safe):
            an_str : str

        class Obj_Routes(Fast_API__Routes):
            tag = 'obj'
            def create_object(self, an_class: An_Class):                  # receive An_Class object
                return True

            def update_object(self, an_class: An_Class) :                   # receive and return An_Class object
                return an_class

            def return_object(self, an_str: str):                           # just return An_Class object
                return An_Class(an_str=an_str)

            def setup_routes(self):
                self.add_route_post(self.create_object)
                self.add_route_post(self.update_object)
                self.add_route_get (self.return_object)

        class An_Fast_API(Fast_API):
            def setup_routes(self):
                self.add_routes(Obj_Routes)

        config      = Schema__Fast_API__Config(default_routes=False)
        an_fast_api = An_Fast_API(config=config).setup()

        assert an_fast_api.routes_paths() == ['/obj/create-object',  '/obj/return-object', '/obj/update-object']

        obj_data = An_Class(an_str='42').json()
        response_1 = an_fast_api.client().post('/obj/create-object', json=obj_data)
        assert response_1.json() is True

        response_2 = an_fast_api.client().post('/obj/update-object', json=obj_data)
        assert response_2.json()  == {'an_str': '42'}

        response_3 = an_fast_api.client().get('/obj/return-object', params={'an_str':'123'})
        assert response_3.json() == {'an_str': '123'}

    def test__7__with_Type_Safe__and_path_params(self):

        class An_User(Type_Safe):
            user_name  : str
            user_id : str

        class POST_Routes(Fast_API__Routes):
            tag = 'v1/post'
            def create__user_id(self, user_id: str, an_user: An_User):              # receive and return An_Class object
                an_user.user_id = user_id
                return an_user


            def setup_routes(self):
                self.add_route_post(self.create__user_id)

        class An_Fast_API(Fast_API):
            def setup_routes(self):
                self.add_routes(POST_Routes)

        config      = Schema__Fast_API__Config(default_routes=False)
        an_fast_api = An_Fast_API(config=config).setup()

        assert an_fast_api.routes_paths() == ['/v1/post/create/{user_id}']

        an_user =  An_User(user_name='abc').json()
        response = an_fast_api.client().post('/v1/post/create/user-abc', json=an_user)
        assert response.status_code == 200
        assert response.json()      == {'user_id': 'user-abc', 'user_name': 'abc'}

    def test__regression__primitive_type__not_supported_on__init(self):
        class An_Class(Type_Safe):
            tag : Safe_Str__File__Path

        an_class = An_Class(tag='abc')
        assert an_class.tag == 'abc'
        an_class.tag = '123'
        assert an_class.tag == '123'

        Fast_API__Routes(tag='abc')

        class An_Class_2(Type_Safe):
            tag : Safe_Str__File__Path = 'aaa/bbbb'

        assert An_Class_2().obj() == __(tag='aaa/bbbb')