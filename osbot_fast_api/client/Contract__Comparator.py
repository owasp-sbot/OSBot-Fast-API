# from typing                                                   import List, Dict
# from osbot_utils.type_safe.Type_Safe                          import Type_Safe
# from osbot_fast_api.client.schemas.Schema__Contract__Diff     import Schema__Contract__Diff
# from osbot_fast_api.client.schemas.Schema__Endpoint__Contract import Schema__Endpoint__Contract
# from osbot_fast_api.client.schemas.Schema__Service__Contract  import Schema__Service__Contract
#
#
# class Contract__Comparator(Type_Safe):
#
#     def compare(self, old_contract : Schema__Service__Contract ,                   # Previous version of contract
#                      new_contract  : Schema__Service__Contract                    # New version of contract
#                ) -> Schema__Contract__Diff:                                       # Compare two contracts and identify changes
#
#         diff = Schema__Contract__Diff()
#                                                                                    # Create lookup dictionaries for efficient comparison
#         old_endpoints_map = self._create_endpoint_map(old_contract.endpoints)
#         new_endpoints_map = self._create_endpoint_map(new_contract.endpoints)
#                                                                                    # Find removed endpoints (breaking change)
#         for key, old_endpoint in old_endpoints_map.items():
#             if key not in new_endpoints_map:
#                 diff.removed_endpoints.append(old_endpoint)
#                 diff.breaking_changes.append(f"Removed endpoint: {old_endpoint.method} {old_endpoint.path_pattern}")
#                                                                                    # Find added endpoints (non-breaking)
#         for key, new_endpoint in new_endpoints_map.items():
#             if key not in old_endpoints_map:
#                 diff.added_endpoints.append(new_endpoint)
#                 diff.non_breaking_changes.append(f"Added endpoint: {new_endpoint.method} {new_endpoint.path_pattern}")
#                                                                                    # Find modified endpoints
#         for key, new_endpoint in new_endpoints_map.items():
#             if key in old_endpoints_map:
#                 old_endpoint = old_endpoints_map[key]
#                 changes      = self._compare_endpoints(old_endpoint, new_endpoint)
#
#                 if changes:
#                     diff.modified_endpoints.append(new_endpoint)
#                                                                                    # Classify changes as breaking or non-breaking
#                     for change_type, description in changes:
#                         if change_type == 'breaking':
#                             diff.breaking_changes.append(description)
#                         else:
#                             diff.non_breaking_changes.append(description)
#
#         return diff
#
#     def _create_endpoint_map(self, endpoints: List[Schema__Endpoint__Contract]    # List of endpoints to map
#                            ) -> Dict[str, Schema__Endpoint__Contract]:           # Create a map of endpoints keyed by method+path for efficient lookup
#
#         endpoint_map = {}
#
#         for endpoint in endpoints:                                               # Use method + path as unique key
#             key               = f"{endpoint.method.value}:{endpoint.path_pattern}"
#             endpoint_map[key] = endpoint
#
#         return endpoint_map
#
#     def _compare_endpoints(self, old_endpoint : Schema__Endpoint__Contract ,      # Old version of endpoint
#                                new_endpoint  : Schema__Endpoint__Contract        # New version of endpoint
#                         ) -> List[Tuple[str, str]]:                             # Compare two endpoints and return list of changes
#
#         changes = []
#                                                                                  # Check if required parameters were removed (breaking)
#         old_required_params = self._get_required_params(old_endpoint)
#         new_required_params = self._get_required_params(new_endpoint)
#
#         for param_name in old_required_params:
#             if param_name not in new_required_params:
#                 changes.append(('breaking', f"Removed required parameter '{param_name}' from {old_endpoint.path_pattern}"))
#                                                                                  # Check if new required parameters were added (breaking for existing clients)
#         for param_name in new_required_params:
#             if param_name not in old_required_params:                          # Check if it has a default value
#                 new_param = self._find_param(new_endpoint, param_name)
#                 if new_param and not new_param.default:
#                     changes.append(('breaking', f"Added required parameter '{param_name}' to {new_endpoint.path_pattern}"))
#                 else:
#                     changes.append(('non-breaking', f"Added optional parameter '{param_name}' to {new_endpoint.path_pattern}"))
#                                                                                  # Check if response schema changed (potentially breaking)
#         if old_endpoint.response_schema != new_endpoint.response_schema:
#             changes.append(('breaking', f"Response schema changed from '{old_endpoint.response_schema}' to '{new_endpoint.response_schema}' for {old_endpoint.path_pattern}"))
#                                                                                  # Check if request schema changed (breaking)
#         if old_endpoint.request_schema != new_endpoint.request_schema:
#             changes.append(('breaking', f"Request schema changed from '{old_endpoint.request_schema}' to '{new_endpoint.request_schema}' for {old_endpoint.path_pattern}"))
#                                                                                  # Check if error codes changed (informational)
#         old_errors = set(old_endpoint.error_codes)
#         new_errors = set(new_endpoint.error_codes)
#
#         if old_errors != new_errors:
#             added_errors   = new_errors - old_errors
#             removed_errors = old_errors - new_errors
#
#             if added_errors:
#                 changes.append(('non-breaking', f"Added error codes {added_errors} to {old_endpoint.path_pattern}"))
#             if removed_errors:
#                 changes.append(('non-breaking', f"Removed error codes {removed_errors} from {old_endpoint.path_pattern}"))
#
#         return changes
#
#     def _get_required_params(self, endpoint: Schema__Endpoint__Contract          # Endpoint to extract params from
#                            ) -> set:                                             # Get set of required parameter names from endpoint
#
#         required = set()
#                                                                                  # Path parameters are always required
#         for param in endpoint.path_params:
#             required.add(param.name)
#                                                                                  # Add required query parameters
#         for param in endpoint.query_params:
#             if param.required:
#                 required.add(param.name)
#                                                                                  # Add required header parameters
#         for param in endpoint.header_params:
#             if param.required:
#                 required.add(param.name)
#
#         return required
#
#     def _find_param(self, endpoint   : Schema__Endpoint__Contract ,             # Endpoint to search in
#                          param_name  : str                                      # Parameter name to find
#                    ):                                                           # Find a parameter by name in endpoint
#                                                                                 # Check all parameter lists
#         for param in endpoint.path_params + endpoint.query_params + endpoint.header_params:
#             if param.name == param_name:
#                 return param
#
#         return None
#
#     def generate_change_summary(self, diff: Schema__Contract__Diff              # Diff to summarize
#                               ) -> str:                                         # Generate human-readable summary of changes
#
#         lines = ["Contract Changes Summary", "=" * 40]
#
#         if diff.added_endpoints:
#             lines.append(f"\nAdded Endpoints ({len(diff.added_endpoints)}):")
#             for endpoint in diff.added_endpoints:
#                 lines.append(f"  + {endpoint.method} {endpoint.path_pattern}")
#
#         if diff.removed_endpoints:
#             lines.append(f"\nRemoved Endpoints ({len(diff.removed_endpoints)}):")
#             for endpoint in diff.removed_endpoints:
#                 lines.append(f"  - {endpoint.method} {endpoint.path_pattern}")
#
#         if diff.modified_endpoints:
#             lines.append(f"\nModified Endpoints ({len(diff.modified_endpoints)}):")
#             for endpoint in diff.modified_endpoints:
#                 lines.append(f"  ~ {endpoint.method} {endpoint.path_pattern}")
#
#         if diff.breaking_changes:
#             lines.append(f"\n⚠️  Breaking Changes ({len(diff.breaking_changes)}):")
#             for change in diff.breaking_changes:
#                 lines.append(f"  • {change}")
#
#         if diff.non_breaking_changes:
#             lines.append(f"\nNon-Breaking Changes ({len(diff.non_breaking_changes)}):")
#             for change in diff.non_breaking_changes:
#                 lines.append(f"  • {change}")
#
#         if not diff.has_changes():
#             lines.append("\n✓ No changes detected")
#
#         return '\n'.join(lines)
#
#     def suggest_version_bump(self, diff            : Schema__Contract__Diff ,    # Changes detected
#                                  current_version   : str                         # Current semantic version
#                            ) -> str:                                             # Suggest version bump based on semantic versioning
#                                                                                 # Parse current version
#         parts = current_version.split('.')
#         major = int(parts[0]) if len(parts) > 0 else 0
#         minor = int(parts[1]) if len(parts) > 1 else 0
#         patch = int(parts[2]) if len(parts) > 2 else 0
#                                                                                 # Determine version bump
#         if diff.has_breaking_changes():                                        # Breaking changes require major version bump
#             return f"{major + 1}.0.0"
#         elif diff.has_changes():                                               # Non-breaking changes require minor version bump
#             return f"{major}.{minor + 1}.0"
#         else:                                                                   # No changes, suggest patch bump
#             return f"{major}.{minor}.{patch + 1}"