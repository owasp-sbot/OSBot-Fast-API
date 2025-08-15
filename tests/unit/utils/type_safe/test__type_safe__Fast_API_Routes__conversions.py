from unittest                                                import TestCase
from pydantic                                                import Field
from osbot_utils.utils.Misc                                  import random_text
from pydantic                                                import BaseModel
from dataclasses                                             import dataclass, field, is_dataclass
from typing                                                  import List, Optional, Dict
from osbot_utils.utils.Objects                               import __, base_types
from osbot_fast_api.api.Fast_API                             import Fast_API
from osbot_fast_api.api.Fast_API__Routes                      import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe                         import Type_Safe
from osbot_fast_api.utils.type_safe.BaseModel__To__Dataclass import basemodel__to__dataclass
from osbot_fast_api.utils.type_safe.BaseModel__To__Type_Safe import basemodel__to__type_safe
from osbot_fast_api.utils.type_safe.Type_Safe__To__BaseModel import type_safe__to__basemodel
from osbot_fast_api.utils.type_safe.Dataclass__To__BaseModel import dataclass__to__basemodel
from osbot_fast_api.utils.type_safe.Type_Safe__To__Dataclass import type_safe__to__dataclass


class test__type_safe__Fast_API__Routes__conversions(TestCase):

    def test__1__with_BaseModel__indirect_support(self):  # Using Pydantic BaseModel with Type_Safe conversion

        class ProductRequest(BaseModel):  # Request model using Pydantic BaseModel
            name        : str            = Field(..., min_length=1, max_length=100)
            description : Optional[str]  = None
            price       : float          = Field(..., gt=0)
            categories  : List[str]      = Field(default_factory=list)
            metadata    : Dict[str, str] = Field(default_factory=dict)
            in_stock    : bool           = True

        class ProductResponse(BaseModel):  # Response model using Pydantic BaseModel
            id          : int
            name        : str
            description : Optional[str]
            price       : float
            categories  : List[str]
            metadata    : Dict[str, str]
            in_stock    : bool
            created_at  : str = "2024-01-01T00:00:00Z"

        class Product_Routes(Fast_API__Routes):
            tag = 'products'

            def create_product(self, product_request: ProductRequest) -> ProductResponse:         # Create a new product
                product_type_safe = basemodel__to__type_safe.convert_instance(product_request)    # Simulate conversion to Type_Safe for internal processing
                assert product_request  .model_dump() ==  product_type_safe.json()                # confirm they are the same
                assert product_type_safe.obj()        == __(description = 'High-performance laptop',
                                                            in_stock    = True,
                                                            name        = 'Laptop Pro Max',
                                                            price       = 1999.99,
                                                            categories  = ['electronics', 'computers'],
                                                            metadata    = __(brand='TechCorp', model='LPM-2024'))
                # Create response
                product_response = ProductResponse( id          = 999,
                                                    name        = product_request.name       ,
                                                    description = product_request.description,
                                                    price       = product_request.price      ,
                                                    categories  = product_request.categories ,
                                                    metadata    = product_request.metadata   ,
                                                    in_stock    = product_request.in_stock   ,
                                                    created_at  = "2024-01-15T10:30:00Z"     )

                return product_response

            def update_product_price(self, product_request: ProductRequest):  # Update product price
                new_price = product_request.price

                # Simulate fetching and updating
                response = ProductResponse( id          = 1000                    ,
                                            name        = "Updated Product"       ,
                                            description = "Price has been updated",
                                            price       = new_price             ,
                                            categories  = ["electronics"],
                                            metadata    = {"last_updated": "today"},
                                            in_stock    = True
                )

                # Convert to Type_Safe and back to demonstrate conversion
                type_safe_version = basemodel__to__type_safe.convert_instance(response)

                # Verify we can access Type_Safe properties
                assert type_safe_version.price  == new_price
                assert type_safe_version.json() == response.model_dump()
                type_safe_version.description   += " (via TypeSafe)"
                type_safe_version.price         += 1000
                base_model_version = type_safe__to__basemodel.convert_instance(type_safe_version)
                return base_model_version

            def setup_routes(self):
                self.add_route_post(self.create_product)
                self.add_route_post(self.update_product_price)

        class Product_Fast_API(Fast_API):
            default_routes = False

            def setup_routes(self):
                self.add_routes(Product_Routes)

        # Test the implementation
        product_api = Product_Fast_API().setup()
        assert product_api.routes_paths() == ['/products/create-product', '/products/update-product-price']

        # Test POST with BaseModel validation
        product_data = { 'name'         : 'Laptop Pro Max',
                         'description'  : 'High-performance laptop',
                         'price'        : 1999.99,
                         'categories'   : ['electronics', 'computers'],
                         'metadata'     : {'brand': 'TechCorp', 'model': 'LPM-2024'},
                         'in_stock'     : True}

        response_1 = product_api.client().post('/products/create-product', json=product_data)
        assert response_1.status_code == 200

        response_data = response_1.json()
        assert response_data['id'        ] == 999
        assert response_data['name'      ] == 'Laptop Pro Max'
        assert response_data['price'     ] == 1999.99
        assert response_data['categories'] == ['electronics', 'computers']
        assert response_data['metadata'  ] == {'brand': 'TechCorp', 'model': 'LPM-2024'}

        product_data['price'] = 10

        response_2 = product_api.client().post('/products/update-product-price', json=product_data)
        assert type(response_2.json()) is dict
        assert response_2.json()       == { 'categories' : ['electronics']          ,
                                            'created_at' : '2024-01-01T00:00:00Z'   ,
                                            'description': 'Price has been updated (via TypeSafe)',
                                            'id'         : 1000                     ,
                                            'in_stock'   : True                     ,
                                            'metadata'   : {'last_updated': 'today' },
                                            'name'       : 'Updated Product'         ,
                                            'price'      : 1010.0                    }


    def test__2__mixed_type_conversions(self):  # Demonstrating conversions between all three types

        # Define models in all three formats
        class CommentTypeSafe(Type_Safe):
            author: str
            content: str
            likes: int = 0

        class CommentBaseModel(BaseModel):
            author: str
            content: str
            likes: int = 0

        @dataclass
        class CommentDataclass:
            author: str
            content: str
            likes: int = 0

        class BlogPostRequest(BaseModel):  # Main request as BaseModel
            title: str
            content: str
            tags: List[str] = []
            published: bool = False

        @dataclass
        class BlogPostResponse:  # Response as dataclass
            id        : int
            title     : str
            content   : str
            tags      : List[str]
            published : bool
            comments  : List[CommentDataclass] = field(default_factory=list)
            views     : int = 0

        class Blog_Routes(Fast_API__Routes):
            tag = 'blog'

            def create_post(self, post_request: BlogPostRequest):       # receive request as BaseModel
                post_type_safe = basemodel__to__type_safe.convert_instance(post_request)            # Convert to Type_Safe for business logic
                comments = []                                                                       # Add some comments using different type systems

                comment1 = CommentTypeSafe( author  = "Alice (Type_Safe)"   ,                       # 1st Comment from Type_Safe
                                            content = "Great post!"         ,
                                            likes   = 5                     )


                comment2 = CommentBaseModel( author  = "Bob (Basemodel)"                ,                       # 2nd Comment from BaseModel
                                             content = "Very informative"   ,
                                             likes   = 3                    )

                comment3 = CommentDataclass(author   = "Charlie (dataclass)",                       #3rd  Comment from Dataclass
                                            content  = "Thanks for sharing" ,
                                            likes    = 7                    )

                assert base_types(comment1)   == [Type_Safe, object]                                # confirm comment1 base types
                assert base_types(comment2)   == [BaseModel, object]                                # confirm comment2 base types
                assert base_types(comment3)   == [object]                                           # confirm comment3 base types
                assert is_dataclass(comment3) is True

                comment1_dataclass = type_safe__to__dataclass.convert_instance(comment1)            # convert 1st comment Type_Safe into a dataclass
                comment2_dataclass = basemodel__to__dataclass.convert_instance(comment2)            # convert 2nd comment Dataclass into a dataclass

                comments.append(comment1_dataclass)
                comments.append(comment2_dataclass)
                comments.append(comment3          )     # this is already a dataclass

                # Create response as dataclass
                response__dataclass = BlogPostResponse(id         = 555                    ,
                                                       title      = post_type_safe.title     ,
                                                       content    = post_type_safe.content   ,
                                                       tags       = post_type_safe.tags      ,
                                                       published  = post_type_safe.published ,
                                                       comments   = comments               ,
                                                       views      = 100                    )            # this is class of List[CommentDataclass]

                assert is_dataclass(response__dataclass) is True
                response_basemodel = dataclass__to__basemodel.convert_instance(response__dataclass)     # Convert to BaseModel
                return response_basemodel                                                               # which we can return directly

            def setup_routes(self):
                self.add_route_post(self.create_post)

        class Blog_Fast_API(Fast_API):
            default_routes = False

            def setup_routes(self):
                self.add_routes(Blog_Routes)

        blog_api      = Blog_Fast_API().setup()
        title         = random_text('Understanding Type Systems'            )
        content       = random_text('A deep dive into Python type systems'  )
        post_data     = { 'title'       : title                             ,
                          'content'     : content                           ,
                          'tags'        : ['python', 'types', 'programming'],
                          'published'   : True                              }
        response      = blog_api.client().post('/blog/create-post', json=post_data)          # Test POST with mixed type conversions
        response_data = response.json()

        assert blog_api.routes_paths() == ['/blog/create-post']
        assert response.status_code    == 200

        assert response_data == {'comments'  : [{'author': 'Alice (Type_Safe)'  , 'content': 'Great post!'       , 'likes': 5},         # created via a Type_Safe object
                                                {'author': 'Bob (Basemodel)'    , 'content': 'Very informative'  , 'likes': 3},         # created via a Basemodel object
                                                {'author': 'Charlie (dataclass)', 'content': 'Thanks for sharing', 'likes': 7}],        # created via a dataclass object
                                 'content'  : content                           ,                                                       # random value
                                 'id'       : 555                               ,                                                       # create from a value inside a dataclass
                                 'published': True                              ,
                                 'tags'     : ['python', 'types', 'programming'],
                                 'title'    : title                             ,                                                       # random value
                                 'views'    : 100                               }

    def test__3__nested_type_conversions(self):  # Testing deeply nested type conversions

        # Nested BaseModel structures
        class Address(BaseModel):
            street  : str
            city    : str
            country : str
            zip_code: Optional[str] = None

        class ContactInfo(BaseModel):
            email    : str
            phone    : Optional[str] = None
            addresses: List[Address] = []

        class CompanyRequest(BaseModel):
            name               : str
            registration_number: str
            contact            : ContactInfo
            departments        : Dict[str, List[str]] = {}  # dept_name -> list of employees

        class CompanyResponse(Type_Safe):  # Response using Type_Safe
            id                  : int
            name                : str
            registration_number : str
            contact             : dict  # Will store converted ContactInfo
            departments         : Dict[str, list[str]]
            verified            : bool = False

        class Company_Routes(Fast_API__Routes):
            tag = 'company'

            def register_company(self, company_request: CompanyRequest              # receive complex nested BaseModel
                                 ) -> dict:                                         # response dict (serialised from Type_Safe instance)

                company_type_safe = basemodel__to__type_safe.convert_instance(company_request)      # Convert to Type_Safe to demonstrate deep conversion

                assert hasattr(company_type_safe, 'contact')                                                            # Verify nested conversion worked
                assert hasattr(company_type_safe, 'departments')


                response_type_safe = CompanyResponse( id                  = 888                                    ,      # Create Type_Safe response
                                                      name                = company_type_safe.name                 ,
                                                      registration_number = company_type_safe.registration_number  ,
                                                      contact             = company_type_safe.contact.json()       ,
                                                      departments         = company_type_safe.departments          ,
                                                      verified            = True                                   )

                response_basemodel = type_safe__to__basemodel.convert_instance(response_type_safe)                      # Convert Type_Safe response to BaseModel for JSON serialization
                return response_basemodel.model_dump()

            def setup_routes(self):
                self.add_route_post(self.register_company)

        class Company_Fast_API(Fast_API):
            default_routes = False

            def setup_routes(self):
                self.add_routes(Company_Routes)

        # Test the implementation
        company_api = Company_Fast_API().setup()
        assert company_api.routes_paths() == ['/company/register-company']

        # Test with deeply nested data
        company_data = { 'name'                 : 'TechCorp International',
                         'registration_number'  : 'TC-2024-001',
                         'contact'              : { 'email'    : 'info@techcorp.com',
                                                    'phone'    : '+1-555-0123',
                                                    'addresses': [{ 'street'  : '123 Tech Boulevard'    ,
                                                                    'city'    : 'San Francisco'         ,
                                                                    'country' : 'USA'                   ,
                                                                    'zip_code': '94105'                 },
                                                                  { 'street'  : '456 Innovation Street' ,
                                                                    'city'    : 'London'                ,
                                                                    'country' : 'UK'                    ,
                                                                    'zip_code': 'EC1A 1BB'              }]},
                        'departments': { 'engineering': ['Alice', 'Bob', 'Charlie'],
                                         'sales'      : ['David', 'Eve'           ],
                                         'hr'         : ['Frank'                  ]}}

        response = company_api.client().post('/company/register-company', json=company_data)

        assert response.status_code == 200

        response_data      = response.json()
        response_type_safe = CompanyResponse.from_json(response_data)
        assert isinstance(response_type_safe, Type_Safe)        is True
        assert response_type_safe.json()                        == response_data
        assert response_data    ['id'         ]                 == 888
        assert response_data    ['verified'   ]                 == True
        assert len(response_data['contact'    ]['addresses'  ]) == 2
        assert response_data    ['departments']['engineering']  == ['Alice', 'Bob', 'Charlie']



    def test__regression__convert_basemodel_list_to_type_safe(self):

        class CompanyRequest(BaseModel):
            departments        : Dict[str, List[str]] = {}  # dept_name -> list of employees

        company_data = { 'departments': {  'engineering': ['Alice', 'Bob', 'Charlie'],
                                           'sales'      : ['David', 'Eve'           ],
                                           'hr'         : ['Frank'                  ]}}

        company_request = CompanyRequest(**company_data)
        assert company_request.model_dump() == company_data

        expected_error = 'Type List cannot be instantiated; use list() instead'
        # with pytest.raises(TypeError, match=re.escape(expected_error)):
        #      basemodel__to__type_safe.convert_instance(company_request)                   # FIXED: BUG: should have worked
        company_type_safe = basemodel__to__type_safe.convert_instance(company_request)      # FIXED: now we don't get an exception
        assert company_type_safe.json() == company_data                                     # confirm data roundtrip
