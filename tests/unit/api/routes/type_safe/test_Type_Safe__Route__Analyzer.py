from unittest                                                                      import TestCase
from typing                                                                        import List, Dict
from osbot_utils.testing.__                                                        import __
from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                                import Safe_Str
from osbot_utils.type_safe.primitives.core.Safe_Int                                import Safe_Int
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                  import Safe_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id    import Safe_Str__Id
from osbot_fast_api.api.routes.type_safe.Type_Safe__Route__Analyzer                import Type_Safe__Route__Analyzer
from osbot_fast_api.api.schemas.routes.Schema__Route__Signature                    import Schema__Route__Signature


class test_Type_Safe__Route__Analyzer(TestCase):

    @classmethod
    def setUpClass(cls):                                                            # Setup expensive resources once
        cls.analyzer = Type_Safe__Route__Analyzer()

    def test__init__(self):                                                         # Test analyzer initialization
        with Type_Safe__Route__Analyzer() as _:
            assert type(_) is Type_Safe__Route__Analyzer

    def test_analyze_function__no_params(self):                                     # Test function with no parameters
        def simple_endpoint():
            return {"status": "ok"}

        with self.analyzer as _:
            signature = _.analyze_function(simple_endpoint)

            assert type(signature)              is Schema__Route__Signature
            assert signature.function_name      == Safe_Str__Id('simple_endpoint')
            assert len(signature.parameters)    == 0
            assert signature.has_body_params    is False
            assert signature.return_type        is None


    def test_analyze_function__with_primitive_params(self):                         # Test function with Safe primitive parameters
        def get_user(user_id: Safe_Id, name: Safe_Str):
            return {"user_id": user_id, "name": name}

        with self.analyzer as _:
            signature = _.analyze_function(get_user)
            assert type(signature)                               is Schema__Route__Signature
            assert signature.obj() == __(return_type             = None                                               ,
                                         return_converted_type   = None                                               ,
                                         return_needs_conversion = False                                              ,
                                         has_body_params         = False                                              ,
                                         has_path_params         = False                                              ,
                                         has_query_params        = False                                              ,
                                         function_name           = 'get_user'                                        ,
                                         parameters              = [__(converted_type          = None                ,
                                                                       is_primitive            = True                ,
                                                                       is_type_safe            = False               ,
                                                                       primitive_base          = 'builtins.str'      ,
                                                                       requires_conversion     = True                ,
                                                                       default_value           = None                ,
                                                                       has_default             = False               ,
                                                                       nested_primitive_fields = None                ,
                                                                       name                    = 'user_id'           ,
                                                                       param_type              = 'osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id.Safe_Id'),
                                                                    __(converted_type          = None                ,
                                                                       is_primitive            = True                ,
                                                                       is_type_safe            = False               ,
                                                                       primitive_base          = 'builtins.str'      ,
                                                                       requires_conversion     = True                ,
                                                                       default_value           = None                ,
                                                                       has_default             = False               ,
                                                                       nested_primitive_fields = None                ,
                                                                       name                    = 'name'              ,
                                                                       param_type              = 'osbot_utils.type_safe.primitives.core.Safe_Str.Safe_Str')],
                                         primitive_conversions   = __(user_id = ('osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id.Safe_Id' , 'builtins.str'),
                                                                      name    = ('osbot_utils.type_safe.primitives.core.Safe_Str.Safe_Str'              , 'builtins.str')),
                                         type_safe_conversions   = __()                                               ,
                                         primitive_field_types   = __()                                               )


            assert len(signature.parameters)                    == 2
            assert signature.parameters[0].name                 == Safe_Str__Id('user_id')
            assert signature.parameters[0].is_primitive         is True
            assert signature.parameters[0].requires_conversion  is True
            assert signature.parameters[0].primitive_base       is str

            assert signature.parameters[1].name                 == Safe_Str__Id('name')
            assert signature.parameters[1].is_primitive         is True
            assert signature.parameters[1].primitive_base       is str

            assert 'user_id' in signature.primitive_conversions                     # Verify conversion tracking
            assert 'name'    in signature.primitive_conversions

    def test_analyze_function__with_type_safe_params(self):                         # Test function with Type_Safe object parameters
        class User_Data(Type_Safe):
            name  : Safe_Str
            email : Safe_Str
            age   : Safe_Int

        def create_user(user_data: User_Data):
            return user_data

        with self.analyzer as _:
            signature = _.analyze_function(create_user)

            assert len(signature.parameters)                    == 1
            assert signature.parameters[0].name                 == Safe_Str__Id('user_data')
            assert signature.parameters[0].is_type_safe         is True
            assert signature.parameters[0].requires_conversion  is True
            assert signature.has_body_params                    is True                         # Type_Safe params go in body

            assert signature.parameters[0].nested_primitive_fields is not None                  # Check nested primitive detection
            assert 'name'  in signature.parameters[0].nested_primitive_fields
            assert 'email' in signature.parameters[0].nested_primitive_fields
            assert 'age'   in signature.parameters[0].nested_primitive_fields

    def test_analyze_function__mixed_params(self):                                  # Test function with both path and body params
        class Order_Data(Type_Safe):
            items    : List[str]
            quantity : Safe_Int

        def update_order(order_id: Safe_Id, data: Order_Data):
            return {"order_id": order_id, "data": data}

        with self.analyzer as _:
            signature = _.analyze_function(update_order)

            assert len(signature.parameters)                    == 2
            assert signature.parameters[0].name                 == Safe_Str__Id('order_id')
            assert signature.parameters[0].is_primitive         is True
            assert signature.parameters[1].name                 == Safe_Str__Id('data')
            assert signature.parameters[1].is_type_safe         is True
            assert signature.has_body_params                    is True

    def test_analyze_function__with_defaults(self):                                 # Test function with default parameter values
        def search(query: Safe_Str, limit: Safe_Int = Safe_Int(10)):
            return {"query": query, "limit": limit}

        with self.analyzer as _:
            signature = _.analyze_function(search)

            assert len(signature.parameters)                    == 2
            assert signature.parameters[0].has_default          is False
            assert signature.parameters[1].has_default          is True
            assert signature.parameters[1].default_value        == Safe_Int(10)

    def test_analyze_function__with_return_type(self):                              # Test function with Type_Safe return type
        class User_Response(Type_Safe):
            user_id  : Safe_Id
            username : Safe_Str

        def get_user() -> User_Response:
            return User_Response(user_id=Safe_Id("123"), username=Safe_Str("alice"))

        with self.analyzer as _:
            signature = _.analyze_function(get_user)

            assert signature.return_type             is User_Response
            assert signature.return_needs_conversion is True

    def test_analyze_parameter__primitive_types(self):                              # Test parameter analysis for primitives
        from inspect import Parameter as InspectParameter

        param = InspectParameter('test_id', InspectParameter.POSITIONAL_OR_KEYWORD)
        type_hints = {'test_id': Safe_Id}

        with self.analyzer as _:
            param_info = _.analyze_parameter('test_id', param, type_hints)

            assert param_info.name              == Safe_Str__Id('test_id')
            assert param_info.param_type        is Safe_Id
            assert param_info.is_primitive      is True
            assert param_info.primitive_base    is str
            assert param_info.requires_conversion is True

    def test_is_primitive_class__various_types(self):                               # Test primitive type detection
        with self.analyzer as _:
            assert _.is_primitive_class(Safe_Str)   is True
            assert _.is_primitive_class(Safe_Int)   is True
            assert _.is_primitive_class(Safe_Id)    is True
            assert _.is_primitive_class(str)        is False                        # Raw primitives are not Type_Safe__Primitive
            assert _.is_primitive_class(int)        is False
            assert _.is_primitive_class(Type_Safe)  is False
            assert _.is_primitive_class(None)       is False

    def test_is_type_safe_class__various_types(self):                               # Test Type_Safe class detection
        class Custom_Schema(Type_Safe):
            value: str

        with self.analyzer as _:
            assert _.is_type_safe_class(Type_Safe)          is True
            assert _.is_type_safe_class(Custom_Schema)      is True
            assert _.is_type_safe_class(Safe_Str)           is False                # Primitives are not Type_Safe (they are Type_Safe__Primitive)
            assert _.is_type_safe_class(str)                is False
            assert _.is_type_safe_class(dict)               is False
            assert _.is_type_safe_class(None)               is False

    def test_get_primitive_base__various_primitives(self):                          # Test primitive base type extraction
        with self.analyzer as _:
            assert _.get_primitive_base(Safe_Str)   is str
            assert _.get_primitive_base(Safe_Int)   is int
            assert _.get_primitive_base(Safe_Id)    is str

    def test_extract_primitive_fields__nested_primitives(self):                     # Test extraction of primitive fields from Type_Safe class
        class Complex_Schema(Type_Safe):
            user_id   : Safe_Id
            count     : Safe_Int
            name      : Safe_Str
            metadata  : Dict[str, str]                                              # Non-primitive field

        with self.analyzer as _:
            primitive_fields = _.extract_primitive_fields(Complex_Schema)

            assert primitive_fields is not None
            assert 'user_id' in primitive_fields
            assert 'count'   in primitive_fields
            assert 'name'    in primitive_fields
            assert 'metadata' not in primitive_fields                               # Non-primitive excluded

            assert primitive_fields['user_id']  is Safe_Id
            assert primitive_fields['count']    is Safe_Int
            assert primitive_fields['name']     is Safe_Str

    def test_extract_primitive_fields__no_primitives(self):                         # Test schema with no primitive fields
        class Simple_Schema(Type_Safe):
            data     : Dict[str, str]
            items    : List[str]

        with self.analyzer as _:
            primitive_fields = _.extract_primitive_fields(Simple_Schema)

            assert primitive_fields is None                                         # No primitives found

    def test_analyze_function__complex_scenario(self):                              # Test complex function with multiple parameter types
        class Product_Data(Type_Safe):
            name     : Safe_Str
            price    : Safe_Int
            category : Safe_Str

        class Product_Response(Type_Safe):
            product_id : Safe_Id
            name       : Safe_Str
            status     : Safe_Str

        def create_product(store_id    : Safe_Id         ,
                          product_data : Product_Data    ,
                          notify       : bool = False
                        ) -> Product_Response:
            return Product_Response()

        with self.analyzer as _:
            signature = _.analyze_function(create_product)

            assert len(signature.parameters)                    == 3
            assert signature.parameters[0].name                 == Safe_Str__Id('store_id')
            assert signature.parameters[0].is_primitive         is True
            assert signature.parameters[1].name                 == Safe_Str__Id('product_data')
            assert signature.parameters[1].is_type_safe         is True
            assert signature.parameters[2].name                 == Safe_Str__Id('notify')
            assert signature.parameters[2].has_default          is True
            assert signature.has_body_params                    is True
            assert signature.return_needs_conversion            is True

    def test_analyze_function__skips_self_parameter(self):                          # Test that self parameter is ignored
        class Test_Routes:
            def endpoint(self, user_id: Safe_Id):
                return user_id

        routes = Test_Routes()

        with self.analyzer as _:
            signature = _.analyze_function(routes.endpoint)

            assert len(signature.parameters)    == 1                                # Only user_id, not self
            assert signature.parameters[0].name == Safe_Str__Id('user_id')