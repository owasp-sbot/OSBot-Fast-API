# import pytest
# from unittest                                                                        import TestCase
# from osbot_utils.testing.__                                                          import __, __SKIP__
# from osbot_utils.utils.Objects                                                       import base_classes
# from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
# from osbot_fast_api.api.contracts.Contract__Comparator                              import Contract__Comparator
# from osbot_fast_api.api.contracts.Schema__Service__Contract                         import Schema__Service__Contract
# from osbot_fast_api.api.contracts.Schema__Service__Contract                         import Schema__Endpoint__Contract
# from osbot_fast_api.api.contracts.Schema__Service__Contract                         import Schema__Endpoint__Param
# from osbot_fast_api.api.contracts.Schema__Service__Contract                         import Schema__Contract__Diff
# from osbot_fast_api.api.contracts.Schema__Service__Contract                         import Enum__Http__Method
# from osbot_fast_api.api.contracts.Schema__Service__Contract                         import Enum__Param__Location
#
#
# class test_Contract__Comparator(TestCase):
#
#     @classmethod
#     def setUpClass(cls):                                                            # ONE-TIME setup - create test contracts
#         cls.comparator = Contract__Comparator()
#
#         # Create base contract
#         cls.contract_v1 = cls._create_test_contract_v1()
#
#         # Create modified versions for testing
#         cls.contract_v2_non_breaking = cls._create_test_contract_v2_non_breaking()
#         cls.contract_v2_breaking      = cls._create_test_contract_v2_breaking()
#
#     def test__init__(self):                                                         # Test Type_Safe inheritance
#         with Contract__Comparator() as _:
#             assert type(_)         is Contract__Comparator
#             assert base_classes(_) == [Type_Safe, object]
#
#     def test_compare__no_changes(self):                                             # Test comparing identical contracts
#         with self.comparator as _:
#             diff = _.compare(self.contract_v1, self.contract_v1)
#
#             assert type(diff)                  is Schema__Contract__Diff
#             assert diff.has_changes()          == False
#             assert diff.has_breaking_changes() == False
#             assert len(diff.added_endpoints)   == 0
#             assert len(diff.removed_endpoints) == 0
#             assert len(diff.modified_endpoints) == 0
#             assert len(diff.breaking_changes)  == 0
#             assert len(diff.non_breaking_changes) == 0
#
#     def test_compare__non_breaking_changes(self):                                   # Test non-breaking changes
#         with self.comparator as _:
#             diff = _.compare(self.contract_v1, self.contract_v2_non_breaking)
#
#             assert diff.has_changes()          == True
#             assert diff.has_breaking_changes() == False
#             assert len(diff.added_endpoints)    > 0                                 # New endpoints added
#             assert len(diff.removed_endpoints) == 0                                 # No endpoints removed
#             assert len(diff.breaking_changes)  == 0                                 # No breaking changes
#             assert len(diff.non_breaking_changes) > 0                               # Has non-breaking changes
#
#     def test_compare__breaking_changes(self):                                       # Test breaking changes
#         with self.comparator as _:
#             diff = _.compare(self.contract_v1, self.contract_v2_breaking)
#
#             assert diff.has_changes()          == True
#             assert diff.has_breaking_changes() == True
#             assert len(diff.removed_endpoints)  > 0                                 # Endpoints removed (breaking)
#             assert len(diff.breaking_changes)   > 0                                 # Has breaking changes
#
#             # Check specific breaking changes
#             breaking_messages = diff.breaking_changes
#             assert any('Removed endpoint' in msg for msg in breaking_messages)
#
#     def test__create_endpoint_map(self):                                           # Test endpoint map creation
#         with self.comparator as _:
#             endpoints = [ Schema__Endpoint__Contract(operation_id = 'get_user'  ,
#                                                      path_pattern = '/users/{id}',
#                                                      method       = Enum__Http__Method.GET),
#                          Schema__Endpoint__Contract(operation_id = 'create_user',
#                                                    path_pattern = '/users'      ,
#                                                    method       = Enum__Http__Method.POST)]
#
#             endpoint_map = _._create_endpoint_map(endpoints)
#
#             assert type(endpoint_map)     is dict
#             assert 'GET:/users/{id}'     in endpoint_map
#             assert 'POST:/users'          in endpoint_map
#             assert endpoint_map['GET:/users/{id}'].operation_id == 'get_user'
#
#     def test__compare_endpoints__no_changes(self):                                 # Test comparing identical endpoints
#         with self.comparator as _:
#             endpoint = Schema__Endpoint__Contract(operation_id    = 'test'     ,
#                                                   path_pattern    = '/test'    ,
#                                                   method          = Enum__Http__Method.GET,
#                                                   response_schema = 'TestSchema')
#
#             changes = _._compare_endpoints(endpoint, endpoint)
#
#             assert len(changes) == 0                                                # No changes
#
#     def test__compare_endpoints__parameter_changes(self):                          # Test parameter changes
#         with self.comparator as _:
#             endpoint_v1 = Schema__Endpoint__Contract(
#                 operation_id = 'test',
#                 path_pattern = '/test',
#                 method       = Enum__Http__Method.GET,
#                 query_params = [Schema__Endpoint__Param(name     = 'limit'                    ,
#                                                         location = Enum__Param__Location.QUERY,
#                                                         required = False                       ,
#                                                         default  = '10'                        )]
#             )
#
#             endpoint_v2 = Schema__Endpoint__Contract(
#                 operation_id = 'test',
#                 path_pattern = '/test',
#                 method       = Enum__Http__Method.GET,
#                 query_params = [Schema__Endpoint__Param(name     = 'limit'                    ,
#                                                         location = Enum__Param__Location.QUERY,
#                                                         required = True                        ,  # Now required!
#                                                         default  = None                        )]
#             )
#
#             changes = _._compare_endpoints(endpoint_v1, endpoint_v2)
#
#             assert len(changes) > 0
#             assert any('required parameter' in desc for _, desc in changes)
#
#     def test__compare_endpoints__schema_changes(self):                             # Test schema changes
#         with self.comparator as _:
#             endpoint_v1 = Schema__Endpoint__Contract(
#                 operation_id     = 'test',
#                 path_pattern     = '/test',
#                 method           = Enum__Http__Method.GET,
#                 response_schema  = 'ResponseV1',
#                 request_schema   = 'RequestV1'
#             )
#
#             endpoint_v2 = Schema__Endpoint__Contract(
#                 operation_id     = 'test',
#                 path_pattern     = '/test',
#                 method           = Enum__Http__Method.GET,
#                 response_schema  = 'ResponseV2',  # Changed
#                 request_schema   = 'RequestV2'    # Changed
#             )
#
#             changes = _._compare_endpoints(endpoint_v1, endpoint_v2)
#
#             assert len(changes) == 2                                                # Both schemas changed
#             assert any('Response schema changed' in desc for _, desc in changes)
#             assert any('Request schema changed' in desc for _, desc in changes)
#             assert all(change_type == 'breaking' for change_type, _ in changes)    # Both are breaking
#
#     def test__get_required_params(self):                                           # Test required parameter extraction
#         with self.comparator as _:
#             endpoint = Schema__Endpoint__Contract(
#                 operation_id  = 'test',
#                 path_pattern  = '/test/{id}',
#                 method        = Enum__Http__Method.GET,
#                 path_params   = [Schema__Endpoint__Param(name='id', location=Enum__Param__Location.PATH)],
#                 query_params  = [Schema__Endpoint__Param(name='filter', location=Enum__Param__Location.QUERY, required=True),
#                                 Schema__Endpoint__Param(name='sort', location=Enum__Param__Location.QUERY, required=False)],
#                 header_params = [Schema__Endpoint__Param(name='X-API-Key', location=Enum__Param__Location.HEADER, required=True)]
#             )
#
#             required_params = _._get_required_params(endpoint)
#
#             assert type(required_params) is set
#             assert 'id'        in required_params                                   # Path params always required
#             assert 'filter'    in required_params                                   # Explicitly required
#             assert 'sort'      not in required_params                               # Not required
#             assert 'X-API-Key' in required_params                                   # Header required
#
#     def test__find_param(self):                                                    # Test parameter finding
#         with self.comparator as _:
#             endpoint = Schema__Endpoint__Contract(
#                 operation_id = 'test',
#                 path_pattern = '/test/{id}',
#                 method       = Enum__Http__Method.GET,
#                 path_params  = [Schema__Endpoint__Param(name='id', location=Enum__Param__Location.PATH)],
#                 query_params = [Schema__Endpoint__Param(name='filter', location=Enum__Param__Location.QUERY)]
#             )
#
#             id_param = _._find_param(endpoint, 'id')
#             assert id_param is not None
#             assert id_param.name     == 'id'
#             assert id_param.location == Enum__Param__Location.PATH
#
#             filter_param = _._find_param(endpoint, 'filter')
#             assert filter_param is not None
#             assert filter_param.name == 'filter'
#
#             missing_param = _._find_param(endpoint, 'nonexistent')
#             assert missing_param is None
#
#     def test_generate_change_summary(self):                                        # Test change summary generation
#         with self.comparator as _:
#             # Create a diff with various changes
#             diff = Schema__Contract__Diff()
#
#             # Add some changes
#             diff.added_endpoints.append(Schema__Endpoint__Contract(
#                 operation_id = 'new_endpoint',
#                 path_pattern = '/new',
#                 method       = Enum__Http__Method.GET
#             ))
#
#             diff.removed_endpoints.append(Schema__Endpoint__Contract(
#                 operation_id = 'old_endpoint',
#                 path_pattern = '/old',
#                 method       = Enum__Http__Method.DELETE
#             ))
#
#             diff.breaking_changes.append("Removed required parameter 'user_id'")
#             diff.non_breaking_changes.append("Added optional parameter 'filter'")
#
#             summary = _.generate_change_summary(diff)
#
#             assert type(summary) is str
#             assert 'Contract Changes Summary' in summary
#             assert 'Added Endpoints (1)'     in summary
#             assert 'Removed Endpoints (1)'   in summary
#             assert '⚠️  Breaking Changes (1)' in summary
#             assert 'GET /new'                in summary
#             assert 'DELETE /old'             in summary
#
#     def test_generate_change_summary__no_changes(self):                            # Test summary for no changes
#         with self.comparator as _:
#             diff = Schema__Contract__Diff()                                        # Empty diff
#             summary = _.generate_change_summary(diff)
#
#             assert '✓ No changes detected' in summary
#
#     def test_suggest_version_bump__patch(self):                                    # Test patch version bump
#         with self.comparator as _:
#             diff = Schema__Contract__Diff()                                        # No changes
#
#             suggested = _.suggest_version_bump(diff, '1.2.3')
#             assert suggested == '1.2.4'                                            # Patch bump
#
#     def test_suggest_version_bump__minor(self):                                    # Test minor version bump
#         with self.comparator as _:
#             diff = Schema__Contract__Diff()
#             diff.non_breaking_changes.append("Added new endpoint")
#
#             suggested = _.suggest_version_bump(diff, '1.2.3')
#             assert suggested == '1.3.0'                                            # Minor bump
#
#     def test_suggest_version_bump__major(self):                                    # Test major version bump
#         with self.comparator as _:
#             diff = Schema__Contract__Diff()
#             diff.breaking_changes.append("Removed endpoint")
#
#             suggested = _.suggest_version_bump(diff, '1.2.3')
#             assert suggested == '2.0.0'                                            # Major bump
#
#     def test_suggest_version_bump__edge_cases(self):                               # Test version bump edge cases
#         with self.comparator as _:
#             diff = Schema__Contract__Diff()
#
#             # Test with version 0.x.x (pre-release)
#             suggested = _.suggest_version_bump(diff, '0.5.2')
#             assert suggested == '0.5.3'
#
#             # Test with incomplete version
#             suggested = _.suggest_version_bump(diff, '1.0')
#             assert suggested == '1.0.1'
#
#             # Test with just major version
#             suggested = _.suggest_version_bump(diff, '2')
#             assert suggested == '2.0.1'
#
#     def test_compare__error_code_changes(self):                                    # Test error code change detection
#         with self.comparator as _:
#             endpoint_v1 = Schema__Endpoint__Contract(
#                 operation_id = 'test',
#                 path_pattern = '/test',
#                 method       = Enum__Http__Method.GET,
#                 error_codes  = [404, 500]
#             )
#
#             endpoint_v2 = Schema__Endpoint__Contract(
#                 operation_id = 'test',
#                 path_pattern = '/test',
#                 method       = Enum__Http__Method.GET,
#                 error_codes  = [404, 401, 403]                                      # Added 401, 403; removed 500
#             )
#
#             changes = _._compare_endpoints(endpoint_v1, endpoint_v2)
#
#             # Error code changes are non-breaking
#             assert any('Added error codes' in desc for _, desc in changes)
#             assert any('Removed error codes' in desc for _, desc in changes)
#             assert all(change_type == 'non-breaking' for change_type, _ in changes if 'error codes' in changes[1])
#
#     # Helper methods to create test contracts
#     @staticmethod
#     def _create_test_contract_v1():                                                # Create base test contract
#         return Schema__Service__Contract(
#             service_name    = 'TestService',
#             version         = '1.0.0',
#             base_path       = '/api',
#             service_version = '1.0.0',
#             endpoints       = [
#                 Schema__Endpoint__Contract(
#                     operation_id = 'get_user',
#                     path_pattern = '/users/{id}',
#                     method       = Enum__Http__Method.GET,
#                     path_params  = [Schema__Endpoint__Param(name='id', location=Enum__Param__Location.PATH)]
#                 ),
#                 Schema__Endpoint__Contract(
#                     operation_id = 'list_users',
#                     path_pattern = '/users',
#                     method       = Enum__Http__Method.GET,
#                     query_params = [Schema__Endpoint__Param(name='limit', location=Enum__Param__Location.QUERY, required=False, default='10')]
#                 )
#             ]
#         )
#
#     @staticmethod
#     def _create_test_contract_v2_non_breaking():                                   # Create contract with non-breaking changes
#         v1 = test_Contract__Comparator._create_test_contract_v1()
#         # Add new endpoint (non-breaking)
#         v1.endpoints.append(
#             Schema__Endpoint__Contract(
#                 operation_id = 'create_user',
#                 path_pattern = '/users',
#                 method       = Enum__Http__Method.POST
#             )
#         )
#         return v1
#
#     @staticmethod
#     def _create_test_contract_v2_breaking():                                       # Create contract with breaking changes
#         return Schema__Service__Contract(
#             service_name    = 'TestService',
#             version         = '2.0.0',
#             base_path       = '/api',
#             service_version = '2.0.0',
#             endpoints       = [
#                 # Removed list_users endpoint (breaking!)
#                 Schema__Endpoint__Contract(
#                     operation_id = 'get_user',
#                     path_pattern = '/users/{id}',
#                     method       = Enum__Http__Method.GET,
#                     path_params  = [Schema__Endpoint__Param(name='id', location=Enum__Param__Location.PATH)]
#                 )
#             ]
#         )