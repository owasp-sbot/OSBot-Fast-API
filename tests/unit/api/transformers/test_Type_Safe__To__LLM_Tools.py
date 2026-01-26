from typing                                                      import List, Dict, Optional
from unittest                                                    import TestCase
from osbot_utils.type_safe.Type_Safe                             import Type_Safe
from osbot_fast_api.api.transformers.Type_Safe__To__LLM_Tools    import Type_Safe__To__LLM_Tools, type_safe__to__llm_tools


class test_Type_Safe__To__LLM_Tools(TestCase):

    def setUp(self):                                                                      # Initialize test environment
        self.converter = Type_Safe__To__LLM_Tools()

    def test__to_openai_function(self):                                                  # Test OpenAI function format
        class SearchParams(Type_Safe):
            query       : str
            max_results : int = 10
            filters     : Optional[Dict[str, str]] = None

        function_def = self.converter.to_openai_function(                                # Convert to OpenAI format
            SearchParams                                      ,
            'search_documents'                                ,
            'Search through documents with optional filters'
        )

        assert function_def['name'       ] == 'search_documents'                         # Verify function structure
        assert function_def['description'] == 'Search through documents with optional filters'

        parameters = function_def['parameters']
        assert parameters['type'] == 'object'
        assert parameters['properties']['query'       ] == {'default': ''  , 'type': 'string' }
        assert parameters['properties']['max_results' ] == {'default': 10  , 'type': 'integer', }
        assert parameters['properties']['filters'     ] == {'type': 'object', 'additionalProperties': {'type': 'string'}, 'nullable': True}

    def test__to_anthropic_tool(self):                                                   # Test Anthropic Claude format
        class AnalyzeParams(Type_Safe):
            text     : str
            language : str = 'en'
            detailed : bool = False

        tool_def = self.converter.to_anthropic_tool(                                     # Convert to Anthropic format
            AnalyzeParams                        ,
            'analyze_text'                       ,
            'Analyze text in specified language'
        )

        assert tool_def['name'       ] == 'analyze_text'                                 # Verify tool structure
        assert tool_def['description'] == 'Analyze text in specified language'

        input_schema = tool_def['input_schema']
        assert input_schema['type'] == 'object'
        assert input_schema['properties']['text'    ] == {'type': 'string', 'default': ''    }
        assert input_schema['properties']['language'] == {'type': 'string', 'default': 'en'  }
        assert input_schema['properties']['detailed'] == {'type': 'boolean', 'default': False}

    def test__to_langchain_tool(self):                                                   # Test LangChain format
        class ProcessParams(Type_Safe):
            input_data : str
            format     : str = 'json'

        tool_def = self.converter.to_langchain_tool(                                     # Convert to LangChain format
            ProcessParams                    ,
            'process_data'                   ,
            'Process data in specified format',
            return_direct=True
        )

        assert tool_def['name'         ] == 'process_data'                               # Verify tool structure
        assert tool_def['description'  ] == 'Process data in specified format'
        assert tool_def['return_direct'] == True

        args_schema = tool_def['args_schema']
        assert args_schema['type'] == 'object'
        assert args_schema['properties']['input_data'] == {'type': 'string', 'default': ''    }
        assert args_schema['properties']['format'    ] == {'type': 'string', 'default': 'json'}

    def test__to_gemini_function(self):                                                  # Test Gemini function format
        class CalculateParams(Type_Safe):
            value1    : float
            value2    : float
            operation : str

        function_def = self.converter.to_gemini_function(                                # Convert to Gemini format
            CalculateParams                    ,
            'calculate'                        ,
            'Perform calculation on two values'
        )

        assert function_def['name'       ] == 'calculate'                                # Verify function structure
        assert function_def['description'] == 'Perform calculation on two values'

        parameters = function_def['parameters']
        assert parameters['type'] == 'object'
        assert parameters['properties']['value1'   ] == {'type': 'number', 'default': 0.0 }               # Gemini uses 'number' not 'float'
        assert parameters['properties']['value2'   ] == {'type': 'number', 'default': 0.0 }
        assert parameters['properties']['operation'] == {'type': 'string', 'default': ''  }

    def test__to_bedrock_tool(self):                                                     # Test AWS Bedrock format
        class TranslateParams(Type_Safe):
            text        : str
            source_lang : str
            target_lang : str

        tool_def = self.converter.to_bedrock_tool(                                       # Convert to Bedrock format
            TranslateParams           ,
            'translate_text'          ,
            'Translate text between languages'
        )

        assert tool_def['toolSpec']['name'       ] == 'translate_text'                   # Verify tool structure
        assert tool_def['toolSpec']['description'] == 'Translate text between languages'

        input_schema = tool_def['toolSpec']['inputSchema']['json']
        assert input_schema['type'] == 'object'
        assert input_schema['properties']['text'       ] == {'type': 'string', 'default': ''}
        assert input_schema['properties']['source_lang'] == {'type': 'string', 'default': ''}
        assert input_schema['properties']['target_lang'] == {'type': 'string', 'default': ''}

    def test__create_function_description(self):                                         # Test human-readable description
        class ComplexParams(Type_Safe):
            required_field  : str
            optional_field  : Optional[str] = None
            default_field   : int = 42
            list_field      : List[str]

        description = self.converter.create_function_description(                        # Generate description
            ComplexParams                  ,
            'complex_function'
        )

        assert description == ( 'Function: complex_function\n'
                                'Parameters:\n'
                                '  - required_field: str (optional)\n'
                                '    default: \n'
                                '  - optional_field: Optional (optional)\n'
                                '  - default_field: int (optional)\n'
                                '    default: 42\n'
                                '  - list_field: List (optional)\n'
                                '    default: list[str] with 0 elements')


    def test__create_example_call(self):                                                 # Test example generation
        class ExampleParams(Type_Safe):
            name    : str
            age     : int
            active  : bool = True
            tags    : List[str]

        example = self.converter.create_example_call(                                    # Generate example call
            ExampleParams                ,
            'example_function'
        )

        assert example['function'] == 'example_function'                                 # Verify example structure
        assert 'args' in example

        args = example['args']
        assert args['name'  ] == 'example_string'                                        # Generated examples
        assert args['age'   ] == 42
        assert args['active'] == True
        assert args['tags'  ] == ['item1', 'item2']

    def test__nested_type_safe_classes(self):                                            # Test nested Type_Safe handling
        class Address(Type_Safe):
            street : str
            city   : str

        class Person(Type_Safe):
            name    : str
            address : Address

        function_def = self.converter.to_openai_function(                                # Convert nested structure
            Person                       ,
            'create_person'              ,
            'Create a person with address'
        )

        parameters = function_def['parameters']
        address_props = parameters['properties']['address']
        assert address_props['type'] == 'object'                                         # Nested object preserved
        assert address_props['properties']['street'] == {'type': 'string', 'default': ''}
        assert address_props['properties']['city'  ] == {'type': 'string', 'default': ''}

    def test__with_descriptions(self):                                                   # Test parameter descriptions
        class DocumentedParams(Type_Safe):
            query : str                                                                  # Search query
            limit : int = 10                                                             # Max results

        # Mock annotations_comments
        DocumentedParams.__annotations_comments__ = {
            'query': 'Search query string',
            'limit': 'Maximum number of results'
        }

        self.converter.include_descriptions = True
        function_def = self.converter.to_openai_function(
            DocumentedParams              ,
            'search'                      ,
            'Search with documentation'
        )

        props = function_def['parameters']['properties']
        assert props['query']['description'] == 'Search query string'                    # Descriptions added
        assert props['limit']['description'] == 'Maximum number of results'

    def test__create_multi_tool_spec(self):                                              # Test multiple tools spec
        class Tool1(Type_Safe):
            param1 : str

        class Tool2(Type_Safe):
            param2 : int

        tool1 = self.converter.to_openai_function(Tool1, 'tool1', 'First tool')
        tool2 = self.converter.to_openai_function(Tool2, 'tool2', 'Second tool')

        multi_spec = self.converter.create_multi_tool_spec([tool1, tool2])               # Create multi-tool spec

        assert multi_spec['version'] == '1.0'                                            # Verify spec structure
        assert multi_spec['count'  ] == 2
        assert len(multi_spec['tools']) == 2
        assert multi_spec['tools'][0]['name'] == 'tool1'
        assert multi_spec['tools'][1]['name'] == 'tool2'

    def test__optional_and_union_types(self):                                            # Test complex type handling
        class ComplexTypes(Type_Safe):
            optional_str  : Optional[str]   = None
            optional_int  : Optional[int]   = None
            list_of_dicts : List[Dict[str, str]]

        function_def = self.converter.to_openai_function(
            ComplexTypes              ,
            'complex'                 ,
            'Handle complex types'
        )

        props = function_def['parameters']['properties']
        assert props['optional_str' ]['nullable'] == True                                # Optional handled
        assert props['optional_int' ]['nullable'] == True
        assert props['list_of_dicts']['type'    ] == 'array'                             # Complex nested type
        assert props['list_of_dicts']['items'   ] == {'type': 'object', 'additionalProperties': {'type': 'string'}}

    def test__singleton_instance(self):                                                  # Test singleton works
        class TestParams(Type_Safe):
            value : str

        function_def = type_safe__to__llm_tools.to_openai_function(                      # Use singleton
            TestParams        ,
            'test'            ,
            'Test function'
        )

        assert function_def['name'] == 'test'
        assert function_def['parameters']['properties']['value'] == {'type': 'string', 'default': ''}

    def test__type_conversion_consistency(self):                                         # Test consistent conversion across formats
        class ConsistentParams(Type_Safe):
            text   : str
            number : int
            flag   : bool

        openai_def    = self.converter.to_openai_function(ConsistentParams, 'test', 'desc')
        anthropic_def = self.converter.to_anthropic_tool(ConsistentParams, 'test', 'desc')
        langchain_def = self.converter.to_langchain_tool(ConsistentParams, 'test', 'desc')

        # All should have same basic structure
        openai_props    = openai_def   ['parameters'  ]['properties']
        anthropic_props = anthropic_def['input_schema']['properties']
        langchain_props = langchain_def['args_schema' ]['properties']

        for props in [openai_props, anthropic_props, langchain_props]:                   # Verify consistency
            assert props['text'  ] == {'type': 'string' , 'default': ''   }
            assert props['number'] == {'type': 'integer', 'default': 0    }
            assert props['flag'  ] == {'type': 'boolean', 'default': False}

    def test__generate_example_value__all_types(self):                                      # Test example generation for all types
        from typing import Set
        class AllTypesParams(Type_Safe):
            a_str   : str
            a_int   : int
            a_float : float
            a_bool  : bool
            a_list  : List[str]
            a_dict  : Dict[str, str]
            a_set   : Set[str]                                                              # use typing.Set for origin detection

        example = self.converter.create_example_call(AllTypesParams, 'test')

        args = example['args']
        assert args['a_str'  ] == 'example_string'                                          # str example
        assert args['a_int'  ] == 42                                                        # int example
        assert args['a_float'] == 3.14                                                      # float example
        assert args['a_bool' ] == True                                                      # bool example
        assert args['a_list' ] == ['item1', 'item2']                                        # list example
        assert args['a_dict' ] == {'key': 'value'}                                          # dict example
        assert args['a_set'  ] == ['unique1', 'unique2']                                    # set example (as list)

    def test__generate_example_value__nested_type_safe(self):                               # Test example for nested Type_Safe
        class Inner(Type_Safe):
            value : str

        class Outer(Type_Safe):
            inner : Inner

        example = self.converter.create_example_call(Outer, 'test')
        assert example['args']['inner'] == {'example': 'data'}                              # nested Type_Safe as dict

    def test__type_to_string__with_typing_generic(self):                                    # Test _type_to_string with typing generics
        result_list = self.converter._type_to_string(List[str])
        result_dict = self.converter._type_to_string(Dict[str, int])

        assert 'List' in result_list or 'list' in result_list                               # typing.List or list
        assert 'Dict' in result_dict or 'dict' in result_dict                               # typing.Dict or dict

    def test__gemini_nested_properties_conversion(self):                                    # Test Gemini type conversion for nested structures
        class Nested(Type_Safe):
            value : int

        class Parent(Type_Safe):
            nested : Nested
            items  : List[Nested]

        function_def = self.converter.to_gemini_function(Parent, 'test', 'Test nested')

        props = function_def['parameters']['properties']
        assert props['nested']['properties']['value']['type'] == 'number'                   # nested int -> number
        assert props['items']['items']['properties']['value']['type'] == 'number'           # items nested int -> number

    def test__create_example_call__uses_default_when_no_example(self):                      # Test default value as example
        class DefaultsOnly(Type_Safe):
            custom_type : object = None                                                     # type with no example generation

        example = self.converter.create_example_call(DefaultsOnly, 'test')
        assert example['args']['custom_type'] is None                                       # uses default value