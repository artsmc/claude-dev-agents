# Architecture Quality Assessment Report

**Generated**: 2026-02-08T11:18:49.952558
**Project**: architecture-quality-assess
**Path**: /home/mark/.claude/skills/architecture-quality-assess
**Analysis Duration**: 3.51 seconds

---

## Executive Summary

**Overall Score**: 0/100 (Needs Improvement ❌)

**Total Issues**: 129
- **Critical**: 2 🔴
- **High**: 14 🟠
- **Medium**: 96 🟡
- **Low**: 17 🔵

⚠️ **Action Required**: 2 critical issue(s) detected that should be addressed immediately.

---

## 1. Project Overview

**Project Type**: unknown
**Framework**: Unknown

---

## 2. Quality Metrics

### SOLID Principles Compliance

**Overall Score**: 100/100

- **Single Responsibility (SRP)**: 100/100
- **Open/Closed (OCP)**: 100/100
- **Liskov Substitution (LSP)**: 100/100
- **Interface Segregation (ISP)**: 100/100
- **Dependency Inversion (DIP)**: 100/100

### Coupling & Dependencies

- **Average FAN-OUT**: 3.41
- **Max FAN-OUT**: 18
- **Total Modules Analyzed**: 66

**Most Coupled Modules**:

- `scripts/assess.py` (FAN-OUT: 18)
- `lib/analyzers/solid_analyzer.py` (FAN-OUT: 8)
- `lib/analyzers/pattern_analyzer.py` (FAN-OUT: 8)
- `lib/analyzers/layer_analyzer.py` (FAN-OUT: 8)
- `lib/analyzers/__init__.py` (FAN-OUT: 8)

### Code Organization

- **Total Files Analyzed**: 66


---

## 3. Violations by Severity

### 🔴 CRITICAL (2 issues)

#### 1. Circular dependency detected involving 2 modules

**Type**: CircularDependency
**File**: `lib/reporters/json_reporter.py`

**Issue**: A circular dependency cycle was detected:

lib/reporters/json_reporter.py -> lib/reporters/json_reporter.py

Circular dependencies make code harder to understand, test, and maintain. They can cause initialization issues and make refactoring difficult.

**Recommendation**: Break the circular dependency by:
- Extracting shared code to a new module that both can depend on
- Using dependency injection to invert one of the dependencies
- Applying the Dependency Inversion Principle
- Refactoring to establish a clear dependency hierarchy

**Additional Details**:
- Cycle:
  - lib/reporters/json_reporter.py
  - lib/reporters/json_reporter.py
- Cycle Length: 2

#### 2. Circular dependency detected involving 2 modules

**Type**: CircularDependency
**File**: `tests/fixtures/express-api/app.js`

**Issue**: A circular dependency cycle was detected:

tests/fixtures/express-api/app.js -> tests/fixtures/express-api/app.js

Circular dependencies make code harder to understand, test, and maintain. They can cause initialization issues and make refactoring difficult.

**Recommendation**: Break the circular dependency by:
- Extracting shared code to a new module that both can depend on
- Using dependency injection to invert one of the dependencies
- Applying the Dependency Inversion Principle
- Refactoring to establish a clear dependency hierarchy

**Additional Details**:
- Cycle:
  - tests/fixtures/express-api/app.js
  - tests/fixtures/express-api/app.js
- Cycle Length: 2

### 🟠 HIGH (14 issues)

#### 1. Long method detected: '_check_database_patterns' (115 lines)

**Type**: LongMethod
**File**: `lib/analyzers/layer_analyzer.py`
**Line**: 328

**Issue**: Method '_check_database_patterns' is 115 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _check_database_patterns
- Line Count: 115

#### 2. God Class detected: 'PatternAnalyzer' (594 LOC)

**Type**: SRPViolation
**File**: `lib/analyzers/pattern_analyzer.py`
**Line**: 25

**Issue**: Class 'PatternAnalyzer' has 594 lines of code, exceeding the recommended maximum of 500. Large classes often violate SRP by handling multiple responsibilities.

**Recommendation**: Break down the God Class:
- Identify cohesive groups of methods and fields
- Extract each group into a focused class
- Use composition or delegation patterns
- Consider using the Facade pattern to simplify the interface

**Additional Details**:
- Class Name: PatternAnalyzer
- Lines Of Code: 594
- Threshold: 500

#### 3. God Class detected: 'SOLIDAnalyzer' (652 LOC)

**Type**: SRPViolation
**File**: `lib/analyzers/solid_analyzer.py`
**Line**: 29

**Issue**: Class 'SOLIDAnalyzer' has 652 lines of code, exceeding the recommended maximum of 500. Large classes often violate SRP by handling multiple responsibilities.

**Recommendation**: Break down the God Class:
- Identify cohesive groups of methods and fields
- Extract each group into a focused class
- Use composition or delegation patterns
- Consider using the Facade pattern to simplify the interface

**Additional Details**:
- Class Name: SOLIDAnalyzer
- Lines Of Code: 652
- Threshold: 500

#### 4. Long method detected: '_analyze_srp' (123 lines)

**Type**: LongMethod
**File**: `lib/analyzers/solid_analyzer.py`
**Line**: 119

**Issue**: Method '_analyze_srp' is 123 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _analyze_srp
- Line Count: 123

#### 5. Long method detected: 'to_markdown' (122 lines)

**Type**: LongMethod
**File**: `lib/models/assessment.py`
**Line**: 120

**Issue**: Method 'to_markdown' is 122 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: to_markdown
- Line Count: 122

#### 6. Long method detected: 'get_expected_patterns' (104 lines)

**Type**: LongMethod
**File**: `lib/models/project_type.py`
**Line**: 72

**Issue**: Method 'get_expected_patterns' is 104 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: get_expected_patterns
- Line Count: 104

#### 7. Long method detected: 'extract_imports' (127 lines)

**Type**: LongMethod
**File**: `lib/parsers/javascript_parser.py`
**Line**: 151

**Issue**: Method 'extract_imports' is 127 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: extract_imports
- Line Count: 127

#### 8. Complex method detected: 'extract_imports' (complexity: 19)

**Type**: ComplexMethod
**File**: `lib/parsers/javascript_parser.py`
**Line**: 151

**Issue**: Method 'extract_imports' has high cyclomatic complexity (19). Complex methods with many branches are hard to test and maintain.

**Recommendation**: Reduce method complexity:
- Extract complex conditions into well-named methods
- Use early returns to reduce nesting
- Consider using the Strategy pattern for complex conditionals
- Split the method into smaller, focused methods

**Additional Details**:
- Method Name: extract_imports
- Complexity: 19

#### 9. Complex method detected: '_extract_classes_from_ast' (complexity: 17)

**Type**: ComplexMethod
**File**: `lib/parsers/python_parser.py`
**Line**: 198

**Issue**: Method '_extract_classes_from_ast' has high cyclomatic complexity (17). Complex methods with many branches are hard to test and maintain.

**Recommendation**: Reduce method complexity:
- Extract complex conditions into well-named methods
- Use early returns to reduce nesting
- Consider using the Strategy pattern for complex conditionals
- Split the method into smaller, focused methods

**Additional Details**:
- Method Name: _extract_classes_from_ast
- Complexity: 17

#### 10. God Class detected: 'MarkdownReporter' (515 LOC)

**Type**: SRPViolation
**File**: `lib/reporters/markdown_reporter.py`
**Line**: 20

**Issue**: Class 'MarkdownReporter' has 515 lines of code, exceeding the recommended maximum of 500. Large classes often violate SRP by handling multiple responsibilities.

**Recommendation**: Break down the God Class:
- Identify cohesive groups of methods and fields
- Extract each group into a focused class
- Use composition or delegation patterns
- Consider using the Facade pattern to simplify the interface

**Additional Details**:
- Class Name: MarkdownReporter
- Lines Of Code: 515
- Threshold: 500

#### 11. Excessive coupling detected (FAN-OUT: 18)

**Type**: HighCoupling
**File**: `scripts/assess.py`

**Issue**: Module 'scripts/assess.py' depends on 18 other modules, indicating tight coupling. High FAN-OUT makes the module fragile and difficult to maintain, as changes in dependencies may require changes here.

Dependencies:
  - argparse
  - datetime
  - hashlib
  - lib/analyzers/base.py
  - lib/analyzers/solid_analyzer.py
  - lib/graph/dependency_graph.py
  - lib/models/assessment.py
  - lib/models/config.py
  - lib/models/metrics.py
  - lib/models/violation.py
  ... and 8 more

**Recommendation**: Consider refactoring to reduce dependencies:
- Extract shared logic to dedicated utility modules
- Apply Dependency Inversion Principle (depend on abstractions)
- Use dependency injection to reduce direct coupling
- Break down large module into smaller, focused modules

**Additional Details**:
- Fan Out: 18
- Fan In: 2
- Instability: 0.9
- Dependencies:
  - typing
  - sys
  - lib/reporters/json_reporter.py
  - lib/analyzers/solid_analyzer.py
  - lib/graph/dependency_graph.py
  - lib/models/assessment.py
  - lib/analyzers/base.py
  - hashlib
  - logging
  - lib/models/metrics.py
  - lib/parsers/javascript_parser.py
  - lib/parsers/base.py
  - scripts/detect_project_type.py
  - datetime
  - pathlib
  - argparse
  - lib/models/config.py
  - lib/models/violation.py

#### 12. Long method detected: 'main' (161 lines)

**Type**: LongMethod
**File**: `scripts/assess.py`
**Line**: 542

**Issue**: Method 'main' is 161 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: main
- Line Count: 161

#### 13. Complex method detected: 'main' (complexity: 18)

**Type**: ComplexMethod
**File**: `scripts/assess.py`
**Line**: 542

**Issue**: Method 'main' has high cyclomatic complexity (18). Complex methods with many branches are hard to test and maintain.

**Recommendation**: Reduce method complexity:
- Extract complex conditions into well-named methods
- Use early returns to reduce nesting
- Consider using the Strategy pattern for complex conditionals
- Split the method into smaller, focused methods

**Additional Details**:
- Method Name: main
- Complexity: 18

#### 14. Direct ORM usage in presentation layer

**Type**: DirectDatabaseAccess
**File**: `tests/fixtures/express-api/routes/users.js`
**Line**: 10

**Issue**: Direct ORM usage was detected in the presentation layer. Database operations should be encapsulated in the data layer following the Repository pattern.

**Recommendation**: Refactor database access:
- Create repository methods for data operations
- Use dependency injection to provide repositories
- Keep ORM models and queries in the data layer only

**Additional Details**:
- Layer: presentation
- Pattern Type: orm_usage
- Matched Text: .delete(

### 🟡 MEDIUM (96 issues)

#### 1. High coupling detected (FAN-OUT: 8)

**Type**: HighCoupling
**File**: `lib/analyzers/__init__.py`

**Issue**: Module 'lib/analyzers/__init__.py' depends on 8 other modules, indicating tight coupling. High FAN-OUT makes the module fragile and difficult to maintain, as changes in dependencies may require changes here.

Dependencies:
  - .drift_analyzer
  - lib/analyzers/base.py
  - lib/analyzers/coupling_analyzer.py
  - lib/analyzers/layer_analyzer.py
  - lib/analyzers/pattern_analyzer.py
  - lib/analyzers/solid_analyzer.py
  - logging
  - typing

**Recommendation**: Consider refactoring to reduce dependencies:
- Extract shared logic to dedicated utility modules
- Apply Dependency Inversion Principle (depend on abstractions)
- Use dependency injection to reduce direct coupling
- Break down large module into smaller, focused modules

**Additional Details**:
- Fan Out: 8
- Fan In: 0
- Instability: 1.0
- Dependencies:
  - typing
  - lib/analyzers/solid_analyzer.py
  - lib/analyzers/base.py
  - logging
  - lib/analyzers/coupling_analyzer.py
  - .drift_analyzer
  - lib/analyzers/layer_analyzer.py
  - lib/analyzers/pattern_analyzer.py

#### 2. High coupling detected (FAN-OUT: 7)

**Type**: HighCoupling
**File**: `lib/analyzers/base.py`

**Issue**: Module 'lib/analyzers/base.py' depends on 7 other modules, indicating tight coupling. High FAN-OUT makes the module fragile and difficult to maintain, as changes in dependencies may require changes here.

Dependencies:
  - ..models.config
  - ..models.violation
  - abc
  - dataclasses
  - logging
  - pathlib
  - typing

**Recommendation**: Consider refactoring to reduce dependencies:
- Extract shared logic to dedicated utility modules
- Apply Dependency Inversion Principle (depend on abstractions)
- Use dependency injection to reduce direct coupling
- Break down large module into smaller, focused modules

**Additional Details**:
- Fan Out: 7
- Fan In: 13
- Instability: 0.35
- Dependencies:
  - typing
  - dataclasses
  - ..models.config
  - ..models.violation
  - logging
  - abc
  - pathlib

#### 3. Class 'BaseAnalyzer' has too many methods (12)

**Type**: SRPViolation
**File**: `lib/analyzers/base.py`
**Line**: 58

**Issue**: Class 'BaseAnalyzer' has 12 methods, exceeding the recommended maximum of 10. This suggests the class may have multiple responsibilities.

**Recommendation**: Refactor to follow Single Responsibility Principle:
- Identify distinct responsibilities in the class
- Extract related methods into separate classes
- Use composition to combine focused classes
- Consider applying the Extract Class refactoring

**Additional Details**:
- Class Name: BaseAnalyzer
- Method Count: 12
- Threshold: 10

#### 4. Fat interface: 'BaseAnalyzer' has 12 methods

**Type**: ISPViolation
**File**: `lib/analyzers/base.py`
**Line**: 58

**Issue**: Interface/base class 'BaseAnalyzer' has 12 methods, exceeding the recommended maximum of 10. Large interfaces force clients to depend on methods they don't use.

**Recommendation**: Split the fat interface:
- Identify distinct groups of related methods
- Create smaller, focused interfaces for each group
- Use interface inheritance to compose larger interfaces if needed
- Apply the Interface Segregation Principle

**Additional Details**:
- Class Name: BaseAnalyzer
- Method Count: 12
- Threshold: 10

#### 5. Class 'BaseAnalyzer' has 3 stub methods

**Type**: ISPViolation
**File**: `lib/analyzers/base.py`
**Line**: 58

**Issue**: Class 'BaseAnalyzer' has multiple stub/empty methods: analyze, get_name, get_description. This suggests the class is forced to implement methods it doesn't need, violating ISP.

**Recommendation**: Apply Interface Segregation:
- Split the interface into smaller, focused interfaces
- Implement only the interfaces needed by this class
- Use composition instead of inheritance if appropriate

**Additional Details**:
- Class Name: BaseAnalyzer
- Stub Methods:
  - analyze
  - get_name
  - get_description

#### 6. Long method detected: 'create_violation' (58 lines)

**Type**: LongMethod
**File**: `lib/analyzers/base.py`
**Line**: 141

**Issue**: Method 'create_violation' is 58 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: create_violation
- Line Count: 58

#### 7. High coupling detected (FAN-OUT: 7)

**Type**: HighCoupling
**File**: `lib/analyzers/coupling_analyzer.py`

**Issue**: Module 'lib/analyzers/coupling_analyzer.py' depends on 7 other modules, indicating tight coupling. High FAN-OUT makes the module fragile and difficult to maintain, as changes in dependencies may require changes here.

Dependencies:
  - ..graph.dependency_graph
  - ..models.config
  - ..models.violation
  - lib/analyzers/base.py
  - logging
  - pathlib
  - typing

**Recommendation**: Consider refactoring to reduce dependencies:
- Extract shared logic to dedicated utility modules
- Apply Dependency Inversion Principle (depend on abstractions)
- Use dependency injection to reduce direct coupling
- Break down large module into smaller, focused modules

**Additional Details**:
- Fan Out: 7
- Fan In: 2
- Instability: 0.7777777777777778
- Dependencies:
  - typing
  - ..graph.dependency_graph
  - ..models.config
  - lib/analyzers/base.py
  - logging
  - ..models.violation
  - pathlib

#### 8. Long method detected: '_analyze_fan_out' (67 lines)

**Type**: LongMethod
**File**: `lib/analyzers/coupling_analyzer.py`
**Line**: 111

**Issue**: Method '_analyze_fan_out' is 67 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _analyze_fan_out
- Line Count: 67

#### 9. Long method detected: '_analyze_fan_in' (62 lines)

**Type**: LongMethod
**File**: `lib/analyzers/coupling_analyzer.py`
**Line**: 179

**Issue**: Method '_analyze_fan_in' is 62 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _analyze_fan_in
- Line Count: 62

#### 10. Long method detected: '_analyze_circular_dependencies' (59 lines)

**Type**: LongMethod
**File**: `lib/analyzers/coupling_analyzer.py`
**Line**: 242

**Issue**: Method '_analyze_circular_dependencies' is 59 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _analyze_circular_dependencies
- Line Count: 59

#### 11. Long method detected: '_analyze_deep_chains' (65 lines)

**Type**: LongMethod
**File**: `lib/analyzers/coupling_analyzer.py`
**Line**: 302

**Issue**: Method '_analyze_deep_chains' is 65 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _analyze_deep_chains
- Line Count: 65

#### 12. High coupling detected (FAN-OUT: 8)

**Type**: HighCoupling
**File**: `lib/analyzers/layer_analyzer.py`

**Issue**: Module 'lib/analyzers/layer_analyzer.py' depends on 8 other modules, indicating tight coupling. High FAN-OUT makes the module fragile and difficult to maintain, as changes in dependencies may require changes here.

Dependencies:
  - ..graph.dependency_graph
  - ..models.config
  - ..models.violation
  - lib/analyzers/base.py
  - logging
  - pathlib
  - tests/fixtures/django-app/manage.py
  - typing

**Recommendation**: Consider refactoring to reduce dependencies:
- Extract shared logic to dedicated utility modules
- Apply Dependency Inversion Principle (depend on abstractions)
- Use dependency injection to reduce direct coupling
- Break down large module into smaller, focused modules

**Additional Details**:
- Fan Out: 8
- Fan In: 2
- Instability: 0.8
- Dependencies:
  - tests/fixtures/django-app/manage.py
  - ..graph.dependency_graph
  - typing
  - ..models.config
  - lib/analyzers/base.py
  - logging
  - ..models.violation
  - pathlib

#### 13. Long method detected: '_analyze_layer_dependencies' (72 lines)

**Type**: LongMethod
**File**: `lib/analyzers/layer_analyzer.py`
**Line**: 444

**Issue**: Method '_analyze_layer_dependencies' is 72 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _analyze_layer_dependencies
- Line Count: 72

#### 14. High coupling detected (FAN-OUT: 8)

**Type**: HighCoupling
**File**: `lib/analyzers/pattern_analyzer.py`

**Issue**: Module 'lib/analyzers/pattern_analyzer.py' depends on 8 other modules, indicating tight coupling. High FAN-OUT makes the module fragile and difficult to maintain, as changes in dependencies may require changes here.

Dependencies:
  - ..models.violation
  - collections
  - lib/analyzers/base.py
  - logging
  - pathlib
  - tests/fixtures/django-app/manage.py
  - tests/fixtures/python-fastapi/app/__init__.py
  - typing

**Recommendation**: Consider refactoring to reduce dependencies:
- Extract shared logic to dedicated utility modules
- Apply Dependency Inversion Principle (depend on abstractions)
- Use dependency injection to reduce direct coupling
- Break down large module into smaller, focused modules

**Additional Details**:
- Fan Out: 8
- Fan In: 2
- Instability: 0.8
- Dependencies:
  - tests/fixtures/django-app/manage.py
  - typing
  - lib/analyzers/base.py
  - logging
  - ..models.violation
  - collections
  - tests/fixtures/python-fastapi/app/__init__.py
  - pathlib

#### 15. Class 'PatternAnalyzer' has too many methods (12)

**Type**: SRPViolation
**File**: `lib/analyzers/pattern_analyzer.py`
**Line**: 25

**Issue**: Class 'PatternAnalyzer' has 12 methods, exceeding the recommended maximum of 10. This suggests the class may have multiple responsibilities.

**Recommendation**: Refactor to follow Single Responsibility Principle:
- Identify distinct responsibilities in the class
- Extract related methods into separate classes
- Use composition to combine focused classes
- Consider applying the Extract Class refactoring

**Additional Details**:
- Class Name: PatternAnalyzer
- Method Count: 12
- Threshold: 10

#### 16. Fat interface: 'PatternAnalyzer' has 12 methods

**Type**: ISPViolation
**File**: `lib/analyzers/pattern_analyzer.py`
**Line**: 25

**Issue**: Interface/base class 'PatternAnalyzer' has 12 methods, exceeding the recommended maximum of 10. Large interfaces force clients to depend on methods they don't use.

**Recommendation**: Split the fat interface:
- Identify distinct groups of related methods
- Create smaller, focused interfaces for each group
- Use interface inheritance to compose larger interfaces if needed
- Apply the Interface Segregation Principle

**Additional Details**:
- Class Name: PatternAnalyzer
- Method Count: 12
- Threshold: 10

#### 17. Long method detected: 'analyze' (57 lines)

**Type**: LongMethod
**File**: `lib/analyzers/pattern_analyzer.py`
**Line**: 71

**Issue**: Method 'analyze' is 57 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: analyze
- Line Count: 57

#### 18. Long method detected: '_detect_magic_numbers' (65 lines)

**Type**: LongMethod
**File**: `lib/analyzers/pattern_analyzer.py`
**Line**: 129

**Issue**: Method '_detect_magic_numbers' is 65 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _detect_magic_numbers
- Line Count: 65

#### 19. Long method detected: '_detect_long_methods' (56 lines)

**Type**: LongMethod
**File**: `lib/analyzers/pattern_analyzer.py`
**Line**: 195

**Issue**: Method '_detect_long_methods' is 56 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _detect_long_methods
- Line Count: 56

#### 20. Long method detected: '_detect_complex_methods' (54 lines)

**Type**: LongMethod
**File**: `lib/analyzers/pattern_analyzer.py`
**Line**: 252

**Issue**: Method '_detect_complex_methods' is 54 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _detect_complex_methods
- Line Count: 54

#### 21. Long method detected: '_detect_dead_code' (65 lines)

**Type**: LongMethod
**File**: `lib/analyzers/pattern_analyzer.py`
**Line**: 307

**Issue**: Method '_detect_dead_code' is 65 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _detect_dead_code
- Line Count: 65

#### 22. Long method detected: '_detect_factory_opportunities' (65 lines)

**Type**: LongMethod
**File**: `lib/analyzers/pattern_analyzer.py`
**Line**: 373

**Issue**: Method '_detect_factory_opportunities' is 65 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _detect_factory_opportunities
- Line Count: 65

#### 23. Long method detected: '_detect_strategy_opportunities' (67 lines)

**Type**: LongMethod
**File**: `lib/analyzers/pattern_analyzer.py`
**Line**: 439

**Issue**: Method '_detect_strategy_opportunities' is 67 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _detect_strategy_opportunities
- Line Count: 67

#### 24. Long method detected: '_detect_singleton_misuse' (71 lines)

**Type**: LongMethod
**File**: `lib/analyzers/pattern_analyzer.py`
**Line**: 507

**Issue**: Method '_detect_singleton_misuse' is 71 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _detect_singleton_misuse
- Line Count: 71

#### 25. High coupling detected (FAN-OUT: 8)

**Type**: HighCoupling
**File**: `lib/analyzers/solid_analyzer.py`

**Issue**: Module 'lib/analyzers/solid_analyzer.py' depends on 8 other modules, indicating tight coupling. High FAN-OUT makes the module fragile and difficult to maintain, as changes in dependencies may require changes here.

Dependencies:
  - ..models.violation
  - collections
  - lib/analyzers/base.py
  - logging
  - pathlib
  - tests/fixtures/django-app/manage.py
  - tests/fixtures/python-fastapi/app/__init__.py
  - typing

**Recommendation**: Consider refactoring to reduce dependencies:
- Extract shared logic to dedicated utility modules
- Apply Dependency Inversion Principle (depend on abstractions)
- Use dependency injection to reduce direct coupling
- Break down large module into smaller, focused modules

**Additional Details**:
- Fan Out: 8
- Fan In: 3
- Instability: 0.7272727272727273
- Dependencies:
  - tests/fixtures/django-app/manage.py
  - typing
  - lib/analyzers/base.py
  - logging
  - ..models.violation
  - collections
  - tests/fixtures/python-fastapi/app/__init__.py
  - pathlib

#### 26. Class 'SOLIDAnalyzer' has too many methods (14)

**Type**: SRPViolation
**File**: `lib/analyzers/solid_analyzer.py`
**Line**: 29

**Issue**: Class 'SOLIDAnalyzer' has 14 methods, exceeding the recommended maximum of 10. This suggests the class may have multiple responsibilities.

**Recommendation**: Refactor to follow Single Responsibility Principle:
- Identify distinct responsibilities in the class
- Extract related methods into separate classes
- Use composition to combine focused classes
- Consider applying the Extract Class refactoring

**Additional Details**:
- Class Name: SOLIDAnalyzer
- Method Count: 14
- Threshold: 10

#### 27. Low cohesion in class 'SOLIDAnalyzer' (LCOM: 0.89)

**Type**: SRPViolation
**File**: `lib/analyzers/solid_analyzer.py`
**Line**: 29

**Issue**: Class 'SOLIDAnalyzer' has low cohesion (LCOM: 0.89). Methods in the class don't share many instance variables, suggesting multiple responsibilities.

**Recommendation**: Improve class cohesion:
- Group methods that work with the same instance variables
- Extract loosely related methods into separate classes
- Ensure each class has a single, well-defined purpose

**Additional Details**:
- Class Name: SOLIDAnalyzer
- Lcom: 0.8901098901098901
- Threshold: 0.8

#### 28. Fat interface: 'SOLIDAnalyzer' has 14 methods

**Type**: ISPViolation
**File**: `lib/analyzers/solid_analyzer.py`
**Line**: 29

**Issue**: Interface/base class 'SOLIDAnalyzer' has 14 methods, exceeding the recommended maximum of 10. Large interfaces force clients to depend on methods they don't use.

**Recommendation**: Split the fat interface:
- Identify distinct groups of related methods
- Create smaller, focused interfaces for each group
- Use interface inheritance to compose larger interfaces if needed
- Apply the Interface Segregation Principle

**Additional Details**:
- Class Name: SOLIDAnalyzer
- Method Count: 14
- Threshold: 10

#### 29. Long method detected: 'analyze' (54 lines)

**Type**: LongMethod
**File**: `lib/analyzers/solid_analyzer.py`
**Line**: 64

**Issue**: Method 'analyze' is 54 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: analyze
- Line Count: 54

#### 30. Long method detected: '_analyze_ocp' (70 lines)

**Type**: LongMethod
**File**: `lib/analyzers/solid_analyzer.py`
**Line**: 243

**Issue**: Method '_analyze_ocp' is 70 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _analyze_ocp
- Line Count: 70

#### 31. Long method detected: '_analyze_lsp' (75 lines)

**Type**: LongMethod
**File**: `lib/analyzers/solid_analyzer.py`
**Line**: 314

**Issue**: Method '_analyze_lsp' is 75 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _analyze_lsp
- Line Count: 75

#### 32. Long method detected: '_analyze_isp' (97 lines)

**Type**: LongMethod
**File**: `lib/analyzers/solid_analyzer.py`
**Line**: 390

**Issue**: Method '_analyze_isp' is 97 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _analyze_isp
- Line Count: 97

#### 33. Long method detected: '_analyze_dip' (60 lines)

**Type**: LongMethod
**File**: `lib/analyzers/solid_analyzer.py`
**Line**: 488

**Issue**: Method '_analyze_dip' is 60 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _analyze_dip
- Line Count: 60

#### 34. Complex method detected: '_calculate_lcom' (complexity: 11)

**Type**: ComplexMethod
**File**: `lib/analyzers/solid_analyzer.py`
**Line**: 565

**Issue**: Method '_calculate_lcom' has high cyclomatic complexity (11). Complex methods with many branches are hard to test and maintain.

**Recommendation**: Reduce method complexity:
- Extract complex conditions into well-named methods
- Use early returns to reduce nesting
- Consider using the Strategy pattern for complex conditionals
- Split the method into smaller, focused methods

**Additional Details**:
- Method Name: _calculate_lcom
- Complexity: 11

#### 35. Class 'DependencyGraph' has too many methods (16)

**Type**: SRPViolation
**File**: `lib/graph/dependency_graph.py`
**Line**: 69

**Issue**: Class 'DependencyGraph' has 16 methods, exceeding the recommended maximum of 10. This suggests the class may have multiple responsibilities.

**Recommendation**: Refactor to follow Single Responsibility Principle:
- Identify distinct responsibilities in the class
- Extract related methods into separate classes
- Use composition to combine focused classes
- Consider applying the Extract Class refactoring

**Additional Details**:
- Class Name: DependencyGraph
- Method Count: 16
- Threshold: 10

#### 36. Fat interface: 'DependencyGraph' has 16 methods

**Type**: ISPViolation
**File**: `lib/graph/dependency_graph.py`
**Line**: 69

**Issue**: Interface/base class 'DependencyGraph' has 16 methods, exceeding the recommended maximum of 10. Large interfaces force clients to depend on methods they don't use.

**Recommendation**: Split the fat interface:
- Identify distinct groups of related methods
- Create smaller, focused interfaces for each group
- Use interface inheritance to compose larger interfaces if needed
- Apply the Interface Segregation Principle

**Additional Details**:
- Class Name: DependencyGraph
- Method Count: 16
- Threshold: 10

#### 37. Long method detected: 'detect_cycles' (51 lines)

**Type**: LongMethod
**File**: `lib/graph/dependency_graph.py`
**Line**: 175

**Issue**: Method 'detect_cycles' is 51 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: detect_cycles
- Line Count: 51

#### 38. Low cohesion in class 'ProjectMetrics' (LCOM: 0.83)

**Type**: SRPViolation
**File**: `lib/models/metrics.py`
**Line**: 125

**Issue**: Class 'ProjectMetrics' has low cohesion (LCOM: 0.83). Methods in the class don't share many instance variables, suggesting multiple responsibilities.

**Recommendation**: Improve class cohesion:
- Group methods that work with the same instance variables
- Extract loosely related methods into separate classes
- Ensure each class has a single, well-defined purpose

**Additional Details**:
- Class Name: ProjectMetrics
- Lcom: 0.8333333333333334
- Threshold: 0.8

#### 39. Low cohesion in class 'ProjectType' (LCOM: 1.00)

**Type**: SRPViolation
**File**: `lib/models/project_type.py`
**Line**: 15

**Issue**: Class 'ProjectType' has low cohesion (LCOM: 1.00). Methods in the class don't share many instance variables, suggesting multiple responsibilities.

**Recommendation**: Improve class cohesion:
- Group methods that work with the same instance variables
- Extract loosely related methods into separate classes
- Ensure each class has a single, well-defined purpose

**Additional Details**:
- Class Name: ProjectType
- Lcom: 1.0
- Threshold: 0.8

#### 40. Low cohesion in class 'BaseParser' (LCOM: 0.93)

**Type**: SRPViolation
**File**: `lib/parsers/base.py`
**Line**: 127

**Issue**: Class 'BaseParser' has low cohesion (LCOM: 0.93). Methods in the class don't share many instance variables, suggesting multiple responsibilities.

**Recommendation**: Improve class cohesion:
- Group methods that work with the same instance variables
- Extract loosely related methods into separate classes
- Ensure each class has a single, well-defined purpose

**Additional Details**:
- Class Name: BaseParser
- Lcom: 0.9333333333333333
- Threshold: 0.8

#### 41. Class 'BaseParser' has 3 stub methods

**Type**: ISPViolation
**File**: `lib/parsers/base.py`
**Line**: 127

**Issue**: Class 'BaseParser' has multiple stub/empty methods: parse_file, extract_imports, get_supported_extensions. This suggests the class is forced to implement methods it doesn't need, violating ISP.

**Recommendation**: Apply Interface Segregation:
- Split the interface into smaller, focused interfaces
- Implement only the interfaces needed by this class
- Use composition instead of inheritance if appropriate

**Additional Details**:
- Class Name: BaseParser
- Stub Methods:
  - parse_file
  - extract_imports
  - get_supported_extensions

#### 42. Low cohesion in class 'JavaScriptParser' (LCOM: 0.97)

**Type**: SRPViolation
**File**: `lib/parsers/javascript_parser.py`
**Line**: 31

**Issue**: Class 'JavaScriptParser' has low cohesion (LCOM: 0.97). Methods in the class don't share many instance variables, suggesting multiple responsibilities.

**Recommendation**: Improve class cohesion:
- Group methods that work with the same instance variables
- Extract loosely related methods into separate classes
- Ensure each class has a single, well-defined purpose

**Additional Details**:
- Class Name: JavaScriptParser
- Lcom: 0.9722222222222222
- Threshold: 0.8

#### 43. Factory pattern opportunity: 'ImportStatement' instantiated 6 times

**Type**: FactoryOpportunity
**File**: `lib/parsers/javascript_parser.py`
**Line**: 268

**Issue**: Class 'ImportStatement' is instantiated 6 times with complex parameters (5+ arguments). This scattered object creation makes code harder to maintain.

**Recommendation**: Consider using Factory pattern:
- Create a factory class or method to encapsulate object creation
- Centralize complex initialization logic
- Make it easier to change object creation strategy
- Improve testability through dependency injection

**Additional Details**:
- Class Name: ImportStatement
- Instantiation Count: 6

#### 44. Long method detected: 'extract_classes' (52 lines)

**Type**: LongMethod
**File**: `lib/parsers/javascript_parser.py`
**Line**: 279

**Issue**: Method 'extract_classes' is 52 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: extract_classes
- Line Count: 52

#### 45. Long method detected: 'extract_functions' (56 lines)

**Type**: LongMethod
**File**: `lib/parsers/javascript_parser.py`
**Line**: 332

**Issue**: Method 'extract_functions' is 56 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: extract_functions
- Line Count: 56

#### 46. Factory pattern opportunity: 'FunctionDefinition' instantiated 3 times

**Type**: FactoryOpportunity
**File**: `lib/parsers/javascript_parser.py`
**Line**: 351

**Issue**: Class 'FunctionDefinition' is instantiated 3 times with complex parameters (5+ arguments). This scattered object creation makes code harder to maintain.

**Recommendation**: Consider using Factory pattern:
- Create a factory class or method to encapsulate object creation
- Centralize complex initialization logic
- Make it easier to change object creation strategy
- Improve testability through dependency injection

**Additional Details**:
- Class Name: FunctionDefinition
- Instantiation Count: 3

#### 47. Complex method detected: '_parse_parameters' (complexity: 11)

**Type**: ComplexMethod
**File**: `lib/parsers/javascript_parser.py`
**Line**: 434

**Issue**: Method '_parse_parameters' has high cyclomatic complexity (11). Complex methods with many branches are hard to test and maintain.

**Recommendation**: Reduce method complexity:
- Extract complex conditions into well-named methods
- Use early returns to reduce nesting
- Consider using the Strategy pattern for complex conditionals
- Split the method into smaller, focused methods

**Additional Details**:
- Method Name: _parse_parameters
- Complexity: 11

#### 48. Low cohesion in class 'PythonParser' (LCOM: 0.84)

**Type**: SRPViolation
**File**: `lib/parsers/python_parser.py`
**Line**: 31

**Issue**: Class 'PythonParser' has low cohesion (LCOM: 0.84). Methods in the class don't share many instance variables, suggesting multiple responsibilities.

**Recommendation**: Improve class cohesion:
- Group methods that work with the same instance variables
- Extract loosely related methods into separate classes
- Ensure each class has a single, well-defined purpose

**Additional Details**:
- Class Name: PythonParser
- Lcom: 0.8444444444444444
- Threshold: 0.8

#### 49. Long method detected: '_extract_classes_from_ast' (68 lines)

**Type**: LongMethod
**File**: `lib/parsers/python_parser.py`
**Line**: 198

**Issue**: Method '_extract_classes_from_ast' is 68 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _extract_classes_from_ast
- Line Count: 68

#### 50. Long method detected: '_build_metrics' (53 lines)

**Type**: LongMethod
**File**: `lib/reporters/json_reporter.py`
**Line**: 138

**Issue**: Method '_build_metrics' is 53 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _build_metrics
- Line Count: 53

#### 51. Long method detected: '_build_recommended_actions' (61 lines)

**Type**: LongMethod
**File**: `lib/reporters/json_reporter.py`
**Line**: 200

**Issue**: Method '_build_recommended_actions' is 61 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _build_recommended_actions
- Line Count: 61

#### 52. Complex method detected: '_build_recommended_actions' (complexity: 12)

**Type**: ComplexMethod
**File**: `lib/reporters/json_reporter.py`
**Line**: 200

**Issue**: Method '_build_recommended_actions' has high cyclomatic complexity (12). Complex methods with many branches are hard to test and maintain.

**Recommendation**: Reduce method complexity:
- Extract complex conditions into well-named methods
- Use early returns to reduce nesting
- Consider using the Strategy pattern for complex conditionals
- Split the method into smaller, focused methods

**Additional Details**:
- Method Name: _build_recommended_actions
- Complexity: 12

#### 53. Long method detected: 'generate_ci_summary' (61 lines)

**Type**: LongMethod
**File**: `lib/reporters/json_reporter.py`
**Line**: 296

**Issue**: Method 'generate_ci_summary' is 61 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: generate_ci_summary
- Line Count: 61

#### 54. Class 'MarkdownReporter' has too many methods (13)

**Type**: SRPViolation
**File**: `lib/reporters/markdown_reporter.py`
**Line**: 20

**Issue**: Class 'MarkdownReporter' has 13 methods, exceeding the recommended maximum of 10. This suggests the class may have multiple responsibilities.

**Recommendation**: Refactor to follow Single Responsibility Principle:
- Identify distinct responsibilities in the class
- Extract related methods into separate classes
- Use composition to combine focused classes
- Consider applying the Extract Class refactoring

**Additional Details**:
- Class Name: MarkdownReporter
- Method Count: 13
- Threshold: 10

#### 55. Fat interface: 'MarkdownReporter' has 13 methods

**Type**: ISPViolation
**File**: `lib/reporters/markdown_reporter.py`
**Line**: 20

**Issue**: Interface/base class 'MarkdownReporter' has 13 methods, exceeding the recommended maximum of 10. Large interfaces force clients to depend on methods they don't use.

**Recommendation**: Split the fat interface:
- Identify distinct groups of related methods
- Create smaller, focused interfaces for each group
- Use interface inheritance to compose larger interfaces if needed
- Apply the Interface Segregation Principle

**Additional Details**:
- Class Name: MarkdownReporter
- Method Count: 13
- Threshold: 10

#### 56. Long method detected: '_executive_summary' (68 lines)

**Type**: LongMethod
**File**: `lib/reporters/markdown_reporter.py`
**Line**: 76

**Issue**: Method '_executive_summary' is 68 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _executive_summary
- Line Count: 68

#### 57. Long method detected: '_metrics_dashboard' (70 lines)

**Type**: LongMethod
**File**: `lib/reporters/markdown_reporter.py`
**Line**: 164

**Issue**: Method '_metrics_dashboard' is 70 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _metrics_dashboard
- Line Count: 70

#### 58. Complex method detected: '_metrics_dashboard' (complexity: 12)

**Type**: ComplexMethod
**File**: `lib/reporters/markdown_reporter.py`
**Line**: 164

**Issue**: Method '_metrics_dashboard' has high cyclomatic complexity (12). Complex methods with many branches are hard to test and maintain.

**Recommendation**: Reduce method complexity:
- Extract complex conditions into well-named methods
- Use early returns to reduce nesting
- Consider using the Strategy pattern for complex conditionals
- Split the method into smaller, focused methods

**Additional Details**:
- Method Name: _metrics_dashboard
- Complexity: 12

#### 59. Long method detected: '_violations_by_severity' (66 lines)

**Type**: LongMethod
**File**: `lib/reporters/markdown_reporter.py`
**Line**: 235

**Issue**: Method '_violations_by_severity' is 66 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _violations_by_severity
- Line Count: 66

#### 60. Long method detected: '_violations_by_dimension' (63 lines)

**Type**: LongMethod
**File**: `lib/reporters/markdown_reporter.py`
**Line**: 302

**Issue**: Method '_violations_by_dimension' is 63 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _violations_by_dimension
- Line Count: 63

#### 61. Long method detected: '_recommended_actions' (73 lines)

**Type**: LongMethod
**File**: `lib/reporters/markdown_reporter.py`
**Line**: 366

**Issue**: Method '_recommended_actions' is 73 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _recommended_actions
- Line Count: 73

#### 62. Class 'TaskGenerator' has too many methods (11)

**Type**: SRPViolation
**File**: `lib/reporters/task_generator.py`
**Line**: 19

**Issue**: Class 'TaskGenerator' has 11 methods, exceeding the recommended maximum of 10. This suggests the class may have multiple responsibilities.

**Recommendation**: Refactor to follow Single Responsibility Principle:
- Identify distinct responsibilities in the class
- Extract related methods into separate classes
- Use composition to combine focused classes
- Consider applying the Extract Class refactoring

**Additional Details**:
- Class Name: TaskGenerator
- Method Count: 11
- Threshold: 10

#### 63. Fat interface: 'TaskGenerator' has 11 methods

**Type**: ISPViolation
**File**: `lib/reporters/task_generator.py`
**Line**: 19

**Issue**: Interface/base class 'TaskGenerator' has 11 methods, exceeding the recommended maximum of 10. Large interfaces force clients to depend on methods they don't use.

**Recommendation**: Split the fat interface:
- Identify distinct groups of related methods
- Create smaller, focused interfaces for each group
- Use interface inheritance to compose larger interfaces if needed
- Apply the Interface Segregation Principle

**Additional Details**:
- Class Name: TaskGenerator
- Method Count: 11
- Threshold: 10

#### 64. Long method detected: '_format_task' (70 lines)

**Type**: LongMethod
**File**: `lib/reporters/task_generator.py`
**Line**: 252

**Issue**: Method '_format_task' is 70 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _format_task
- Line Count: 70

#### 65. Long method detected: '_format_grouped_task' (64 lines)

**Type**: LongMethod
**File**: `lib/reporters/task_generator.py`
**Line**: 323

**Issue**: Method '_format_grouped_task' is 64 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _format_grouped_task
- Line Count: 64

#### 66. Class 'AssessmentOrchestrator' has too many methods (11)

**Type**: SRPViolation
**File**: `scripts/assess.py`
**Line**: 87

**Issue**: Class 'AssessmentOrchestrator' has 11 methods, exceeding the recommended maximum of 10. This suggests the class may have multiple responsibilities.

**Recommendation**: Refactor to follow Single Responsibility Principle:
- Identify distinct responsibilities in the class
- Extract related methods into separate classes
- Use composition to combine focused classes
- Consider applying the Extract Class refactoring

**Additional Details**:
- Class Name: AssessmentOrchestrator
- Method Count: 11
- Threshold: 10

#### 67. Fat interface: 'AssessmentOrchestrator' has 11 methods

**Type**: ISPViolation
**File**: `scripts/assess.py`
**Line**: 87

**Issue**: Interface/base class 'AssessmentOrchestrator' has 11 methods, exceeding the recommended maximum of 10. Large interfaces force clients to depend on methods they don't use.

**Recommendation**: Split the fat interface:
- Identify distinct groups of related methods
- Create smaller, focused interfaces for each group
- Use interface inheritance to compose larger interfaces if needed
- Apply the Interface Segregation Principle

**Additional Details**:
- Class Name: AssessmentOrchestrator
- Method Count: 11
- Threshold: 10

#### 68. Long method detected: 'run' (65 lines)

**Type**: LongMethod
**File**: `scripts/assess.py`
**Line**: 128

**Issue**: Method 'run' is 65 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: run
- Line Count: 65

#### 69. Long method detected: '_discover_files' (63 lines)

**Type**: LongMethod
**File**: `scripts/assess.py`
**Line**: 213

**Issue**: Method '_discover_files' is 63 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _discover_files
- Line Count: 63

#### 70. Long method detected: '_parse_files' (51 lines)

**Type**: LongMethod
**File**: `scripts/assess.py`
**Line**: 277

**Issue**: Method '_parse_files' is 51 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: _parse_files
- Line Count: 51

#### 71. High coupling detected (FAN-OUT: 7)

**Type**: HighCoupling
**File**: `scripts/detect_project_type.py`

**Issue**: Module 'scripts/detect_project_type.py' depends on 7 other modules, indicating tight coupling. High FAN-OUT makes the module fragile and difficult to maintain, as changes in dependencies may require changes here.

Dependencies:
  - argparse
  - lib/models/project_type.py
  - lib/reporters/json_reporter.py
  - logging
  - pathlib
  - sys
  - typing

**Recommendation**: Consider refactoring to reduce dependencies:
- Extract shared logic to dedicated utility modules
- Apply Dependency Inversion Principle (depend on abstractions)
- Use dependency injection to reduce direct coupling
- Break down large module into smaller, focused modules

**Additional Details**:
- Fan Out: 7
- Fan In: 2
- Instability: 0.7777777777777778
- Dependencies:
  - typing
  - sys
  - lib/reporters/json_reporter.py
  - lib/models/project_type.py
  - logging
  - pathlib
  - argparse

#### 72. Class 'ProjectTypeDetector' has too many methods (18)

**Type**: SRPViolation
**File**: `scripts/detect_project_type.py`
**Line**: 36

**Issue**: Class 'ProjectTypeDetector' has 18 methods, exceeding the recommended maximum of 10. This suggests the class may have multiple responsibilities.

**Recommendation**: Refactor to follow Single Responsibility Principle:
- Identify distinct responsibilities in the class
- Extract related methods into separate classes
- Use composition to combine focused classes
- Consider applying the Extract Class refactoring

**Additional Details**:
- Class Name: ProjectTypeDetector
- Method Count: 18
- Threshold: 10

#### 73. Fat interface: 'ProjectTypeDetector' has 18 methods

**Type**: ISPViolation
**File**: `scripts/detect_project_type.py`
**Line**: 36

**Issue**: Interface/base class 'ProjectTypeDetector' has 18 methods, exceeding the recommended maximum of 10. Large interfaces force clients to depend on methods they don't use.

**Recommendation**: Split the fat interface:
- Identify distinct groups of related methods
- Create smaller, focused interfaces for each group
- Use interface inheritance to compose larger interfaces if needed
- Apply the Interface Segregation Principle

**Additional Details**:
- Class Name: ProjectTypeDetector
- Method Count: 18
- Threshold: 10

#### 74. Complex method detected: 'detect' (complexity: 14)

**Type**: ComplexMethod
**File**: `scripts/detect_project_type.py`
**Line**: 49

**Issue**: Method 'detect' has high cyclomatic complexity (14). Complex methods with many branches are hard to test and maintain.

**Recommendation**: Reduce method complexity:
- Extract complex conditions into well-named methods
- Use early returns to reduce nesting
- Consider using the Strategy pattern for complex conditionals
- Split the method into smaller, focused methods

**Additional Details**:
- Method Name: detect
- Complexity: 14

#### 75. Strategy pattern opportunity in 'detect' (11 branches)

**Type**: StrategyOpportunity
**File**: `scripts/detect_project_type.py`
**Line**: 70

**Issue**: Method 'detect' has a long if-elif chain with 11 branches. This suggests different algorithms being selected at runtime.

**Recommendation**: Consider using Strategy pattern:
- Create a strategy interface with an execute method
- Implement each branch as a concrete strategy class
- Use a dictionary or factory to select strategies
- Makes adding new strategies easier (Open/Closed Principle)

**Additional Details**:
- Method Name: detect
- Branch Count: 11

#### 76. Strategy pattern opportunity in 'detect' (10 branches)

**Type**: StrategyOpportunity
**File**: `scripts/detect_project_type.py`
**Line**: 72

**Issue**: Method 'detect' has a long if-elif chain with 10 branches. This suggests different algorithms being selected at runtime.

**Recommendation**: Consider using Strategy pattern:
- Create a strategy interface with an execute method
- Implement each branch as a concrete strategy class
- Use a dictionary or factory to select strategies
- Makes adding new strategies easier (Open/Closed Principle)

**Additional Details**:
- Method Name: detect
- Branch Count: 10

#### 77. Strategy pattern opportunity in 'detect' (9 branches)

**Type**: StrategyOpportunity
**File**: `scripts/detect_project_type.py`
**Line**: 74

**Issue**: Method 'detect' has a long if-elif chain with 9 branches. This suggests different algorithms being selected at runtime.

**Recommendation**: Consider using Strategy pattern:
- Create a strategy interface with an execute method
- Implement each branch as a concrete strategy class
- Use a dictionary or factory to select strategies
- Makes adding new strategies easier (Open/Closed Principle)

**Additional Details**:
- Method Name: detect
- Branch Count: 9

#### 78. Strategy pattern opportunity in 'detect' (8 branches)

**Type**: StrategyOpportunity
**File**: `scripts/detect_project_type.py`
**Line**: 76

**Issue**: Method 'detect' has a long if-elif chain with 8 branches. This suggests different algorithms being selected at runtime.

**Recommendation**: Consider using Strategy pattern:
- Create a strategy interface with an execute method
- Implement each branch as a concrete strategy class
- Use a dictionary or factory to select strategies
- Makes adding new strategies easier (Open/Closed Principle)

**Additional Details**:
- Method Name: detect
- Branch Count: 8

#### 79. Strategy pattern opportunity in 'detect' (7 branches)

**Type**: StrategyOpportunity
**File**: `scripts/detect_project_type.py`
**Line**: 78

**Issue**: Method 'detect' has a long if-elif chain with 7 branches. This suggests different algorithms being selected at runtime.

**Recommendation**: Consider using Strategy pattern:
- Create a strategy interface with an execute method
- Implement each branch as a concrete strategy class
- Use a dictionary or factory to select strategies
- Makes adding new strategies easier (Open/Closed Principle)

**Additional Details**:
- Method Name: detect
- Branch Count: 7

#### 80. Strategy pattern opportunity in 'detect' (6 branches)

**Type**: StrategyOpportunity
**File**: `scripts/detect_project_type.py`
**Line**: 80

**Issue**: Method 'detect' has a long if-elif chain with 6 branches. This suggests different algorithms being selected at runtime.

**Recommendation**: Consider using Strategy pattern:
- Create a strategy interface with an execute method
- Implement each branch as a concrete strategy class
- Use a dictionary or factory to select strategies
- Makes adding new strategies easier (Open/Closed Principle)

**Additional Details**:
- Method Name: detect
- Branch Count: 6

#### 81. Strategy pattern opportunity in 'detect' (5 branches)

**Type**: StrategyOpportunity
**File**: `scripts/detect_project_type.py`
**Line**: 84

**Issue**: Method 'detect' has a long if-elif chain with 5 branches. This suggests different algorithms being selected at runtime.

**Recommendation**: Consider using Strategy pattern:
- Create a strategy interface with an execute method
- Implement each branch as a concrete strategy class
- Use a dictionary or factory to select strategies
- Makes adding new strategies easier (Open/Closed Principle)

**Additional Details**:
- Method Name: detect
- Branch Count: 5

#### 82. Class 'TestProjectTypeDetector' has too many methods (13)

**Type**: SRPViolation
**File**: `tests/test_detect_project_type.py`
**Line**: 20

**Issue**: Class 'TestProjectTypeDetector' has 13 methods, exceeding the recommended maximum of 10. This suggests the class may have multiple responsibilities.

**Recommendation**: Refactor to follow Single Responsibility Principle:
- Identify distinct responsibilities in the class
- Extract related methods into separate classes
- Use composition to combine focused classes
- Consider applying the Extract Class refactoring

**Additional Details**:
- Class Name: TestProjectTypeDetector
- Method Count: 13
- Threshold: 10

#### 83. Low cohesion in class 'TestProjectTypeDetector' (LCOM: 1.00)

**Type**: SRPViolation
**File**: `tests/test_detect_project_type.py`
**Line**: 20

**Issue**: Class 'TestProjectTypeDetector' has low cohesion (LCOM: 1.00). Methods in the class don't share many instance variables, suggesting multiple responsibilities.

**Recommendation**: Improve class cohesion:
- Group methods that work with the same instance variables
- Extract loosely related methods into separate classes
- Ensure each class has a single, well-defined purpose

**Additional Details**:
- Class Name: TestProjectTypeDetector
- Lcom: 1.0
- Threshold: 0.8

#### 84. Fat interface: 'TestProjectTypeDetector' has 13 methods

**Type**: ISPViolation
**File**: `tests/test_detect_project_type.py`
**Line**: 20

**Issue**: Interface/base class 'TestProjectTypeDetector' has 13 methods, exceeding the recommended maximum of 10. Large interfaces force clients to depend on methods they don't use.

**Recommendation**: Split the fat interface:
- Identify distinct groups of related methods
- Create smaller, focused interfaces for each group
- Use interface inheritance to compose larger interfaces if needed
- Apply the Interface Segregation Principle

**Additional Details**:
- Class Name: TestProjectTypeDetector
- Method Count: 13
- Threshold: 10

#### 85. Class 'TestIntegration' has too many methods (11)

**Type**: SRPViolation
**File**: `tests/test_integration.py`
**Line**: 27

**Issue**: Class 'TestIntegration' has 11 methods, exceeding the recommended maximum of 10. This suggests the class may have multiple responsibilities.

**Recommendation**: Refactor to follow Single Responsibility Principle:
- Identify distinct responsibilities in the class
- Extract related methods into separate classes
- Use composition to combine focused classes
- Consider applying the Extract Class refactoring

**Additional Details**:
- Class Name: TestIntegration
- Method Count: 11
- Threshold: 10

#### 86. Low cohesion in class 'TestIntegration' (LCOM: 1.00)

**Type**: SRPViolation
**File**: `tests/test_integration.py`
**Line**: 27

**Issue**: Class 'TestIntegration' has low cohesion (LCOM: 1.00). Methods in the class don't share many instance variables, suggesting multiple responsibilities.

**Recommendation**: Improve class cohesion:
- Group methods that work with the same instance variables
- Extract loosely related methods into separate classes
- Ensure each class has a single, well-defined purpose

**Additional Details**:
- Class Name: TestIntegration
- Lcom: 1.0
- Threshold: 0.8

#### 87. Fat interface: 'TestIntegration' has 11 methods

**Type**: ISPViolation
**File**: `tests/test_integration.py`
**Line**: 27

**Issue**: Interface/base class 'TestIntegration' has 11 methods, exceeding the recommended maximum of 10. Large interfaces force clients to depend on methods they don't use.

**Recommendation**: Split the fat interface:
- Identify distinct groups of related methods
- Create smaller, focused interfaces for each group
- Use interface inheritance to compose larger interfaces if needed
- Apply the Interface Segregation Principle

**Additional Details**:
- Class Name: TestIntegration
- Method Count: 11
- Threshold: 10

#### 88. Class 'TestJavaScriptParser' has too many methods (30)

**Type**: SRPViolation
**File**: `tests/test_javascript_parser.py`
**Line**: 20

**Issue**: Class 'TestJavaScriptParser' has 30 methods, exceeding the recommended maximum of 10. This suggests the class may have multiple responsibilities.

**Recommendation**: Refactor to follow Single Responsibility Principle:
- Identify distinct responsibilities in the class
- Extract related methods into separate classes
- Use composition to combine focused classes
- Consider applying the Extract Class refactoring

**Additional Details**:
- Class Name: TestJavaScriptParser
- Method Count: 30
- Threshold: 10

#### 89. Low cohesion in class 'TestJavaScriptParser' (LCOM: 1.00)

**Type**: SRPViolation
**File**: `tests/test_javascript_parser.py`
**Line**: 20

**Issue**: Class 'TestJavaScriptParser' has low cohesion (LCOM: 1.00). Methods in the class don't share many instance variables, suggesting multiple responsibilities.

**Recommendation**: Improve class cohesion:
- Group methods that work with the same instance variables
- Extract loosely related methods into separate classes
- Ensure each class has a single, well-defined purpose

**Additional Details**:
- Class Name: TestJavaScriptParser
- Lcom: 1.0
- Threshold: 0.8

#### 90. Fat interface: 'TestJavaScriptParser' has 30 methods

**Type**: ISPViolation
**File**: `tests/test_javascript_parser.py`
**Line**: 20

**Issue**: Interface/base class 'TestJavaScriptParser' has 30 methods, exceeding the recommended maximum of 10. Large interfaces force clients to depend on methods they don't use.

**Recommendation**: Split the fat interface:
- Identify distinct groups of related methods
- Create smaller, focused interfaces for each group
- Use interface inheritance to compose larger interfaces if needed
- Apply the Interface Segregation Principle

**Additional Details**:
- Class Name: TestJavaScriptParser
- Method Count: 30
- Threshold: 10

#### 91. High coupling detected (FAN-OUT: 7)

**Type**: HighCoupling
**File**: `tests/test_layer_analyzer.py`

**Issue**: Module 'tests/test_layer_analyzer.py' depends on 7 other modules, indicating tight coupling. High FAN-OUT makes the module fragile and difficult to maintain, as changes in dependencies may require changes here.

Dependencies:
  - lib/analyzers/base.py
  - lib/analyzers/layer_analyzer.py
  - lib/graph/dependency_graph.py
  - lib/models/config.py
  - pathlib
  - pytest
  - tempfile

**Recommendation**: Consider refactoring to reduce dependencies:
- Extract shared logic to dedicated utility modules
- Apply Dependency Inversion Principle (depend on abstractions)
- Use dependency injection to reduce direct coupling
- Break down large module into smaller, focused modules

**Additional Details**:
- Fan Out: 7
- Fan In: 0
- Instability: 1.0
- Dependencies:
  - pytest
  - lib/analyzers/base.py
  - lib/analyzers/layer_analyzer.py
  - tempfile
  - lib/graph/dependency_graph.py
  - pathlib
  - lib/models/config.py

#### 92. Class 'TestPythonParser' has too many methods (21)

**Type**: SRPViolation
**File**: `tests/test_python_parser.py`
**Line**: 20

**Issue**: Class 'TestPythonParser' has 21 methods, exceeding the recommended maximum of 10. This suggests the class may have multiple responsibilities.

**Recommendation**: Refactor to follow Single Responsibility Principle:
- Identify distinct responsibilities in the class
- Extract related methods into separate classes
- Use composition to combine focused classes
- Consider applying the Extract Class refactoring

**Additional Details**:
- Class Name: TestPythonParser
- Method Count: 21
- Threshold: 10

#### 93. Low cohesion in class 'TestPythonParser' (LCOM: 1.00)

**Type**: SRPViolation
**File**: `tests/test_python_parser.py`
**Line**: 20

**Issue**: Class 'TestPythonParser' has low cohesion (LCOM: 1.00). Methods in the class don't share many instance variables, suggesting multiple responsibilities.

**Recommendation**: Improve class cohesion:
- Group methods that work with the same instance variables
- Extract loosely related methods into separate classes
- Ensure each class has a single, well-defined purpose

**Additional Details**:
- Class Name: TestPythonParser
- Lcom: 1.0
- Threshold: 0.8

#### 94. Fat interface: 'TestPythonParser' has 21 methods

**Type**: ISPViolation
**File**: `tests/test_python_parser.py`
**Line**: 20

**Issue**: Interface/base class 'TestPythonParser' has 21 methods, exceeding the recommended maximum of 10. Large interfaces force clients to depend on methods they don't use.

**Recommendation**: Split the fat interface:
- Identify distinct groups of related methods
- Create smaller, focused interfaces for each group
- Use interface inheritance to compose larger interfaces if needed
- Apply the Interface Segregation Principle

**Additional Details**:
- Class Name: TestPythonParser
- Method Count: 21
- Threshold: 10

#### 95. Low cohesion in class 'TestSelfAnalysis' (LCOM: 1.00)

**Type**: SRPViolation
**File**: `tests/test_self_analysis.py`
**Line**: 29

**Issue**: Class 'TestSelfAnalysis' has low cohesion (LCOM: 1.00). Methods in the class don't share many instance variables, suggesting multiple responsibilities.

**Recommendation**: Improve class cohesion:
- Group methods that work with the same instance variables
- Extract loosely related methods into separate classes
- Ensure each class has a single, well-defined purpose

**Additional Details**:
- Class Name: TestSelfAnalysis
- Lcom: 1.0
- Threshold: 0.8

#### 96. Long method detected: 'test_self_analysis_runs_successfully' (59 lines)

**Type**: LongMethod
**File**: `tests/test_self_analysis.py`
**Line**: 42

**Issue**: Method 'test_self_analysis_runs_successfully' is 59 lines long. Long methods are hard to understand, test, and maintain.

**Recommendation**: Refactor the long method:
- Extract logical sections into smaller helper methods
- Use the Extract Method refactoring pattern
- Each method should do one thing and do it well
- Aim for methods under 30 lines

**Additional Details**:
- Method Name: test_self_analysis_runs_successfully
- Line Count: 59

### 🔵 LOW (17 issues)

#### 1. 3 unused imports detected

**Type**: UnusedImports
**File**: `lib/analyzers/pattern_analyzer.py`

**Issue**: Found 3 unused imports: Dict, Path, Set. Unused imports clutter code and may indicate dead code.

**Recommendation**: Remove unused imports:
- Delete imports that aren't being used
- Use tools like autoflake or ruff to clean up imports
- Configure your IDE to highlight unused imports

**Additional Details**:
- Unused Imports:
  - Path
  - Dict
  - Set

#### 2. Multiple magic numbers detected (9 found)

**Type**: MagicNumbers
**File**: `lib/analyzers/pattern_analyzer.py`
**Line**: 163

**Issue**: Found 9 magic numbers (unexplained numeric constants) in the code. Examples: 5 (line 163), 3 (line 346), 50 (line 221). Magic numbers make code harder to understand and maintain.

**Recommendation**: Replace magic numbers with named constants:
- Define constants at module or class level with descriptive names
- Use enums for related constant values
- Add comments explaining the significance of values

**Additional Details**:
- Count: 9
- Examples:
  - 5
  - 3
  - 50

#### 3. 7 unused imports detected

**Type**: UnusedImports
**File**: `lib/analyzers/solid_analyzer.py`

**Issue**: Found 7 unused imports: Dict, Optional, Path, Tuple, defaultdict. Unused imports clutter code and may indicate dead code.

**Recommendation**: Remove unused imports:
- Delete imports that aren't being used
- Use tools like autoflake or ruff to clean up imports
- Configure your IDE to highlight unused imports

**Additional Details**:
- Unused Imports:
  - Path
  - Optional
  - Dict
  - defaultdict
  - Tuple
  - re
  - Set

#### 4. Multiple magic numbers detected (5 found)

**Type**: MagicNumbers
**File**: `lib/analyzers/solid_analyzer.py`
**Line**: 213

**Issue**: Found 5 magic numbers (unexplained numeric constants) in the code. Examples: 3 (line 213), 5 (line 418), 3 (line 285). Magic numbers make code harder to understand and maintain.

**Recommendation**: Replace magic numbers with named constants:
- Define constants at module or class level with descriptive names
- Use enums for related constant values
- Add comments explaining the significance of values

**Additional Details**:
- Count: 5
- Examples:
  - 3
  - 5
  - 3

#### 5. 14 unused imports detected

**Type**: UnusedImports
**File**: `lib/models/__init__.py`

**Issue**: Found 14 unused imports: AnalysisConfig, AssessmentConfig, LayerDefinition, ProjectInfo, ProjectType. Unused imports clutter code and may indicate dead code.

**Recommendation**: Remove unused imports:
- Delete imports that aren't being used
- Use tools like autoflake or ruff to clean up imports
- Configure your IDE to highlight unused imports

**Additional Details**:
- Unused Imports:
  - AssessmentConfig
  - ProjectType
  - ProjectInfo
  - AnalysisConfig
  - LayerDefinition
  - ProjectConfig
  - ReportingConfig
  - ProjectMetrics
  - Violation
  - CouplingThresholds
  - AssessmentResult
  - SOLIDMetrics
  - CouplingMetrics
  - SOLIDThresholds

#### 6. 5 unused imports detected

**Type**: UnusedImports
**File**: `lib/parsers/__init__.py`

**Issue**: Found 5 unused imports: ClassDefinition, FunctionDefinition, ImportStatement, ParseResult, ParserError. Unused imports clutter code and may indicate dead code.

**Recommendation**: Remove unused imports:
- Delete imports that aren't being used
- Use tools like autoflake or ruff to clean up imports
- Configure your IDE to highlight unused imports

**Additional Details**:
- Unused Imports:
  - ImportStatement
  - ParseResult
  - ParserError
  - ClassDefinition
  - FunctionDefinition

#### 7. Multiple magic numbers detected (9 found)

**Type**: MagicNumbers
**File**: `lib/reporters/json_reporter.py`
**Line**: 322

**Issue**: Found 9 magic numbers (unexplained numeric constants) in the code. Examples: 15 (line 322), 8 (line 323), 3 (line 324). Magic numbers make code harder to understand and maintain.

**Recommendation**: Replace magic numbers with named constants:
- Define constants at module or class level with descriptive names
- Use enums for related constant values
- Add comments explaining the significance of values

**Additional Details**:
- Count: 9
- Examples:
  - 15
  - 8
  - 3

#### 8. Multiple magic numbers detected (14 found)

**Type**: MagicNumbers
**File**: `lib/reporters/markdown_reporter.py`
**Line**: 95

**Issue**: Found 14 magic numbers (unexplained numeric constants) in the code. Examples: 15 (line 95), 8 (line 96), 3 (line 97). Magic numbers make code harder to understand and maintain.

**Recommendation**: Replace magic numbers with named constants:
- Define constants at module or class level with descriptive names
- Use enums for related constant values
- Add comments explaining the significance of values

**Additional Details**:
- Count: 14
- Examples:
  - 15
  - 8
  - 3

#### 9. 3 unused imports detected

**Type**: UnusedImports
**File**: `scripts/assess.py`

**Issue**: Found 3 unused imports: Set, get_enabled_analyzers, is_parseable. Unused imports clutter code and may indicate dead code.

**Recommendation**: Remove unused imports:
- Delete imports that aren't being used
- Use tools like autoflake or ruff to clean up imports
- Configure your IDE to highlight unused imports

**Additional Details**:
- Unused Imports:
  - get_enabled_analyzers
  - is_parseable
  - Set

#### 10. Multiple magic numbers detected (12 found)

**Type**: MagicNumbers
**File**: `scripts/assess.py`
**Line**: 422

**Issue**: Found 12 magic numbers (unexplained numeric constants) in the code. Examples: 3 (line 422), 60 (line 614), 3 (line 643). Magic numbers make code harder to understand and maintain.

**Recommendation**: Replace magic numbers with named constants:
- Define constants at module or class level with descriptive names
- Use enums for related constant values
- Add comments explaining the significance of values

**Additional Details**:
- Count: 12
- Examples:
  - 3
  - 60
  - 3

#### 11. Multiple magic numbers detected (11 found)

**Type**: MagicNumbers
**File**: `scripts/detect_project_type.py`
**Line**: 71

**Issue**: Found 11 magic numbers (unexplained numeric constants) in the code. Examples: 0.95 (line 71), 0.9 (line 73), 0.85 (line 75). Magic numbers make code harder to understand and maintain.

**Recommendation**: Replace magic numbers with named constants:
- Define constants at module or class level with descriptive names
- Use enums for related constant values
- Add comments explaining the significance of values

**Additional Details**:
- Count: 11
- Examples:
  - 0.95
  - 0.9
  - 0.85

#### 12. Multiple magic numbers detected (11 found)

**Type**: MagicNumbers
**File**: `tests/test_coupling_analyzer.py`
**Line**: 41

**Issue**: Found 11 magic numbers (unexplained numeric constants) in the code. Examples: 12 (line 41), 8 (line 66), 25 (line 89). Magic numbers make code harder to understand and maintain.

**Recommendation**: Replace magic numbers with named constants:
- Define constants at module or class level with descriptive names
- Use enums for related constant values
- Add comments explaining the significance of values

**Additional Details**:
- Count: 11
- Examples:
  - 12
  - 8
  - 25

#### 13. Multiple magic numbers detected (5 found)

**Type**: MagicNumbers
**File**: `tests/test_detect_project_type.py`
**Line**: 37

**Issue**: Found 5 magic numbers (unexplained numeric constants) in the code. Examples: 0.9 (line 37), 0.85 (line 50), 0.8 (line 63). Magic numbers make code harder to understand and maintain.

**Recommendation**: Replace magic numbers with named constants:
- Define constants at module or class level with descriptive names
- Use enums for related constant values
- Add comments explaining the significance of values

**Additional Details**:
- Count: 5
- Examples:
  - 0.9
  - 0.85
  - 0.8

#### 14. Multiple magic numbers detected (8 found)

**Type**: MagicNumbers
**File**: `tests/test_javascript_parser.py`
**Line**: 66

**Issue**: Found 8 magic numbers (unexplained numeric constants) in the code. Examples: 4 (line 66), 3 (line 107), 3 (line 121). Magic numbers make code harder to understand and maintain.

**Recommendation**: Replace magic numbers with named constants:
- Define constants at module or class level with descriptive names
- Use enums for related constant values
- Add comments explaining the significance of values

**Additional Details**:
- Count: 8
- Examples:
  - 4
  - 3
  - 3

#### 15. Multiple magic numbers detected (6 found)

**Type**: MagicNumbers
**File**: `tests/test_python_parser.py`
**Line**: 49

**Issue**: Found 6 magic numbers (unexplained numeric constants) in the code. Examples: 4 (line 49), 3 (line 88), 3 (line 123). Magic numbers make code harder to understand and maintain.

**Recommendation**: Replace magic numbers with named constants:
- Define constants at module or class level with descriptive names
- Use enums for related constant values
- Add comments explaining the significance of values

**Additional Details**:
- Count: 6
- Examples:
  - 4
  - 3
  - 3

#### 16. Multiple magic numbers detected (8 found)

**Type**: MagicNumbers
**File**: `tests/test_self_analysis.py`
**Line**: 275

**Issue**: Found 8 magic numbers (unexplained numeric constants) in the code. Examples: 60 (line 275), 60 (line 67), 60 (line 100). Magic numbers make code harder to understand and maintain.

**Recommendation**: Replace magic numbers with named constants:
- Define constants at module or class level with descriptive names
- Use enums for related constant values
- Add comments explaining the significance of values

**Additional Details**:
- Count: 8
- Examples:
  - 60
  - 60
  - 60

#### 17. Multiple magic numbers detected (9 found)

**Type**: MagicNumbers
**File**: `tests/test_solid_analyzer.py`
**Line**: 309

**Issue**: Found 9 magic numbers (unexplained numeric constants) in the code. Examples: 5 (line 309), 200 (line 310), 15 (line 41). Magic numbers make code harder to understand and maintain.

**Recommendation**: Replace magic numbers with named constants:
- Define constants at module or class level with descriptive names
- Use enums for related constant values
- Add comments explaining the significance of values

**Additional Details**:
- Count: 9
- Examples:
  - 5
  - 200
  - 15


---

## 4. Violations by Analysis Dimension

### Layer Separation (1 issue)

- 🟠 **Direct ORM usage in presentation layer** - `tests/fixtures/express-api/routes/users.js:10`

### SOLID Principles (40 issues)

- 🟠 **God Class detected: 'PatternAnalyzer' (594 LOC)** - `lib/analyzers/pattern_analyzer.py:25`
- 🟠 **God Class detected: 'SOLIDAnalyzer' (652 LOC)** - `lib/analyzers/solid_analyzer.py:29`
- 🟠 **God Class detected: 'MarkdownReporter' (515 LOC)** - `lib/reporters/markdown_reporter.py:20`
- 🟡 **Class 'BaseAnalyzer' has too many methods (12)** - `lib/analyzers/base.py:58`
- 🟡 **Fat interface: 'BaseAnalyzer' has 12 methods** - `lib/analyzers/base.py:58`
- 🟡 **Class 'BaseAnalyzer' has 3 stub methods** - `lib/analyzers/base.py:58`
- 🟡 **Class 'PatternAnalyzer' has too many methods (12)** - `lib/analyzers/pattern_analyzer.py:25`
- 🟡 **Fat interface: 'PatternAnalyzer' has 12 methods** - `lib/analyzers/pattern_analyzer.py:25`
- 🟡 **Class 'SOLIDAnalyzer' has too many methods (14)** - `lib/analyzers/solid_analyzer.py:29`
- 🟡 **Low cohesion in class 'SOLIDAnalyzer' (LCOM: 0.89)** - `lib/analyzers/solid_analyzer.py:29`
- 🟡 **Fat interface: 'SOLIDAnalyzer' has 14 methods** - `lib/analyzers/solid_analyzer.py:29`
- 🟡 **Class 'DependencyGraph' has too many methods (16)** - `lib/graph/dependency_graph.py:69`
- 🟡 **Fat interface: 'DependencyGraph' has 16 methods** - `lib/graph/dependency_graph.py:69`
- 🟡 **Low cohesion in class 'ProjectMetrics' (LCOM: 0.83)** - `lib/models/metrics.py:125`
- 🟡 **Low cohesion in class 'ProjectType' (LCOM: 1.00)** - `lib/models/project_type.py:15`
- 🟡 **Low cohesion in class 'BaseParser' (LCOM: 0.93)** - `lib/parsers/base.py:127`
- 🟡 **Class 'BaseParser' has 3 stub methods** - `lib/parsers/base.py:127`
- 🟡 **Low cohesion in class 'JavaScriptParser' (LCOM: 0.97)** - `lib/parsers/javascript_parser.py:31`
- 🟡 **Low cohesion in class 'PythonParser' (LCOM: 0.84)** - `lib/parsers/python_parser.py:31`
- 🟡 **Class 'MarkdownReporter' has too many methods (13)** - `lib/reporters/markdown_reporter.py:20`
- 🟡 **Fat interface: 'MarkdownReporter' has 13 methods** - `lib/reporters/markdown_reporter.py:20`
- 🟡 **Class 'TaskGenerator' has too many methods (11)** - `lib/reporters/task_generator.py:19`
- 🟡 **Fat interface: 'TaskGenerator' has 11 methods** - `lib/reporters/task_generator.py:19`
- 🟡 **Class 'AssessmentOrchestrator' has too many methods (11)** - `scripts/assess.py:87`
- 🟡 **Fat interface: 'AssessmentOrchestrator' has 11 methods** - `scripts/assess.py:87`
- 🟡 **Class 'ProjectTypeDetector' has too many methods (18)** - `scripts/detect_project_type.py:36`
- 🟡 **Fat interface: 'ProjectTypeDetector' has 18 methods** - `scripts/detect_project_type.py:36`
- 🟡 **Class 'TestProjectTypeDetector' has too many methods (13)** - `tests/test_detect_project_type.py:20`
- 🟡 **Low cohesion in class 'TestProjectTypeDetector' (LCOM: 1.00)** - `tests/test_detect_project_type.py:20`
- 🟡 **Fat interface: 'TestProjectTypeDetector' has 13 methods** - `tests/test_detect_project_type.py:20`
- 🟡 **Class 'TestIntegration' has too many methods (11)** - `tests/test_integration.py:27`
- 🟡 **Low cohesion in class 'TestIntegration' (LCOM: 1.00)** - `tests/test_integration.py:27`
- 🟡 **Fat interface: 'TestIntegration' has 11 methods** - `tests/test_integration.py:27`
- 🟡 **Class 'TestJavaScriptParser' has too many methods (30)** - `tests/test_javascript_parser.py:20`
- 🟡 **Low cohesion in class 'TestJavaScriptParser' (LCOM: 1.00)** - `tests/test_javascript_parser.py:20`
- 🟡 **Fat interface: 'TestJavaScriptParser' has 30 methods** - `tests/test_javascript_parser.py:20`
- 🟡 **Class 'TestPythonParser' has too many methods (21)** - `tests/test_python_parser.py:20`
- 🟡 **Low cohesion in class 'TestPythonParser' (LCOM: 1.00)** - `tests/test_python_parser.py:20`
- 🟡 **Fat interface: 'TestPythonParser' has 21 methods** - `tests/test_python_parser.py:20`
- 🟡 **Low cohesion in class 'TestSelfAnalysis' (LCOM: 1.00)** - `tests/test_self_analysis.py:29`

### Design Patterns (77 issues)

- 🟠 **Long method detected: '_check_database_patterns' (115 lines)** - `lib/analyzers/layer_analyzer.py:328`
- 🟠 **Long method detected: '_analyze_srp' (123 lines)** - `lib/analyzers/solid_analyzer.py:119`
- 🟠 **Long method detected: 'to_markdown' (122 lines)** - `lib/models/assessment.py:120`
- 🟠 **Long method detected: 'get_expected_patterns' (104 lines)** - `lib/models/project_type.py:72`
- 🟠 **Long method detected: 'extract_imports' (127 lines)** - `lib/parsers/javascript_parser.py:151`
- 🟠 **Complex method detected: 'extract_imports' (complexity: 19)** - `lib/parsers/javascript_parser.py:151`
- 🟠 **Complex method detected: '_extract_classes_from_ast' (complexity: 17)** - `lib/parsers/python_parser.py:198`
- 🟠 **Long method detected: 'main' (161 lines)** - `scripts/assess.py:542`
- 🟠 **Complex method detected: 'main' (complexity: 18)** - `scripts/assess.py:542`
- 🟡 **Long method detected: 'create_violation' (58 lines)** - `lib/analyzers/base.py:141`
- 🟡 **Long method detected: '_analyze_fan_out' (67 lines)** - `lib/analyzers/coupling_analyzer.py:111`
- 🟡 **Long method detected: '_analyze_fan_in' (62 lines)** - `lib/analyzers/coupling_analyzer.py:179`
- 🟡 **Long method detected: '_analyze_circular_dependencies' (59 lines)** - `lib/analyzers/coupling_analyzer.py:242`
- 🟡 **Long method detected: '_analyze_deep_chains' (65 lines)** - `lib/analyzers/coupling_analyzer.py:302`
- 🟡 **Long method detected: '_analyze_layer_dependencies' (72 lines)** - `lib/analyzers/layer_analyzer.py:444`
- 🟡 **Long method detected: 'analyze' (57 lines)** - `lib/analyzers/pattern_analyzer.py:71`
- 🟡 **Long method detected: '_detect_magic_numbers' (65 lines)** - `lib/analyzers/pattern_analyzer.py:129`
- 🟡 **Long method detected: '_detect_long_methods' (56 lines)** - `lib/analyzers/pattern_analyzer.py:195`
- 🟡 **Long method detected: '_detect_complex_methods' (54 lines)** - `lib/analyzers/pattern_analyzer.py:252`
- 🟡 **Long method detected: '_detect_dead_code' (65 lines)** - `lib/analyzers/pattern_analyzer.py:307`
- 🟡 **Long method detected: '_detect_factory_opportunities' (65 lines)** - `lib/analyzers/pattern_analyzer.py:373`
- 🟡 **Long method detected: '_detect_strategy_opportunities' (67 lines)** - `lib/analyzers/pattern_analyzer.py:439`
- 🟡 **Long method detected: '_detect_singleton_misuse' (71 lines)** - `lib/analyzers/pattern_analyzer.py:507`
- 🟡 **Long method detected: 'analyze' (54 lines)** - `lib/analyzers/solid_analyzer.py:64`
- 🟡 **Long method detected: '_analyze_ocp' (70 lines)** - `lib/analyzers/solid_analyzer.py:243`
- 🟡 **Long method detected: '_analyze_lsp' (75 lines)** - `lib/analyzers/solid_analyzer.py:314`
- 🟡 **Long method detected: '_analyze_isp' (97 lines)** - `lib/analyzers/solid_analyzer.py:390`
- 🟡 **Long method detected: '_analyze_dip' (60 lines)** - `lib/analyzers/solid_analyzer.py:488`
- 🟡 **Complex method detected: '_calculate_lcom' (complexity: 11)** - `lib/analyzers/solid_analyzer.py:565`
- 🟡 **Long method detected: 'detect_cycles' (51 lines)** - `lib/graph/dependency_graph.py:175`
- 🟡 **Factory pattern opportunity: 'ImportStatement' instantiated 6 times** - `lib/parsers/javascript_parser.py:268`
- 🟡 **Long method detected: 'extract_classes' (52 lines)** - `lib/parsers/javascript_parser.py:279`
- 🟡 **Long method detected: 'extract_functions' (56 lines)** - `lib/parsers/javascript_parser.py:332`
- 🟡 **Factory pattern opportunity: 'FunctionDefinition' instantiated 3 times** - `lib/parsers/javascript_parser.py:351`
- 🟡 **Complex method detected: '_parse_parameters' (complexity: 11)** - `lib/parsers/javascript_parser.py:434`
- 🟡 **Long method detected: '_extract_classes_from_ast' (68 lines)** - `lib/parsers/python_parser.py:198`
- 🟡 **Long method detected: '_build_metrics' (53 lines)** - `lib/reporters/json_reporter.py:138`
- 🟡 **Long method detected: '_build_recommended_actions' (61 lines)** - `lib/reporters/json_reporter.py:200`
- 🟡 **Complex method detected: '_build_recommended_actions' (complexity: 12)** - `lib/reporters/json_reporter.py:200`
- 🟡 **Long method detected: 'generate_ci_summary' (61 lines)** - `lib/reporters/json_reporter.py:296`
- 🟡 **Long method detected: '_executive_summary' (68 lines)** - `lib/reporters/markdown_reporter.py:76`
- 🟡 **Long method detected: '_metrics_dashboard' (70 lines)** - `lib/reporters/markdown_reporter.py:164`
- 🟡 **Complex method detected: '_metrics_dashboard' (complexity: 12)** - `lib/reporters/markdown_reporter.py:164`
- 🟡 **Long method detected: '_violations_by_severity' (66 lines)** - `lib/reporters/markdown_reporter.py:235`
- 🟡 **Long method detected: '_violations_by_dimension' (63 lines)** - `lib/reporters/markdown_reporter.py:302`
- 🟡 **Long method detected: '_recommended_actions' (73 lines)** - `lib/reporters/markdown_reporter.py:366`
- 🟡 **Long method detected: '_format_task' (70 lines)** - `lib/reporters/task_generator.py:252`
- 🟡 **Long method detected: '_format_grouped_task' (64 lines)** - `lib/reporters/task_generator.py:323`
- 🟡 **Long method detected: 'run' (65 lines)** - `scripts/assess.py:128`
- 🟡 **Long method detected: '_discover_files' (63 lines)** - `scripts/assess.py:213`
- 🟡 **Long method detected: '_parse_files' (51 lines)** - `scripts/assess.py:277`
- 🟡 **Complex method detected: 'detect' (complexity: 14)** - `scripts/detect_project_type.py:49`
- 🟡 **Strategy pattern opportunity in 'detect' (11 branches)** - `scripts/detect_project_type.py:70`
- 🟡 **Strategy pattern opportunity in 'detect' (10 branches)** - `scripts/detect_project_type.py:72`
- 🟡 **Strategy pattern opportunity in 'detect' (9 branches)** - `scripts/detect_project_type.py:74`
- 🟡 **Strategy pattern opportunity in 'detect' (8 branches)** - `scripts/detect_project_type.py:76`
- 🟡 **Strategy pattern opportunity in 'detect' (7 branches)** - `scripts/detect_project_type.py:78`
- 🟡 **Strategy pattern opportunity in 'detect' (6 branches)** - `scripts/detect_project_type.py:80`
- 🟡 **Strategy pattern opportunity in 'detect' (5 branches)** - `scripts/detect_project_type.py:84`
- 🟡 **Long method detected: 'test_self_analysis_runs_successfully' (59 lines)** - `tests/test_self_analysis.py:42`
- 🔵 **3 unused imports detected** - `lib/analyzers/pattern_analyzer.py`
- 🔵 **Multiple magic numbers detected (9 found)** - `lib/analyzers/pattern_analyzer.py:163`
- 🔵 **7 unused imports detected** - `lib/analyzers/solid_analyzer.py`
- 🔵 **Multiple magic numbers detected (5 found)** - `lib/analyzers/solid_analyzer.py:213`
- 🔵 **14 unused imports detected** - `lib/models/__init__.py`
- 🔵 **5 unused imports detected** - `lib/parsers/__init__.py`
- 🔵 **Multiple magic numbers detected (9 found)** - `lib/reporters/json_reporter.py:322`
- 🔵 **Multiple magic numbers detected (14 found)** - `lib/reporters/markdown_reporter.py:95`
- 🔵 **3 unused imports detected** - `scripts/assess.py`
- 🔵 **Multiple magic numbers detected (12 found)** - `scripts/assess.py:422`
- 🔵 **Multiple magic numbers detected (11 found)** - `scripts/detect_project_type.py:71`
- 🔵 **Multiple magic numbers detected (11 found)** - `tests/test_coupling_analyzer.py:41`
- 🔵 **Multiple magic numbers detected (5 found)** - `tests/test_detect_project_type.py:37`
- 🔵 **Multiple magic numbers detected (8 found)** - `tests/test_javascript_parser.py:66`
- 🔵 **Multiple magic numbers detected (6 found)** - `tests/test_python_parser.py:49`
- 🔵 **Multiple magic numbers detected (8 found)** - `tests/test_self_analysis.py:275`
- 🔵 **Multiple magic numbers detected (9 found)** - `tests/test_solid_analyzer.py:309`

### Coupling & Dependencies (11 issues)

- 🔴 **Circular dependency detected involving 2 modules** - `lib/reporters/json_reporter.py`
- 🔴 **Circular dependency detected involving 2 modules** - `tests/fixtures/express-api/app.js`
- 🟠 **Excessive coupling detected (FAN-OUT: 18)** - `scripts/assess.py`
- 🟡 **High coupling detected (FAN-OUT: 8)** - `lib/analyzers/__init__.py`
- 🟡 **High coupling detected (FAN-OUT: 7)** - `lib/analyzers/base.py`
- 🟡 **High coupling detected (FAN-OUT: 7)** - `lib/analyzers/coupling_analyzer.py`
- 🟡 **High coupling detected (FAN-OUT: 8)** - `lib/analyzers/layer_analyzer.py`
- 🟡 **High coupling detected (FAN-OUT: 8)** - `lib/analyzers/pattern_analyzer.py`
- 🟡 **High coupling detected (FAN-OUT: 8)** - `lib/analyzers/solid_analyzer.py`
- 🟡 **High coupling detected (FAN-OUT: 7)** - `scripts/detect_project_type.py`
- 🟡 **High coupling detected (FAN-OUT: 7)** - `tests/test_layer_analyzer.py`


---

## 5. Recommended Actions

### 🔴 Priority 0: Immediate Action Required

Address these 2 critical issue(s) immediately:

1. **Circular dependency detected involving 2 modules** in `lib/reporters/json_reporter.py`
   - Break the circular dependency by:
- Extracting shared code to a new module that both can depend on
- Using dependency injection to invert one of the dependencies
- Applying the Dependency Inversion Principle
- Refactoring to establish a clear dependency hierarchy
2. **Circular dependency detected involving 2 modules** in `tests/fixtures/express-api/app.js`
   - Break the circular dependency by:
- Extracting shared code to a new module that both can depend on
- Using dependency injection to invert one of the dependencies
- Applying the Dependency Inversion Principle
- Refactoring to establish a clear dependency hierarchy

### 🟠 Priority 1: Address in Next Sprint

Plan to resolve these 14 high-priority issue(s):

1. **Long method detected: '_check_database_patterns' (115 lines)** in `lib/analyzers/layer_analyzer.py`
2. **God Class detected: 'PatternAnalyzer' (594 LOC)** in `lib/analyzers/pattern_analyzer.py`
3. **God Class detected: 'SOLIDAnalyzer' (652 LOC)** in `lib/analyzers/solid_analyzer.py`
4. **Long method detected: '_analyze_srp' (123 lines)** in `lib/analyzers/solid_analyzer.py`
5. **Long method detected: 'to_markdown' (122 lines)** in `lib/models/assessment.py`
   ... and 9 more

### 🟡 Priority 2: Plan for Next Quarter

Consider addressing these 96 medium-priority improvement(s).

### 🔵 Priority 3: Nice to Have

Optional improvements: 17 low-priority suggestion(s).


---

## Appendix: Detailed Violation List

Total violations: 129

| ID | Type | Severity | File | Line | Message |
|---|---|---|---|---|---|
| CPL-010 | CircularDependency | CRITICAL | `lib/reporters/json_reporter.py` | - | Circular dependency detected involving 2 modules |
| CPL-011 | CircularDependency | CRITICAL | `tests/fixtures/express-api/app.js` | - | Circular dependency detected involving 2 modules |
| PAT-033 | LongMethod | HIGH | `lib/analyzers/layer_analyzer.py` | 328 | Long method detected: '_check_database_patterns... |
| SRP-017 | SRPViolation | HIGH | `lib/analyzers/pattern_analyzer.py` | 25 | God Class detected: 'PatternAnalyzer' (594 LOC) |
| SRP-013 | SRPViolation | HIGH | `lib/analyzers/solid_analyzer.py` | 29 | God Class detected: 'SOLIDAnalyzer' (652 LOC) |
| PAT-026 | LongMethod | HIGH | `lib/analyzers/solid_analyzer.py` | 119 | Long method detected: '_analyze_srp' (123 lines) |
| PAT-075 | LongMethod | HIGH | `lib/models/assessment.py` | 120 | Long method detected: 'to_markdown' (122 lines) |
| PAT-077 | LongMethod | HIGH | `lib/models/project_type.py` | 72 | Long method detected: 'get_expected_patterns' (... |
| PAT-051 | LongMethod | HIGH | `lib/parsers/javascript_parser.py` | 151 | Long method detected: 'extract_imports' (127 li... |
| PAT-054 | ComplexMethod | HIGH | `lib/parsers/javascript_parser.py` | 151 | Complex method detected: 'extract_imports' (com... |
| PAT-060 | ComplexMethod | HIGH | `lib/parsers/python_parser.py` | 198 | Complex method detected: '_extract_classes_from... |
| SRP-024 | SRPViolation | HIGH | `lib/reporters/markdown_reporter.py` | 20 | God Class detected: 'MarkdownReporter' (515 LOC) |
| CPL-001 | HighCoupling | HIGH | `scripts/assess.py` | - | Excessive coupling detected (FAN-OUT: 18) |
| PAT-002 | LongMethod | HIGH | `scripts/assess.py` | 542 | Long method detected: 'main' (161 lines) |
| PAT-006 | ComplexMethod | HIGH | `scripts/assess.py` | 542 | Complex method detected: 'main' (complexity: 18) |
| LSV-001 | DirectDatabaseAccess | HIGH | `.../fixtures/express-api/routes/users.js` | 10 | Direct ORM usage in presentation layer |
| CPL-009 | HighCoupling | MEDIUM | `lib/analyzers/__init__.py` | - | High coupling detected (FAN-OUT: 8) |
| CPL-003 | HighCoupling | MEDIUM | `lib/analyzers/base.py` | - | High coupling detected (FAN-OUT: 7) |
| SRP-015 | SRPViolation | MEDIUM | `lib/analyzers/base.py` | 58 | Class 'BaseAnalyzer' has too many methods (12) |
| ISP-008 | ISPViolation | MEDIUM | `lib/analyzers/base.py` | 58 | Fat interface: 'BaseAnalyzer' has 12 methods |
| ISP-009 | ISPViolation | MEDIUM | `lib/analyzers/base.py` | 58 | Class 'BaseAnalyzer' has 3 stub methods |
| PAT-039 | LongMethod | MEDIUM | `lib/analyzers/base.py` | 141 | Long method detected: 'create_violation' (58 li... |
| CPL-005 | HighCoupling | MEDIUM | `lib/analyzers/coupling_analyzer.py` | - | High coupling detected (FAN-OUT: 7) |
| PAT-035 | LongMethod | MEDIUM | `lib/analyzers/coupling_analyzer.py` | 111 | Long method detected: '_analyze_fan_out' (67 li... |
| PAT-036 | LongMethod | MEDIUM | `lib/analyzers/coupling_analyzer.py` | 179 | Long method detected: '_analyze_fan_in' (62 lines) |
| PAT-037 | LongMethod | MEDIUM | `lib/analyzers/coupling_analyzer.py` | 242 | Long method detected: '_analyze_circular_depend... |
| PAT-038 | LongMethod | MEDIUM | `lib/analyzers/coupling_analyzer.py` | 302 | Long method detected: '_analyze_deep_chains' (6... |
| CPL-008 | HighCoupling | MEDIUM | `lib/analyzers/layer_analyzer.py` | - | High coupling detected (FAN-OUT: 8) |
| PAT-034 | LongMethod | MEDIUM | `lib/analyzers/layer_analyzer.py` | 444 | Long method detected: '_analyze_layer_dependenc... |
| CPL-006 | HighCoupling | MEDIUM | `lib/analyzers/pattern_analyzer.py` | - | High coupling detected (FAN-OUT: 8) |
| SRP-016 | SRPViolation | MEDIUM | `lib/analyzers/pattern_analyzer.py` | 25 | Class 'PatternAnalyzer' has too many methods (12) |
| ISP-010 | ISPViolation | MEDIUM | `lib/analyzers/pattern_analyzer.py` | 25 | Fat interface: 'PatternAnalyzer' has 12 methods |
| PAT-041 | LongMethod | MEDIUM | `lib/analyzers/pattern_analyzer.py` | 71 | Long method detected: 'analyze' (57 lines) |
| PAT-042 | LongMethod | MEDIUM | `lib/analyzers/pattern_analyzer.py` | 129 | Long method detected: '_detect_magic_numbers' (... |
| PAT-043 | LongMethod | MEDIUM | `lib/analyzers/pattern_analyzer.py` | 195 | Long method detected: '_detect_long_methods' (5... |
| PAT-044 | LongMethod | MEDIUM | `lib/analyzers/pattern_analyzer.py` | 252 | Long method detected: '_detect_complex_methods'... |
| PAT-045 | LongMethod | MEDIUM | `lib/analyzers/pattern_analyzer.py` | 307 | Long method detected: '_detect_dead_code' (65 l... |
| PAT-046 | LongMethod | MEDIUM | `lib/analyzers/pattern_analyzer.py` | 373 | Long method detected: '_detect_factory_opportun... |
| PAT-047 | LongMethod | MEDIUM | `lib/analyzers/pattern_analyzer.py` | 439 | Long method detected: '_detect_strategy_opportu... |
| PAT-048 | LongMethod | MEDIUM | `lib/analyzers/pattern_analyzer.py` | 507 | Long method detected: '_detect_singleton_misuse... |
| CPL-002 | HighCoupling | MEDIUM | `lib/analyzers/solid_analyzer.py` | - | High coupling detected (FAN-OUT: 8) |
| SRP-012 | SRPViolation | MEDIUM | `lib/analyzers/solid_analyzer.py` | 29 | Class 'SOLIDAnalyzer' has too many methods (14) |
| SRP-014 | SRPViolation | MEDIUM | `lib/analyzers/solid_analyzer.py` | 29 | Low cohesion in class 'SOLIDAnalyzer' (LCOM: 0.89) |
| ISP-007 | ISPViolation | MEDIUM | `lib/analyzers/solid_analyzer.py` | 29 | Fat interface: 'SOLIDAnalyzer' has 14 methods |
| PAT-025 | LongMethod | MEDIUM | `lib/analyzers/solid_analyzer.py` | 64 | Long method detected: 'analyze' (54 lines) |
| PAT-027 | LongMethod | MEDIUM | `lib/analyzers/solid_analyzer.py` | 243 | Long method detected: '_analyze_ocp' (70 lines) |
| PAT-028 | LongMethod | MEDIUM | `lib/analyzers/solid_analyzer.py` | 314 | Long method detected: '_analyze_lsp' (75 lines) |
| PAT-029 | LongMethod | MEDIUM | `lib/analyzers/solid_analyzer.py` | 390 | Long method detected: '_analyze_isp' (97 lines) |
| PAT-030 | LongMethod | MEDIUM | `lib/analyzers/solid_analyzer.py` | 488 | Long method detected: '_analyze_dip' (60 lines) |
| PAT-031 | ComplexMethod | MEDIUM | `lib/analyzers/solid_analyzer.py` | 565 | Complex method detected: '_calculate_lcom' (com... |
| SRP-018 | SRPViolation | MEDIUM | `lib/graph/dependency_graph.py` | 69 | Class 'DependencyGraph' has too many methods (16) |
| ISP-011 | ISPViolation | MEDIUM | `lib/graph/dependency_graph.py` | 69 | Fat interface: 'DependencyGraph' has 16 methods |
| PAT-050 | LongMethod | MEDIUM | `lib/graph/dependency_graph.py` | 175 | Long method detected: 'detect_cycles' (51 lines) |
| SRP-026 | SRPViolation | MEDIUM | `lib/models/metrics.py` | 125 | Low cohesion in class 'ProjectMetrics' (LCOM: 0... |
| SRP-025 | SRPViolation | MEDIUM | `lib/models/project_type.py` | 15 | Low cohesion in class 'ProjectType' (LCOM: 1.00) |
| SRP-020 | SRPViolation | MEDIUM | `lib/parsers/base.py` | 127 | Low cohesion in class 'BaseParser' (LCOM: 0.93) |
| ISP-012 | ISPViolation | MEDIUM | `lib/parsers/base.py` | 127 | Class 'BaseParser' has 3 stub methods |
| SRP-019 | SRPViolation | MEDIUM | `lib/parsers/javascript_parser.py` | 31 | Low cohesion in class 'JavaScriptParser' (LCOM:... |
| PAT-056 | FactoryOpportunity | MEDIUM | `lib/parsers/javascript_parser.py` | 268 | Factory pattern opportunity: 'ImportStatement' ... |
| PAT-052 | LongMethod | MEDIUM | `lib/parsers/javascript_parser.py` | 279 | Long method detected: 'extract_classes' (52 lines) |
| PAT-053 | LongMethod | MEDIUM | `lib/parsers/javascript_parser.py` | 332 | Long method detected: 'extract_functions' (56 l... |
| PAT-057 | FactoryOpportunity | MEDIUM | `lib/parsers/javascript_parser.py` | 351 | Factory pattern opportunity: 'FunctionDefinitio... |
| PAT-055 | ComplexMethod | MEDIUM | `lib/parsers/javascript_parser.py` | 434 | Complex method detected: '_parse_parameters' (c... |
| SRP-021 | SRPViolation | MEDIUM | `lib/parsers/python_parser.py` | 31 | Low cohesion in class 'PythonParser' (LCOM: 0.84) |
| PAT-059 | LongMethod | MEDIUM | `lib/parsers/python_parser.py` | 198 | Long method detected: '_extract_classes_from_as... |
| PAT-063 | LongMethod | MEDIUM | `lib/reporters/json_reporter.py` | 138 | Long method detected: '_build_metrics' (53 lines) |
| PAT-064 | LongMethod | MEDIUM | `lib/reporters/json_reporter.py` | 200 | Long method detected: '_build_recommended_actio... |
| PAT-065 | ComplexMethod | MEDIUM | `lib/reporters/json_reporter.py` | 200 | Complex method detected: '_build_recommended_ac... |
| PAT-062 | LongMethod | MEDIUM | `lib/reporters/json_reporter.py` | 296 | Long method detected: 'generate_ci_summary' (61... |
| SRP-023 | SRPViolation | MEDIUM | `lib/reporters/markdown_reporter.py` | 20 | Class 'MarkdownReporter' has too many methods (13) |
| ISP-014 | ISPViolation | MEDIUM | `lib/reporters/markdown_reporter.py` | 20 | Fat interface: 'MarkdownReporter' has 13 methods |
| PAT-069 | LongMethod | MEDIUM | `lib/reporters/markdown_reporter.py` | 76 | Long method detected: '_executive_summary' (68 ... |
| PAT-070 | LongMethod | MEDIUM | `lib/reporters/markdown_reporter.py` | 164 | Long method detected: '_metrics_dashboard' (70 ... |
| PAT-074 | ComplexMethod | MEDIUM | `lib/reporters/markdown_reporter.py` | 164 | Complex method detected: '_metrics_dashboard' (... |
| PAT-071 | LongMethod | MEDIUM | `lib/reporters/markdown_reporter.py` | 235 | Long method detected: '_violations_by_severity'... |
| PAT-072 | LongMethod | MEDIUM | `lib/reporters/markdown_reporter.py` | 302 | Long method detected: '_violations_by_dimension... |
| PAT-073 | LongMethod | MEDIUM | `lib/reporters/markdown_reporter.py` | 366 | Long method detected: '_recommended_actions' (7... |
| SRP-022 | SRPViolation | MEDIUM | `lib/reporters/task_generator.py` | 19 | Class 'TaskGenerator' has too many methods (11) |
| ISP-013 | ISPViolation | MEDIUM | `lib/reporters/task_generator.py` | 19 | Fat interface: 'TaskGenerator' has 11 methods |
| PAT-066 | LongMethod | MEDIUM | `lib/reporters/task_generator.py` | 252 | Long method detected: '_format_task' (70 lines) |
| PAT-067 | LongMethod | MEDIUM | `lib/reporters/task_generator.py` | 323 | Long method detected: '_format_grouped_task' (6... |
| SRP-001 | SRPViolation | MEDIUM | `scripts/assess.py` | 87 | Class 'AssessmentOrchestrator' has too many met... |
| ISP-001 | ISPViolation | MEDIUM | `scripts/assess.py` | 87 | Fat interface: 'AssessmentOrchestrator' has 11 ... |
| PAT-003 | LongMethod | MEDIUM | `scripts/assess.py` | 128 | Long method detected: 'run' (65 lines) |
| PAT-004 | LongMethod | MEDIUM | `scripts/assess.py` | 213 | Long method detected: '_discover_files' (63 lines) |
| PAT-005 | LongMethod | MEDIUM | `scripts/assess.py` | 277 | Long method detected: '_parse_files' (51 lines) |
| CPL-004 | HighCoupling | MEDIUM | `scripts/detect_project_type.py` | - | High coupling detected (FAN-OUT: 7) |
| SRP-002 | SRPViolation | MEDIUM | `scripts/detect_project_type.py` | 36 | Class 'ProjectTypeDetector' has too many method... |
| ISP-002 | ISPViolation | MEDIUM | `scripts/detect_project_type.py` | 36 | Fat interface: 'ProjectTypeDetector' has 18 met... |
| PAT-009 | ComplexMethod | MEDIUM | `scripts/detect_project_type.py` | 49 | Complex method detected: 'detect' (complexity: 14) |
| PAT-010 | StrategyOpportunity | MEDIUM | `scripts/detect_project_type.py` | 70 | Strategy pattern opportunity in 'detect' (11 br... |
| PAT-011 | StrategyOpportunity | MEDIUM | `scripts/detect_project_type.py` | 72 | Strategy pattern opportunity in 'detect' (10 br... |
| PAT-012 | StrategyOpportunity | MEDIUM | `scripts/detect_project_type.py` | 74 | Strategy pattern opportunity in 'detect' (9 bra... |
| PAT-013 | StrategyOpportunity | MEDIUM | `scripts/detect_project_type.py` | 76 | Strategy pattern opportunity in 'detect' (8 bra... |
| PAT-014 | StrategyOpportunity | MEDIUM | `scripts/detect_project_type.py` | 78 | Strategy pattern opportunity in 'detect' (7 bra... |
| PAT-015 | StrategyOpportunity | MEDIUM | `scripts/detect_project_type.py` | 80 | Strategy pattern opportunity in 'detect' (6 bra... |
| PAT-016 | StrategyOpportunity | MEDIUM | `scripts/detect_project_type.py` | 84 | Strategy pattern opportunity in 'detect' (5 bra... |
| SRP-007 | SRPViolation | MEDIUM | `tests/test_detect_project_type.py` | 20 | Class 'TestProjectTypeDetector' has too many me... |
| SRP-008 | SRPViolation | MEDIUM | `tests/test_detect_project_type.py` | 20 | Low cohesion in class 'TestProjectTypeDetector'... |
| ISP-005 | ISPViolation | MEDIUM | `tests/test_detect_project_type.py` | 20 | Fat interface: 'TestProjectTypeDetector' has 13... |
| SRP-005 | SRPViolation | MEDIUM | `tests/test_integration.py` | 27 | Class 'TestIntegration' has too many methods (11) |
| SRP-006 | SRPViolation | MEDIUM | `tests/test_integration.py` | 27 | Low cohesion in class 'TestIntegration' (LCOM: ... |
| ISP-004 | ISPViolation | MEDIUM | `tests/test_integration.py` | 27 | Fat interface: 'TestIntegration' has 11 methods |
| SRP-010 | SRPViolation | MEDIUM | `tests/test_javascript_parser.py` | 20 | Class 'TestJavaScriptParser' has too many metho... |
| SRP-011 | SRPViolation | MEDIUM | `tests/test_javascript_parser.py` | 20 | Low cohesion in class 'TestJavaScriptParser' (L... |
| ISP-006 | ISPViolation | MEDIUM | `tests/test_javascript_parser.py` | 20 | Fat interface: 'TestJavaScriptParser' has 30 me... |
| CPL-007 | HighCoupling | MEDIUM | `tests/test_layer_analyzer.py` | - | High coupling detected (FAN-OUT: 7) |
| SRP-003 | SRPViolation | MEDIUM | `tests/test_python_parser.py` | 20 | Class 'TestPythonParser' has too many methods (21) |
| SRP-004 | SRPViolation | MEDIUM | `tests/test_python_parser.py` | 20 | Low cohesion in class 'TestPythonParser' (LCOM:... |
| ISP-003 | ISPViolation | MEDIUM | `tests/test_python_parser.py` | 20 | Fat interface: 'TestPythonParser' has 21 methods |
| SRP-009 | SRPViolation | MEDIUM | `tests/test_self_analysis.py` | 29 | Low cohesion in class 'TestSelfAnalysis' (LCOM:... |
| PAT-022 | LongMethod | MEDIUM | `tests/test_self_analysis.py` | 42 | Long method detected: 'test_self_analysis_runs_... |
| PAT-049 | UnusedImports | LOW | `lib/analyzers/pattern_analyzer.py` | - | 3 unused imports detected |
| PAT-040 | MagicNumbers | LOW | `lib/analyzers/pattern_analyzer.py` | 163 | Multiple magic numbers detected (9 found) |
| PAT-032 | UnusedImports | LOW | `lib/analyzers/solid_analyzer.py` | - | 7 unused imports detected |
| PAT-024 | MagicNumbers | LOW | `lib/analyzers/solid_analyzer.py` | 213 | Multiple magic numbers detected (5 found) |
| PAT-076 | UnusedImports | LOW | `lib/models/__init__.py` | - | 14 unused imports detected |
| PAT-058 | UnusedImports | LOW | `lib/parsers/__init__.py` | - | 5 unused imports detected |
| PAT-061 | MagicNumbers | LOW | `lib/reporters/json_reporter.py` | 322 | Multiple magic numbers detected (9 found) |
| PAT-068 | MagicNumbers | LOW | `lib/reporters/markdown_reporter.py` | 95 | Multiple magic numbers detected (14 found) |
| PAT-007 | UnusedImports | LOW | `scripts/assess.py` | - | 3 unused imports detected |
| PAT-001 | MagicNumbers | LOW | `scripts/assess.py` | 422 | Multiple magic numbers detected (12 found) |
| PAT-008 | MagicNumbers | LOW | `scripts/detect_project_type.py` | 71 | Multiple magic numbers detected (11 found) |
| PAT-018 | MagicNumbers | LOW | `tests/test_coupling_analyzer.py` | 41 | Multiple magic numbers detected (11 found) |
| PAT-019 | MagicNumbers | LOW | `tests/test_detect_project_type.py` | 37 | Multiple magic numbers detected (5 found) |
| PAT-023 | MagicNumbers | LOW | `tests/test_javascript_parser.py` | 66 | Multiple magic numbers detected (8 found) |
| PAT-017 | MagicNumbers | LOW | `tests/test_python_parser.py` | 49 | Multiple magic numbers detected (6 found) |
| PAT-021 | MagicNumbers | LOW | `tests/test_self_analysis.py` | 275 | Multiple magic numbers detected (8 found) |
| PAT-020 | MagicNumbers | LOW | `tests/test_solid_analyzer.py` | 309 | Multiple magic numbers detected (9 found) |

---

*Report generated by Architecture Quality Assessment Skill*
*Tool Version: 1.0.0*