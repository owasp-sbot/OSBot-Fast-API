from unittest                                                                      import TestCase

from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Email import Safe_Str__Email

from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Display_Name import Safe_Str__Display_Name

from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id

from osbot_utils.utils.Objects                                                     import __
from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                                import Safe_Str
from osbot_utils.type_safe.primitives.core.Safe_Int                                import Safe_Int
from osbot_utils.type_safe.primitives.core.Safe_Float                              import Safe_Float
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                  import Safe_Id
from osbot_fast_api.api.routes.Type_Safe__Route__Analyzer                          import Type_Safe__Route__Analyzer
from osbot_fast_api.api.routes.Type_Safe__Route__Converter                         import Type_Safe__Route__Converter
from pydantic                                                                      import BaseModel


class test_Type_Safe__Route__Converter(TestCase):

    @classmethod
    def setUpClass(cls):                                                            # Setup expensive resources once
        cls.analyzer  = Type_Safe__Route__Analyzer()
        cls.converter = Type_Safe__Route__Converter()

    def test__init__(self):                                                         # Test converter initialization
        with Type_Safe__Route__Converter() as _:
            assert type(_) is Type_Safe__Route__Converter

    def test_enrich_signature_with_conversions__no_conversion_needed(self):         # Test signature with no Type_Safe parameters
        def simple_endpoint(name: str, age: int):
            return {"name": name, "age": age}

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(simple_endpoint)

        with self.converter as _:
            enriched = _.enrich_signature_with_conversions(signature)

            assert len(enriched.type_safe_conversions) == 0                         # No Type_Safe classes to convert
            assert enriched.return_needs_conversion    is False

    def test_enrich_signature_with_conversions__type_safe_param(self):              # Test signature with Type_Safe parameter
        class User_Data(Type_Safe):
            name  : Safe_Str
            email : Safe_Str

        def create_user(user_data: User_Data):
            return user_data

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(create_user)

        with self.converter as _:
            enriched = _.enrich_signature_with_conversions(signature)

            assert 'user_data' in enriched.type_safe_conversions                    # Conversion entry created
            type_safe_class, basemodel_class = enriched.type_safe_conversions['user_data']
            assert type_safe_class is User_Data
            assert issubclass(basemodel_class, BaseModel)                           # Converted to Pydantic

            param_info = enriched.parameters[0]
            assert param_info.converted_type is not None
            assert issubclass(param_info.converted_type, BaseModel)

    def test_enrich_signature_with_conversions__type_safe_return(self):             # Test signature with Type_Safe return type
        class Response_Data(Type_Safe):
            status  : Safe_Str
            code    : Safe_Int

        def get_status() -> Response_Data:
            return Response_Data(status=Safe_Str("ok"), code=Safe_Int(200))

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(get_status)

        with self.converter as _:
            enriched = _.enrich_signature_with_conversions(signature)

            assert enriched.return_needs_conversion      is True
            assert enriched.return_converted_type        is not None
            assert issubclass(enriched.return_converted_type, BaseModel)

    def test_convert_parameter_value__primitive_conversion(self):                   # Test converting raw value to Safe primitive
        class User_Data(Type_Safe):
            user_id : Safe_Id

        def endpoint(user_id: Safe_Id):
            return user_id

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)

        with self.converter as _:
            converted = _.convert_parameter_value('user_id', 'raw-string-id', signature)

            assert type(converted) is Safe_Id
            assert converted       == Safe_Id('raw-string-id')

    def test_convert_parameter_value__type_safe_from_dict(self):                    # Test converting dict to Type_Safe object
        class Product_Data(Type_Safe):
            name  : Safe_Str
            price : Safe_Int

        def create_product(product: Product_Data):
            return product

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(create_product)
            signature = self.converter.enrich_signature_with_conversions(signature)

        product_dict = {'name': 'Widget', 'price': 99}

        with self.converter as _:
            converted = _.convert_parameter_value('product', product_dict, signature)

            assert type(converted) is Product_Data
            assert converted.obj() == __(name='Widget', price=99)

    def test_convert_parameter_value__type_safe_with_nested_primitives(self):       # Test converting dict with nested Safe primitives
        class Order_Data(Type_Safe):
            order_id : Safe_Id
            quantity : Safe_Int
            price    : Safe_Float

        def create_order(order: Order_Data):
            return order

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(create_order)
            signature = self.converter.enrich_signature_with_conversions(signature)

        order_dict = {  'order_id' : 'ORD-123',
                        'quantity' : 5        ,
                        'price'    : 99.99    }

        with self.converter as _:
            converted = _.convert_parameter_value('order', order_dict, signature)

            assert type(converted)          is Order_Data
            assert type(converted.order_id) is Safe_Id
            assert type(converted.quantity) is Safe_Int
            assert type(converted.price)    is Safe_Float

    def test_convert_return_value__type_safe_to_dict(self):                         # Test converting Type_Safe return to dict
        class Response_Data(Type_Safe):
            message : Safe_Str
            code    : Safe_Int

        def endpoint() -> Response_Data:
            return Response_Data(message=Safe_Str("success"), code=Safe_Int(200))

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)
            signature = self.converter.enrich_signature_with_conversions(signature)

        result = Response_Data(message=Safe_Str("success"), code=Safe_Int(200))

        with self.converter as _:
            converted = _.convert_return_value(result, signature)

            assert type(converted) is dict
            assert converted       == {'message': 'success', 'code': 200}

    def test_convert_return_value__primitive_to_base(self):                         # Test converting Safe primitive return to base type
        def endpoint() -> Safe_Id:
            return Safe_Id("test-id-123")

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)

        result = Safe_Id("test-id-123")

        with self.converter as _:
            converted = _.convert_return_value(result, signature)

            assert type(converted) is str                                           # Converted to base type
            assert converted       == "test-id-123"

    def test_convert_return_value__no_conversion_needed(self):                      # Test return value that doesn't need conversion
        def endpoint() -> dict:
            return {"status": "ok"}

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)

        result = {"status": "ok"}

        with self.converter as _:
            converted = _.convert_return_value(result, signature)

            assert converted is result                                              # No conversion, same object

    def test_find_parameter__existing_param(self):                                  # Test finding parameter in signature
        def endpoint(user_id: Safe_Id, name: Safe_Str):
            return {"user_id": user_id, "name": name}

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)

        with self.converter as _:
            param_info = _.find_parameter(signature, 'user_id')

            assert param_info is not None
            assert param_info.name == 'user_id'

    def test_find_parameter__nonexistent_param(self):                               # Test finding non-existent parameter
        def endpoint(user_id: Safe_Id):
            return user_id

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(endpoint)

        with self.converter as _:
            param_info = _.find_parameter(signature, 'nonexistent')

            assert param_info is None

    def test_complex_scenario__mixed_conversions(self):                             # Test complex scenario with multiple conversion types
        class Product_Data(Type_Safe):
            name     : Safe_Str
            price    : Safe_Int
            category : Safe_Id

        class Product_Response(Type_Safe):
            product_id : Safe_Id
            name       : Safe_Str
            status     : Safe_Str

        def create_product(store_id     : Safe_Id      ,
                          product_data  : Product_Data ,
                          notify        : bool = False
                         ) -> Product_Response:
            return Product_Response(
                product_id = Safe_Id("PROD-123")    ,
                name       = product_data.name      ,
                status     = Safe_Str("created")
            )

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(create_product)

        with self.converter as _:
            enriched = _.enrich_signature_with_conversions(signature)

            assert 'store_id'     in enriched.primitive_conversions                 # Primitive conversion
            assert 'product_data' in enriched.type_safe_conversions                 # Type_Safe conversion
            assert enriched.return_needs_conversion is True

            product_dict = {'name': 'Widget', 'price': 100, 'category': 'CAT-1'}
            converted_store_id = _.convert_parameter_value('store_id', 'STORE-42', enriched)
            converted_product  = _.convert_parameter_value('product_data', product_dict, enriched)

            assert type(converted_store_id)        is Safe_Id
            assert type(converted_product)         is Product_Data
            assert type(converted_product.name)    is Safe_Str
            assert type(converted_product.price)   is Safe_Int
            assert type(converted_product.category) is Safe_Id

    def test_convert_parameter_value__from_basemodel_instance(self):                # Test converting from Pydantic BaseModel instance
        class User_Data(Type_Safe):
            name  : Safe_Str__Display_Name
            email : Safe_Str__Email

        def create_user(user: User_Data):
            return user

        with self.analyzer as analyzer:
            signature = analyzer.analyze_function(create_user)
            signature = self.converter.enrich_signature_with_conversions(signature)

        _, basemodel_class = signature.type_safe_conversions['user']
        basemodel_instance = basemodel_class(name='Alice', email='alice@test.com')

        with self.converter as _:
            converted = _.convert_parameter_value('user', basemodel_instance, signature)

            assert type(converted)       is User_Data
            assert type(converted.name)  is Safe_Str__Display_Name
            assert type(converted.email) is Safe_Str__Email
            assert converted.name        == 'Alice'
            assert converted.email       == 'alice@test.com'