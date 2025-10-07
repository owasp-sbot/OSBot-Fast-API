import re
import pytest
from unittest                                                                             import TestCase
from fastapi                                                                              import FastAPI
from osbot_utils.type_safe.primitives.core.Safe_Float                                     import Safe_Float
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Display_Name import Safe_Str__Display_Name
from osbot_utils.type_safe.primitives.core.Safe_UInt                                      import Safe_UInt
from starlette.testclient                                                                 import TestClient
from osbot_fast_api.api.routes.type_safe.Type_Safe__Route__Registration                   import Type_Safe__Route__Registration
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                         import Safe_Id


class Schema__Core_User(Type_Safe):                               # Schema for Core FastAPI test
    user_id : Safe_Id
    name    : Safe_Str__Display_Name
    age     : Safe_UInt


class Schema__Core_Product(Type_Safe):                            # Another schema for testing
    product_id : Safe_Id
    price      : Safe_Float
    in_stock   : bool = True


class test_Fast_API__Type_Safe__support_for_core_FastAPI(TestCase):
    """
    Important TEST: This demonstrates that Type_Safe route registration
    works with Core FastAPI, not just our Fast_API wrapper class.

    This means developers can:
        1. Add Type_Safe to existing FastAPI projects incrementally
        2. Use Type_Safe without adopting our full Fast_API class
        3. Get automatic type conversion and validation in Core FastAPI
    """

    @classmethod
    def setUpClass(cls):                                              # ONE-TIME setup with core FastAPI
        cls.app          = FastAPI()                                  # Pure FastAPI - no Fast_API wrapper!
        cls.registration = Type_Safe__Route__Registration()

        # Register routes using Type_Safe system
        cls.registration.register_route(cls.app.router, cls.create_user     , ['POST'])
        cls.registration.register_route(cls.app.router, cls.get_user        , ['GET'])
        cls.registration.register_route(cls.app.router, cls.create_product  , ['POST'])

        cls.client = TestClient(cls.app)

    @staticmethod
    def create_user(user: Schema__Core_User) -> Schema__Core_User:                          # Type_Safe parameter and return
        return user

    @staticmethod
    def get_user(user_id: Safe_Id) -> dict:                                                 # Type_Safe primitive parameter
        return {'user_id': str(user_id), 'found': True}

    @staticmethod
    def create_product(product: Schema__Core_Product) -> Schema__Core_Product:
        return product

    def test__Core_fastapi__handles_type_safe_body_params(self):                            # Test Core FastAPI handles Type_Safe body parameters
        response = self.client.post('/create-user', json={  'user_id': 'USER-456'   ,
                                                            'name'   : 'Core Test'  ,
                                                            'age'    : 30           })

        assert response.status_code == 200
        result = response.json()

        assert result['user_id'] == 'USER-456'                                              # Type_Safe conversion worked in Core FastAPI!
        assert result['name']    == 'Core Test'
        assert result['age']     == 30

    def test__Core_fastapi__handles_safe_primitives(self):        # Test Core FastAPI handles Safe_Str primitives
        response = self.client.get('/get-user', params={'user_id': 'USER-789'})

        assert response.status_code == 200
        result = response.json()

        # Safe_Id was handled correctly
        assert result['user_id'] == 'USER-789'
        assert result['found']   is True

    def test__Core_fastapi__auto_validates(self):                 # Test Core FastAPI gets Type_Safe validation

        error_message = "Safe_UInt must be >= 0, got -5"
        with pytest.raises(ValueError, match=re.escape(error_message)):
            response = self.client.post('/create-user', json={ 'user_id': 'USER-999',                            # Invalid age will should be rejected by Safe_UInt
                                                               'name': 'Invalid User',
                                                               'age'  : -5           })                           # Negative not allowed in Safe_Int


        # Should get validation error (not 200)                             # note we don't get this far, since self.client is the one raising the exception
        # assert response.status_code == 400                                # Type_Safe validation worked!

    def test__Core_fastapi__sanitizes_input(self):                # Test Core FastAPI gets Type_Safe sanitization
        # Safe_Id should sanitize special characters
        response = self.client.post('/create-user', json={
            'user_id': 'USER!@#$%123',                                # Special chars will be sanitized
            'name': 'Test',
            'age': 25
        })

        assert response.status_code == 200
        result = response.json()

        # Safe_Id sanitized the input automatically
        assert result['user_id'] == 'USER_____123'                    # Special chars replaced with _

    def test__Core_fastapi__complex_schema(self):                 # Test Core FastAPI handles complex Type_Safe schemas
        response = self.client.post('/create-product', json={
            'product_id': 'PROD-001',
            'price': 99.99,
            'in_stock': False
        })

        assert response.status_code == 200
        result = response.json()

        assert result['product_id'] == 'PROD-001'
        assert result['price']      == 99.99
        assert result['in_stock']   is False

    def test__Core_fastapi__route_extraction_works(self):         # Test that route extraction works on Core FastAPI
        from osbot_fast_api.client.Fast_API__Route__Extractor import Fast_API__Route__Extractor

        extractor  = Fast_API__Route__Extractor(app=self.app, include_default=False)
        collection = extractor.extract_routes()

        # Should extract all our Type_Safe routes
        route_names = [r.method_name for r in collection.routes]
        assert 'create_user'    in route_names
        assert 'get_user'       in route_names
        assert 'create_product' in route_names

        # Verify original types preserved
        create_user_route = next(r for r in collection.routes if r.method_name == 'create_user')
        assert create_user_route.body_params[0].param_type is Schema__Core_User  # Original Type_Safe class
        assert create_user_route.return_type is Schema__Core_User

    def test__Core_fastapi__serialization_round_trip(self):       # Test serialization works with Core FastAPI routes
        from osbot_fast_api.client.Fast_API__Route__Extractor import Fast_API__Route__Extractor

        extractor  = Fast_API__Route__Extractor(app=self.app, include_default=False)
        collection = extractor.extract_routes()

        # Serialize
        json_data = collection.json()

        # Deserialize
        restored = collection.__class__.from_json(json_data)

        # Perfect round-trip
        assert collection.obj() == restored.obj()

        # No __BaseModel artifacts
        json_str = str(json_data)
        assert '__BaseModel' not in json_str