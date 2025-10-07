import inspect
from typing                                                    import Callable, Set
from osbot_utils.type_safe.Type_Safe                           import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe


class Fast_API__Route__Parser(Type_Safe):

    @type_safe
    def parse_route_path(self, function : Callable                                      # Function to parse into route path
                          ) -> str:                                                     # Returns route path string
        function_name = function.__name__                                               # Get function name
        param_names   = self.extract_param_names(function)                              # Extract parameter names
        segments      = self.parse_function_name_segments(function_name, param_names)   # Parse into segments
        segments = [seg for seg in segments if seg]                                     # Filter out empty segments to avoid // in paths.  Remove empty strings

        if not segments:                                                                # Handle edge case of no segments (e.g., just "__"). If all segments were empty
            segments = ['']                                                             # Use single empty for root '/'

        return '/' + '/'.join(segments)

    @type_safe
    def extract_param_names(self, function : Callable                                   # Function to extract params from
                             ) -> Set[str]:                                             # Returns set of param names
        sig         = inspect.signature(function)                                       # Get function signature
        param_names = set(sig.parameters.keys())                                        # Get all parameter names
        param_names.discard('self')                                                     # Remove 'self' if present
        return param_names

    @type_safe
    def parse_function_name_segments(self, function_name : str       ,                  # Function name to parse
                                           param_names   : Set[str]                     # Set of parameter names
                                      ) -> list:                                        # Returns list of path segments
        parts   = function_name.split('__')                                             # Split on double underscore
        segments = []                                                                   # Initialize segments list

        for i, part in enumerate(parts):                                                # Process each part
            if i == 0:                                                                   # First part is always literal
                segment = self.convert_to_literal_segment(part)                         # Convert underscores to hyphens
                segments.append(segment)
            else:                                                                        # Parts after __ could be params or literals
                part_segments = self.parse_part_with_params(part, param_names)          # Parse part considering params
                segments.extend(part_segments)                                          # Add all segments from this part

        return segments

    @type_safe
    def parse_part_with_params(self, part        : str       ,                          # Part to parse
                                     param_names : Set[str]                             # Set of parameter names
                                ) -> list:                                              # Returns list of segments
        if '_' in part:                                                                 # Part contains underscore
            return self.parse_part_with_underscore(part, param_names)                   # Handle mixed param/literal
        else:                                                                           # Part has no underscore
            return self.parse_simple_part(part, param_names)                            # Handle simple param or literal

    @type_safe
    def parse_part_with_underscore(self, part        : str       ,                      # Part with underscore to parse
                                         param_names : Set[str]                         # Set of parameter names
                                    ) -> list:                                          # Returns list of segments
        # First check if the entire part (with underscores) is a parameter
        if part in param_names:                                                         # Whole part is a parameter
            return [self.create_param_segment(part)]                                    # Return as {param}

        # If not, try the original logic (split on first underscore)
        subparts = part.split('_', 1)                                                   # Split on first underscore only
        first_subpart = subparts[0]                                                     # First part before underscore
        remaining     = subparts[1] if len(subparts) > 1 else ''                        # Remaining after underscore

        segments = []                                                                   # Initialize segments list

        if first_subpart in param_names:                                                # First subpart is a parameter
            segments.append(self.create_param_segment(first_subpart))                   # Add as {param}
            if remaining:                                                                # If there's remaining text
                segments.append(self.convert_to_literal_segment(remaining))             # Add as literal
        else:                                                                           # Not a parameter
            segments.append(self.convert_to_literal_segment(part))                      # Treat whole part as literal

        return segments

    @type_safe
    def parse_simple_part(self, part        : str       ,                               # Simple part to parse
                               param_names : Set[str]                                   # Set of parameter names
                          ) -> list:                                                     # Returns single segment in list
        if part in param_names:                                                         # Part is a parameter name
            return [self.create_param_segment(part)]                                    # Return as {param}
        else:                                                                           # Part is literal
            return [part]                                                               # Return as-is (no underscore conversion)

    @type_safe
    def convert_to_literal_segment(self, text : str                                     # Text to convert to literal
                                   ) -> str:                                             # Returns literal segment
        return text.replace('_', '-')                                                   # Replace underscores with hyphens

    @type_safe
    def create_param_segment(self, param_name : str                                     # Parameter name
                             ) -> str:                                                   # Returns param segment
        return '{' + param_name + '}'                                                   # Wrap in curly braces