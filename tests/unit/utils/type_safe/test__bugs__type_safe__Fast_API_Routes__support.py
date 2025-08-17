from unittest                                   import TestCase
from osbot_utils.type_safe.Type_Safe            import Type_Safe
from osbot_fast_api.api.Fast_API                import Fast_API
from osbot_fast_api.api.routes.Fast_API__Routes        import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe__Primitive import Type_Safe__Primitive


class test__bugs__type_safe__Fast_API__Routes__support(TestCase):

    def test__regression__type_safe_classes__fail__on_get_requests__return_value(self):
        class To_Lower(Type_Safe__Primitive, str):              # example of a Type_Safe__Primitive class
            def __new__(cls, value):
                lower_value = value.lower()                     # which just converts a string to lower
                return str.__new__(cls, lower_value)

        class An_Class(Type_Safe):
            an_str: str

        class GET_Routes(Fast_API__Routes):
            tag = 'get'

            def with_primitive(self, to_lower: To_Lower) -> To_Lower:               # this works ok
                return to_lower

            def with_type_safe(self, an_str: str) -> An_Class:               # BUG: this raises the exception on .setup()
                an_class = An_Class()
                an_class.an_str = an_str + " (via with_type_safe)"
                return an_class


            def setup_routes(self):
                self.add_route_get(self.with_primitive )
                self.add_route_get(self.with_type_safe )

        class An_Fast_API(Fast_API):
            default_routes = False
            def setup_routes(self):
                self.add_routes(GET_Routes)

        # error_message  = ("Invalid args for response field! Hint: check that "
        #                   "<class 'test__bugs__type_safe__Fast_API__Routes__support.test__bugs__type_safe__Fast_API__Routes__support."
        #                   "test__type_safe_classes__fail__on_get_requests__return_value.<locals>.An_Class'> "
        #                   "is a valid Pydantic field type. If you are using a return type annotation that is not a valid Pydantic field "
        #                   "(e.g. Union[Response, dict, None]) you can disable generating the response model from the type annotation "
        #                   "with the path operation decorator parameter response_model=None. "
        #                   "Read more: https://fastapi.tiangolo.com/tutorial/response-model/")
        # with pytest.raises(FastAPIError, match= re.escape(error_message)):
        #     An_Fast_API().setup()             # FIXED: BUG: this should not raise exception

        an_fast_api = An_Fast_API().setup()
        assert an_fast_api.routes_paths() == ['/get/with-primitive', '/get/with-type-safe']

        test_value = "aBBccDD"
        response_1 = an_fast_api.client().get('/get/with-primitive?to_lower=' + test_value)
        response_2 = an_fast_api.client().get('/get/with-type-safe?an_str=' + test_value)
        assert response_1.status_code == 200
        assert response_1.json()      == 'abbccdd' == test_value.lower()
        assert response_2.json()      == {'an_str': 'aBBccDD (via with_type_safe)'}