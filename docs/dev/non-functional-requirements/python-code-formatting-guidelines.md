# Python Code Formatting Guidelines


# Code Formatting Philosophy, Principles and Specification

## Core Principles

### 1. Visual Pattern Recognition
The human brain excels at pattern recognition. This formatting prioritizes creating clear visual patterns that make code structure immediately apparent: 
- Aligned equals signs create vertical lanes that guide the eye
- Consistent comma placement creates predictable rhythm
- Grouped imports with aligned elements form distinct visual blocks

### 2. Information Density vs Readability
While PEP-8 often spreads code across many lines for "readability", this approach recognizes that excessive vertical spread can actually harm comprehension by:

- Forcing more scrolling
- Breaking mental context
- Making patterns harder to spot
- Reducing the amount of code visible at once

### 3. Contextual Proximity
Related information should be visually close to enhance understanding:
- Method documentation appears on the same line as the method definition
- Constructor parameters align vertically to show relationships
- Dictionary key-value pairs maintain close horizontal proximity

## Departures from PEP-8

### Why We Differ

PEP-8's formatting guidelines, while well-intentioned, can create several practical issues:

1. Vertical Space Inefficiency
```python
# PEP-8 style
self.method_call(
parameter_one="value",
    parameter_two="value",
    parameter_three="value"
)

# This style
self.method_call(parameter_one   = "value",
                 parameter_two   = "value",
                 parameter_three = "value")
```

2. Loss of Visual Patterns
```python
# PEP-8 style
assert something.value == expected_value
assert something_else.other_value == other_expected_value
assert third_thing.final_value == final_expected_value

# This style
assert something.value          == expected_value
assert something_else.value     == other_expected_value
assert third_thing.final_value  == final_expected_value
```

3. Broken Visual Context
```python
# PEP-8 style - related elements separated
class SomeClass:
    
    def __init__(
        self,
        param_one,
        param_two
    ):
        self.param_one = param_one
        self.param_two = param_two

# This style - related elements together
class SomeClass:
    def __init__(self, param_one ,
                       param_two  
                   )-> None:
        self.param_one = param_one
        self.param_two = param_two
```

## Benefits of Our Approach

1. Enhanced Scanning
- Column alignment makes it easy to scan for specific elements
- Consistent patterns reduce cognitive load
- Related information stays visually grouped

2. Better Maintainability
- Alignment makes inconsistencies immediately visible
- Format violations stand out visually
- Pattern adherence encourages consistent updates

3. Improved Debugging
- Clear visual structure helps spot logical errors
- Aligned comparisons make value mismatches obvious
- Grouped information reduces context switching

4. Code Review Efficiency
- Structured patterns make changes more apparent
- Consistent formatting reduces noise in diffs
- Visual grouping helps reviewers understand intent

## Real-World Impact

This formatting approach has proven particularly valuable in:
- Large codebases where pattern recognition becomes crucial
- Test files where structure and relationships matter more than PEP-8 conformity
- Code review processes where visual clarity speeds up reviews
- Debugging sessions where quick scanning and pattern recognition are essential

Our philosophy prioritizes human factors and practical utility over strict adherence to style guidelines, recognizing that code is read far more often than it is written.


# Python Code Formatting Specification

## Import Statements
Imports should be aligned with the longest import path, using spaces between major groups:

```python
from unittest                                                           import TestCase
from mgraph_ai.schemas.Schema__MGraph__Node                             import Schema__MGraph__Node
from mgraph_ai.schemas.Schema__MGraph__Node__Config                     import Schema__MGraph__Node__Config
from osbot_utils.type_safe.primitives.safe_str.identifiers.Random_Guid  import Random_Guid
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id import Safe_Id
```

## Method Signature Formatting

### Core Principles

1. **Visual Lanes**
   - Parameters stack vertically
   - Type hints align in their own column
   - Comments align at a consistent position
   - Return types appear on a new line after continuation

2. **Information Density**
   - Each line contains one parameter
   - Type information is immediately visible
   - Purpose is clear from aligned comment
   - Related elements stay visually grouped

### Method Signature Layout

```python
def method_name(self, first_param  : Type1        ,                               # Method purpose comment
                      second_param : Type2        ,                               # Aligned at column 80
                      third_param  : Type3 = None                                 # Default values align with type
                 ) -> ReturnType:                                                # Return on new line
```

Key aspects:
- Method name starts at indent level
- Parameters indent to align with opening parenthesis
- Type hints align in their own column
- Commas align in their own column
- Backslash continuation before return type
- Return type aligns with the first variable name
- Comments align at column 80
- vertical alignment on : , #
- DON'T use this when there is only one param or when (where are no types or default values being set)
- the format for the return type is ") -> {return type}" 

### Parameter Documentation

```python
def complex_operation(self, data_input     : Dict    [str, Any]         ,         # Primary data structure
                            config_options : Optional[Config  ]         ,         # Processing configuration 
                            max_retries    : int                = 3     ,         # Maximum retry attempts
                            timeout_ms     : float              = 1000.0          # Operation timeout
                       ) -> Tuple[Results, Metrics]:             # Returns results and metrics
```

Guidelines:
- Parameter names should be descriptive
- Type hints should be as specific as possible
- Default values align with type hints
- Comments describe parameter purpose
- Return type comment describes what is returned

### Method Groups and Spacing

Methods should be grouped by functionality with clear separation:

```python
    # Core initialization methods
    def __init__(self, config : Config                                           # Initialize with configuration
                  ) -> None:                                                           
        
    def setup(self, options: Dict[str, Any]                                      # Configure processing options
               ) -> bool:                                                              


    # Data validation methods  
    def validate_input(self, data        : InputData        ,                    # Validate input format
                             strict_mode : bool      = False                     # Enable strict validation
                        ) -> ValidationResult:

    def validate_output(self, result     : OutputData ,                          # Validate output format
                              thresholds : Thresholds                            # Validation thresholds
                         ) -> bool:


    # Processing methods
    def process_item(self, item     : DataItem ,                                 # Process single data item
                           settings : Settings                                   # Processing settings
                      ) -> ProcessedItem:
```
Note how the return type name assigns with the variable self, and there is always at least one space before the : and the ,

### Complex Type Signatures

For methods with complex type signatures:

```python
def process_batch(self, items           : List[DataItem]                   ,     # Batch of items to process
                        batch_config     : BatchConfig                      ,     # Batch processing config
                        error_handler    : ErrorHandler                     ,     # Handles processing errors
                        retry_strategy   : Optional[Strategy]               ,     # Retry strategy to use
                        metrics_callback : Callable[[Metrics], None] = None       # Metrics reporting callback
                   ) -> BatchResults:                          # Processed batch results
```

Guidelines:
- Break complex generic types at logical points
- Align nested type parameters
- Keep related type information together
- Document complex types in comments



## Variable Assignment Alignment
Variable assignments should be aligned on the `=` operator:

```python
self.node_id    = Random_Guid()
self.value_type = str
```

## Constructor Calls
Constructor calls should be formatted with aligned parameters, aligned equals signs, and aligned commas:

```python
node_config = Schema__MGraph__Node__Config(node_id    = Random_Guid(),
                                           value_type = str          )

```

Note that:
- The opening parenthesis is on the same line as the constructor call
- Parameters are indented to align with the start of the constructor name
- Equals signs are aligned
- Commas are aligned at the end
- Closing parenthesis is aligned with the commas

## Assert Statements
Assert statements should be aligned on the comparison operator:

```python
assert type(self.node)                                   is Schema__MGraph__Node
assert self.node.node_data                               == self.node_data
assert self.node.value                                   == "test_node_value"
assert len(self.node.attributes)                         == 1
assert self.node.attributes[self.attribute.attribute_id] == self.attribute
```

## Dictionary Literals
Dictionary literals in constructor calls should maintain alignment while using minimal line breaks:

```python
node = Schema__MGraph__Node(attributes = {attr_1.attribute_id: attr_1   ,
                                          attr_2.attribute_id: attr_2}  ,
                            node_config = self.node_data                ,
                            node_type   = Schema__MGraph__Node          ,
                            value       = "test_node_value"             )
```

## Test Class Structure
Test classes should follow this structure:
1. Helper classes (if needed)
2. setUp method
3. Test methods in logical grouping:
   - Basic initialization tests
   - Type safety validation tests
   - Functionality tests
   - Edge cases/special scenarios

Example:
```python
class Simple_Node(Schema__MGraph__Node): pass                                   # Helper class for testing

class test_Schema__MGraph__Node(TestCase):
    
    def setUp(self):                                                            # Initialize test data
        ...

    def test_init(self):                                                        # Tests basic initialization
        ...

    def test_type_safety_validation(self):                                      # Tests type safety
        ...

    def test_different_value_types(self):                                       # Tests various scenarios
        ...
```

## Comments and Documentation
- Inline documentation should be minimal and descriptive
- Comments explaining test cases should be aligned with the code
- Complex test setups should include explanatory comments
- DON'T add docstrings to methods or classes 
- methods or classes can have a comment in the same line as the method return value (column aligned with the other comments on the page)

## Additional Guidelines
- Maximum line length should be reasonable (around 120 characters)
- Group related tests together
- Use consistent spacing between methods (one line)
- Maintain alphabetical ordering of imports when possible
- Use clear and descriptive test method names

This specification aims to enhance code readability while maintaining consistent formatting across the codebase.