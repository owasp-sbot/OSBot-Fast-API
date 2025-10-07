from unittest                                                       import TestCase
from fastapi                                                        import FastAPI
from starlette.testclient                                           import TestClient
from osbot_fast_api.client.Fast_API__Route__Extractor               import Fast_API__Route__Extractor
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id   import Safe_Id
from osbot_fast_api.api.routes.Type_Safe__Route__Registration       import Type_Safe__Route__Registration


class Schema__Integration_User(Type_Safe):                           # Test schema for integration
    user_id : Safe_Id
    name    : str
    age     : int = 0


class test_Fast_API__Type_Safe__routes_support(TestCase):

    @classmethod
    def setUpClass(cls):                                              # ONE-TIME setup for integration tests
        cls.app          = FastAPI()
        cls.registration = Type_Safe__Route__Registration()
        cls.client       = None                                       # Will be created after routes registered

    def test__full_cycle__original_types_preserved(self):            # Test complete cycle: register -> extract -> serialize -> deserialize
        # Step 1: Register route with Type_Safe parameter
        def create_user(user: Schema__Integration_User) -> Schema__Integration_User:
            return user

        self.registration.register_route(self.app.router, create_user, ['POST'])

        # Step 2: Make actual request through TestClient
        if self.client is None:
            self.client = TestClient(self.app)

        response = self.client.post('/create-user', json= { 'user_id': 'USER-123' ,
                                                            'name'   : 'Test User',
                                                            'age'    : 25         })

        # Step 3: Verify response works correctly
        assert response.status_code == 200
        result = response.json()
        assert result['user_id'] == 'USER-123'                        # Type_Safe handled conversion
        assert result['name'   ] == 'Test User'
        assert result['age'    ]  == 25

        # Step 4: Extract routes and verify types
        extractor  = Fast_API__Route__Extractor(app=self.app, include_default=False)
        collection = extractor.extract_routes()

        # Find our route
        our_route = None                                                            # todo: we should have a helper method to provide this
        for route in collection.routes:                                             #       need to find a particular route
            if route.method_name == 'create_user':
                our_route = route
                break

        assert our_route is not None

        # Step 5: CRITICAL - Verify original types preserved throughout
        assert len(our_route.body_params) == 1
        assert our_route.body_params[0].param_type is Schema__Integration_User  # Original class
        assert our_route.return_type is Schema__Integration_User                # Original class

        # Step 6: Serialize and deserialize
        json_data = collection.json()
        restored  = collection.__class__.from_json(json_data)

        # Step 7: Verify round-trip preserved everything
        assert collection.obj() == restored.obj()

    # todo: add more edge cases tests