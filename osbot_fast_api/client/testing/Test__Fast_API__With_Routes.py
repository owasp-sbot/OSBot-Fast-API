from fastapi                                    import HTTPException
from osbot_utils.type_safe.Type_Safe            import Type_Safe
from osbot_fast_api.api.Fast_API                import Fast_API
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes

# todo: see if:
#   - we should move this class to better location
#   - the 'Test' in the name Test__Fast_API__With_Routes, should be renamed (since it clashes with the normal use of 'Test_'
#   - the individual classes (below) should be in separate files

class Test__Fast_API__With_Routes(Fast_API):                                       # Test Fast_API with sample routes
    name    = "Test_API"
    version = "v1.0.0"

    def setup_routes(self):
        self.add_routes(Routes__Users)
        self.add_routes(Routes__Products)
        return self


class Schema__User(Type_Safe):                                                      # Test schemas
    id   : int
    name : str
    email: str


class Schema__Product(Type_Safe):
    id   : int
    name : str
    price: float


class Routes__Users(Fast_API__Routes):                                              # Test route class - Users
    tag = 'users'

    def get_user__user_id(self, user_id: int) -> Schema__User:                      # Get user by ID
        if user_id == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return Schema__User(id=user_id, name="Test User", email="test@test.com")

    def create_user(self, user: Schema__User) -> Schema__User:                      # Create new user
        return user

    def setup_routes(self):
        self.add_route_get(self.get_user__user_id)
        self.add_route_post(self.create_user)


class Routes__Products(Fast_API__Routes):                                           # Test route class - Products
    tag = 'products'

    def get_product__product_id(self, product_id: int) -> Schema__Product:          # Get product by ID
        return Schema__Product(id=product_id, name="Test Product", price=99.99)

    def list_products(self, limit: int = 10, offset: int = 0) -> list:              # List products with pagination
        return []

    def update_product__product_id(self, product_id: int, product: Schema__Product) -> Schema__Product: # Update product
        return product

    def setup_routes(self):
        self.add_route_get(self.get_product__product_id)
        self.add_route_get(self.list_products)
        self.add_route_put(self.update_product__product_id)