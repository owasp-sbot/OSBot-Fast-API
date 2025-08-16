from typing                                                                      import Optional, List, Dict, Set, Any
from unittest                                                                    import TestCase
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.Type_Safe__Primitive                                  import Type_Safe__Primitive
from osbot_utils.type_safe.primitives.safe_int.Timestamp_Now                     import Timestamp_Now
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                          import Safe_Str
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Name   import Safe_Str__File__Name
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path   import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.safe_str.http.Safe_Str__Http__Content_Type import Safe_Str__Http__Content_Type
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id               import Safe_Id
from osbot_utils.utils.Objects                                                   import __
from osbot_fast_api.api.Fast_API                                                 import Fast_API
from osbot_utils.type_safe.primitives.safe_str.identifiers.Random_Guid           import Random_Guid
from osbot_fast_api.api.Fast_API__Routes                                         import Fast_API__Routes


class test__type_safe__Fast_API__Routes__support(TestCase):

    def test__1__type_safe_primitive__on_get_requests(self):
        class To_Lower(Type_Safe__Primitive, str):              # example of a Type_Safe__Primitive class
            def __new__(cls, value):
                lower_value = value.lower()                     # which just converts a string to lower
                return str.__new__(cls, lower_value)

        class GET_Routes(Fast_API__Routes):
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

        class API_Routes(Fast_API__Routes):
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

        class GUID_Routes(Fast_API__Routes):
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

        class POST_Routes(Fast_API__Routes):
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

        class POST_Routes(Fast_API__Routes):
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

    def test__6__bug__type_safe__on_put_requests(self):      # Test PUT requests with Type_Safe support

        class UpdateRequest(Type_Safe):
            id      : int
            name    : Optional[str]  = None             #  BUG this is not being picked up as optional by Pydantic
            active  : bool           = True
            metadata: Dict[str, str]

        class UpdateResponse(Type_Safe):
            id          : int
            name        : str
            active      : bool
            metadata    : Dict[str, str]
            updated_at  : str

        class PUT_Routes(Fast_API__Routes):
            tag = 'updates'

            def update_item(self, request: UpdateRequest) -> UpdateResponse:
                # Verify we get the correct Type_Safe instance
                assert isinstance(request, UpdateRequest)
                assert isinstance(request.metadata, dict)

                return UpdateResponse( id         = request.id                    ,
                                       name       = request.name or "default_name",
                                       active     = request.active                ,
                                       metadata   = request.metadata              ,
                                       updated_at = "2024-01-15T10:00:00Z"        )

            def setup_routes(self):
                self.add_route_put(self.update_item)

        class An_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(PUT_Routes)

        an_fast_api = An_Fast_API().setup()
        assert an_fast_api.routes_paths() == ['/updates/update-item']

        # Test with full data
        update_data = {'id'      : 123,
                       'name'    : 'Updated Item',
                       'active'  : False,
                       'metadata': {'key1': 'value1', 'key2': 'value2'}}

        response = an_fast_api.client().put('/updates/update-item', json=update_data)
        assert response.status_code == 200
        assert response.json() == { 'id'        : 123                               ,
                                    'name'      : 'Updated Item'                    ,
                                    'active'    : False                             ,
                                    'metadata'  : {'key1': 'value1', 'key2': 'value2'},
                                    'updated_at': '2024-01-15T10:00:00Z'
        }

        # Test with minimal data (using defaults)       # BUG name should be optional but it is needed
        minimal_data = {'id': 456}
        response = an_fast_api.client().put('/updates/update-item', json=minimal_data)
        assert response.status_code == 400
        assert response.json() == {'detail': [{'input': {'id': 456},
                                              'loc': ['body', 'name'],
                                              'msg': 'Field required',
                                              'type': 'missing'}]}

        minimal_data = {'id': 456, 'name': 'abc'}
        response = an_fast_api.client().put('/updates/update-item', json=minimal_data)


        assert response.status_code == 200
        assert response.json() == { 'id'      : 456  ,
                                    'name'    : 'abc',
                                    'active'  : True ,                          # Used default value
                                    'metadata': {}   ,                          # Used default value
                                    'updated_at': '2024-01-15T10:00:00Z'}

    def test__7__type_safe__edge_case__nested_types(self):  # Test edge case with deeply nested Type_Safe structures"""

        class Address(Type_Safe):
            street  : str
            city    : str
            country : str = "USA"

        class Contact(Type_Safe):
            email    : str
            phone    : Optional[str] = None
            addresses: List[Address]                # Complex nested type

        class PersonRequest(Type_Safe):
            name    : str
            contact : Contact                       # Will be converted to Contact-like structure
            tags    : Set[str]                      # Edge case: Set type

        class PersonResponse(Type_Safe):
            id           : int
            name         : str
            email        : str
            address_count: int

        class POST_Routes(Fast_API__Routes):
            tag = 'person'

            def create_person(self, request: PersonRequest) -> PersonResponse:
                assert isinstance(request, PersonRequest)

                # Handle the nested data
                email     = request.contact.email
                addresses = request.contact.addresses

                return PersonResponse(id            = 999           ,
                                      name          = request.name  ,
                                      email         = email         ,
                                      address_count = len(addresses))

            def setup_routes(self):
                self.add_route_post(self.create_person)

        class An_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(POST_Routes)

        an_fast_api = An_Fast_API().setup()

        # Test with nested data
        person_data = { 'name': 'John Doe',
                        'contact': {
                            'email': 'john@example.com',
                            'phone': '555-1234',
                            'addresses': [
                                {'street': '123 Main St', 'city': 'NYC'},
                                {'street': '456 Oak Ave', 'city': 'LA' }]},
                        'tags': ['vip', 'premium']}                           # Will be converted to set


        response = an_fast_api.client().post('/person/create-person', json=person_data)
        assert response.status_code == 200
        assert response.json()      == { 'id': 999,
                                         'name': 'John Doe',
                                         'email': 'john@example.com',
                                         'address_count': 2}


    def test__8__type_safe__edge_case__empty_and_none_values(self):
        """Test edge cases with empty values, None, and missing fields"""

        class FlexibleRequest(Type_Safe):
            required_field: str
            optional_str: Optional[str] = None
            optional_int: Optional[int] = None
            list_field: List[str]
            dict_field: Dict[str, Any]
            bool_field: bool = False

        class POST_Routes(Fast_API__Routes):
            tag = 'flex'

            def process(self, request: FlexibleRequest) -> dict:
                assert isinstance(request, FlexibleRequest)

                # Return the actual values to verify defaults work
                return {
                    'required': request.required_field,
                    'optional_str': request.optional_str,
                    'optional_int': request.optional_int,
                    'list_len': len(request.list_field),
                    'dict_len': len(request.dict_field),
                    'bool_val': request.bool_field
                }

            def setup_routes(self):
                self.add_route_post(self.process)

        class An_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(POST_Routes)

        an_fast_api = An_Fast_API().setup()

        # Test with minimal required data only
        minimal_data = {'required_field': 'test',
                        'optional_str'  : 'aaaa',           # BUG: should not be needed
                        'optional_int'   : 42   }           # BUG: should not be needed
        response = an_fast_api.client().post('/flex/process', json=minimal_data)
        assert response.status_code == 200
        assert response.json()      == { 'required': 'test',
                                         'optional_str': 'aaaa',    # BUG: should be None or ''
                                         'optional_int': 42    ,    # BUG: should be 0
                                         'list_len': 0,             # Empty list default
                                         'dict_len': 0,             # Empty dict default
                                         'bool_val': False          # False default
                                        }

        # Test with explicit None values
        none_data = {
            'required_field': 'test',
            'optional_str': None,
            'optional_int': None,
            'list_field': [],
            'dict_field': {},
            'bool_field': True
        }
        response = an_fast_api.client().post('/flex/process', json=none_data)
        assert response.status_code == 200
        assert response.json()      == { 'bool_val': True,
                                         'dict_len': 0,
                                         'list_len': 0,
                                         'optional_int': None,
                                         'optional_str': None,
                                         'required': 'test'}


    def test__9__type_safe__edge_case__validation_errors(self):
        """Test that validation errors are properly handled"""

        class StrictRequest(Type_Safe):
            email: str  # Will add validation in real use
            age  : int
            score: float

        class POST_Routes(Fast_API__Routes):
            tag = 'strict'

            def validate_data(self, request: StrictRequest) -> dict:
                # Manual validation as example
                if '@' not in request.email:
                    raise ValueError("Invalid email format")
                if request.age < 0 or request.age > 150:
                    raise ValueError("Age must be between 0 and 150")
                if request.score < 0.0 or request.score > 100.0:
                    raise ValueError("Score must be between 0 and 100")

                return {'status': 'valid'}

            def setup_routes(self):
                self.add_route_post(self.validate_data)

        class An_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(POST_Routes)

        an_fast_api = An_Fast_API().setup()

        # Test with invalid types (FastAPI should catch these)
        invalid_type_data = {
            'email': 'test@example.com',
            'age': 'not_a_number',  # Wrong type
            'score': 95.5
        }
        response = an_fast_api.client().post('/strict/validate-data', json=invalid_type_data)
        #assert response.status_code == 422  # Validation error from FastAPI

        # Test with valid types but business logic validation failure
        invalid_email_data = {
            'email': 'invalid_email',  # No @ sign
            'age': 25,
            'score': 95.5
        }
        response = an_fast_api.client().post('/strict/validate-data', json=invalid_email_data)
        assert response.status_code == 400  # Will get internal error from ValueError
        assert response.json()      == {'detail': 'ValueError: Invalid email format'}
        # In production, you'd want to catch ValueError and return a proper 400/422

    def test__10__regression__type_safe_primitive__on_type_safe(self):
        class To_Lower(Type_Safe__Primitive, str):          # example of a Type_Safe__Primitive class
            def __new__(cls, value):
                lower_value = value.lower()                 # which just converts a string to lower
                return str.__new__(cls, lower_value)

        class An_Class(Type_Safe):
            an_str  : str
            an_int  : int
            to_lower: To_Lower                              # FIXED: BUG: Type_Safe__Primitive is currently not supported

        class POST_Routes(Fast_API__Routes):
            tag = 'post'

            # def with_primitive(self, to_lower: To_Lower):   # QUESTION: Is this a realistic scenario?
            #    return to_lower

            def with_type_safe(self, an_class: An_Class):   # FIXED: BUG: Type_Safe__Primitive is currently not supported on posts
               return an_class

            def setup_routes(self):
                #self.add_route_post(self.with_primitive)
                self.add_route_post(self.with_type_safe)    # QUESTION: Is this a realistic scenario?

        class An_Fast_API(Fast_API):
            default_routes = False

            def setup_routes(self):
                self.add_routes(POST_Routes)

        # error_message =  ("Unable to generate pydantic-core schema for "
        #                   "<class 'test__type_safe__Fast_API__Routes__support.test__type_safe__Fast_API__Routes__support."
        #                   "test__10__bug__type_safe_primitive__on_type_safe.<locals>.To_Lower'>. "
        #                   "Set `arbitrary_types_allowed=True` in the model_config to ignore this error or implement "
        #                   "`__get_pydantic_core_schema__` on your type to fully support it.\n\nIf you got this error by calling handler(<some type>) "
        #                   "within `__get_pydantic_core_schema__` then you likely need to call `handler.generate_schema(<some type>)` "
        #                   "since we do not call `__get_pydantic_core_schema__` on `<some type>` otherwise to avoid infinite recursion.\n\n"
        #                   "For further information visit https://errors.pydantic.dev/2.11/u/schema-for-unknown-type")
        # with pytest.raises(PydanticSchemaGenerationError, match=re.escape(error_message)):
        #     An_Fast_API().setup()                     # FIXED: BUG should be able to handle it

        an_fast_api = An_Fast_API().setup()
        assert an_fast_api.routes_paths() == ['/post/with-type-safe']

        an_class = An_Class(to_lower='AbC')
        response = an_fast_api.client().post('/post/with-type-safe', json=an_class.json())
        assert response.status_code == 200
        assert response.json() == {'an_int': 0, 'an_str': '', 'to_lower': 'abc'}                # FIXED this is now working


    def test__11__type_safe_primitives__on_type_safe(self):
        class To_Lower(Type_Safe__Primitive, str):          # example of a Type_Safe__Primitive class
            def __new__(cls, value):
                lower_value = value.lower()                 # which just converts a string to lower
                return str.__new__(cls, lower_value)

        class An_Class(Type_Safe):
            an_guid                     : Random_Guid
            safe_id                     : Safe_Id
            safe_str                    : Safe_Str
            safe_str_http_content_type  : Safe_Str__Http__Content_Type  = None
            safe_str_file_name          : Safe_Str__File__Name          = None
            safe_str_file_path          : Safe_Str__File__Path
            timestamp                   : Timestamp_Now
            to_lower                    : To_Lower


        class POST_Routes(Fast_API__Routes):
            tag = 'post'

            def with_type_safe(self, an_class: An_Class) -> An_Class:
               return an_class

            def setup_routes(self):
                self.add_route_post(self.with_type_safe)

        class An_Fast_API(Fast_API):
            default_routes = False

            def setup_routes(self):
                self.add_routes(POST_Routes)

        an_fast_api = An_Fast_API().setup()
        assert an_fast_api.routes_paths() == ['/post/with-type-safe']

        an_class = An_Class(an_guid                     = '1b4b086d-0ad3-4de7-928a-7f66ccabafa3',
                            safe_str                    = 'safe!!!!'                            ,
                            safe_str_http_content_type  = 'AA!!!BBB'                            ,
                            safe_str_file_name          = '../safe.txt!!!'                      ,
                            safe_str_file_path          = '../an/path/!!!/goes-here'            ,
                            safe_id                     = 'safe-id_uvklt!!!!'                   ,
                            to_lower                    = 'AbC'                                 ,
                            timestamp                   = 1754998257071                         )
        response = an_fast_api.client().post('/post/with-type-safe', json=an_class.json())
        assert response.status_code == 200
        assert response.json() == {  'an_guid'                      : '1b4b086d-0ad3-4de7-928a-7f66ccabafa3',
                                     'safe_id'                      : 'safe-id_uvklt____'                   ,
                                     'safe_str'                     : 'safe____'                            ,
                                     'safe_str_file_name'           : '.._safe.txt___'                      ,
                                     'safe_str_file_path'           : '../an/path/___/goes-here'            ,
                                     'safe_str_http_content_type'   : 'AA___BBB'                            ,
                                     'timestamp'                    : 1754998257071                         ,
                                     'to_lower'                     : 'abc'                                 }


    def test__12__type_safe__mixed_primitive_and_complex(self):
        """Test routes that mix Type_Safe__Primitive in path/query with Type_Safe in body"""

        class ResourceID(Type_Safe__Primitive, str):
            def __new__(cls, value):
                if not value.startswith('RES-'):
                    value = f'RES-{value}'
                return str.__new__(cls, value.upper())

        class UpdateData(Type_Safe):
            content    : str
            version    : int = 1
            resource_id: ResourceID

        class PUT_Routes(Fast_API__Routes):
            tag = 'resource'

            def update_resource__id(self, data: UpdateData) -> dict:                                                    # note that there is no id var in the function
                assert isinstance(data, UpdateData)

                return { 'resource_id': str(data.resource_id),
                         'content': data.content ,
                         'version': data.version }

            def setup_routes(self):
                self.add_route_put(self.update_resource__id)            # This will create route: /resource/update-resource/id (because there is no id field in the method definition)

        class An_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(PUT_Routes)

        an_fast_api = An_Fast_API().setup()
        assert an_fast_api.routes_paths() == ['/resource/update-resource/id']

        # Test PUT with path parameter and body
        update_data = UpdateData(resource_id='abc').json()
        response = an_fast_api.client().put('/resource/update-resource/id', json=update_data)

        assert response.status_code == 200
        assert response.json() == {'content'    : ''       ,
                                   'resource_id': 'RES-ABC',
                                   'version'    : 1        }

