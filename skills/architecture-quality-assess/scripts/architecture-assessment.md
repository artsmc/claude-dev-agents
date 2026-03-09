# Architecture Quality Assessment Report

**Generated**: 2026-02-11T13:01:12.547140
**Project**: scripts
**Path**: /home/artsmc/.claude/skills/architecture-quality-assess/scripts
**Analysis Duration**: 0.10 seconds

---

## Executive Summary

**Overall Score**: 10/100 (Needs Improvement ❌)

**Total Issues**: 23
- **Critical**: 1 🔴
- **High**: 3 🟠
- **Medium**: 16 🟡
- **Low**: 3 🔵

⚠️ **Action Required**: 1 critical issue(s) detected that should be addressed immediately.

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

- **Average FAN-OUT**: 13.00
- **Max FAN-OUT**: 19
- **Total Modules Analyzed**: 2

**Most Coupled Modules**:

- `assess.py` (FAN-OUT: 19)
- `detect_project_type.py` (FAN-OUT: 7)

### Code Organization

- **Total Files Analyzed**: 2


---

## 3. Violations by Severity

### 🔴 CRITICAL (1 issue)

#### 1. Circular dependency detected involving 2 modules

**Type**: CircularDependency
**File**: `assess.py`

**Issue**: A circular dependency cycle was detected:

assess.py -> assess.py

Circular dependencies make code harder to understand, test, and maintain. They can cause initialization issues and make refactoring difficult.

**Recommendation**: Break the circular dependency by:
- Extracting shared code to a new module that both can depend on
- Using dependency injection to invert one of the dependencies
- Applying the Dependency Inversion Principle
- Refactoring to establish a clear dependency hierarchy

**Additional Details**:
- Cycle:
  - assess.py
  - assess.py
- Cycle Length: 2

### 🟠 HIGH (3 issues)

#### 1. Excessive coupling detected (FAN-OUT: 19)

**Type**: HighCoupling
**File**: `assess.py`

**Issue**: Module 'assess.py' depends on 19 other modules, indicating tight coupling. High FAN-OUT makes the module fragile and difficult to maintain, as changes in dependencies may require changes here.

Dependencies:
  - argparse
  - assess.py
  - datetime
  - detect_project_type.py
  - hashlib
  - json
  - lib.analyzers
  - lib.analyzers.base
  - lib.graph.dependency_graph
  - lib.models.config
  ... and 9 more

**Recommendation**: Consider refactoring to reduce dependencies:
- Extract shared logic to dedicated utility modules
- Apply Dependency Inversion Principle (depend on abstractions)
- Use dependency injection to reduce direct coupling
- Break down large module into smaller, focused modules

**Additional Details**:
- Fan Out: 19
- Fan In: 1
- Instability: 0.95
- Dependencies:
  - lib.models.metrics
  - json
  - sys
  - argparse
  - lib.parsers.base
  - lib.reporters
  - lib.analyzers
  - logging
  - lib.graph.dependency_graph
  - lib.models.violation
  - detect_project_type.py
  - datetime
  - pathlib
  - assess.py
  - lib.parsers
  - typing
  - lib.analyzers.base
  - hashlib
  - lib.models.config

#### 2. Long method detected: 'main' (161 lines)

**Type**: LongMethod
**File**: `assess.py`
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

#### 3. Complex method detected: 'main' (complexity: 18)

**Type**: ComplexMethod
**File**: `assess.py`
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

### 🟡 MEDIUM (16 issues)

#### 1. Class 'AssessmentOrchestrator' has too many methods (11)

**Type**: SRPViolation
**File**: `assess.py`
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

#### 2. Fat interface: 'AssessmentOrchestrator' has 11 methods

**Type**: ISPViolation
**File**: `assess.py`
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

#### 3. Long method detected: 'run' (65 lines)

**Type**: LongMethod
**File**: `assess.py`
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

#### 4. Long method detected: '_discover_files' (63 lines)

**Type**: LongMethod
**File**: `assess.py`
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

#### 5. Long method detected: '_parse_files' (51 lines)

**Type**: LongMethod
**File**: `assess.py`
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

#### 6. High coupling detected (FAN-OUT: 7)

**Type**: HighCoupling
**File**: `detect_project_type.py`

**Issue**: Module 'detect_project_type.py' depends on 7 other modules, indicating tight coupling. High FAN-OUT makes the module fragile and difficult to maintain, as changes in dependencies may require changes here.

Dependencies:
  - argparse
  - json
  - lib.models.project_type
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
- Fan In: 1
- Instability: 0.875
- Dependencies:
  - json
  - pathlib
  - sys
  - typing
  - logging
  - lib.models.project_type
  - argparse

#### 7. Class 'ProjectTypeDetector' has too many methods (18)

**Type**: SRPViolation
**File**: `detect_project_type.py`
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

#### 8. Fat interface: 'ProjectTypeDetector' has 18 methods

**Type**: ISPViolation
**File**: `detect_project_type.py`
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

#### 9. Complex method detected: 'detect' (complexity: 14)

**Type**: ComplexMethod
**File**: `detect_project_type.py`
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

#### 10. Strategy pattern opportunity in 'detect' (11 branches)

**Type**: StrategyOpportunity
**File**: `detect_project_type.py`
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

#### 11. Strategy pattern opportunity in 'detect' (10 branches)

**Type**: StrategyOpportunity
**File**: `detect_project_type.py`
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

#### 12. Strategy pattern opportunity in 'detect' (9 branches)

**Type**: StrategyOpportunity
**File**: `detect_project_type.py`
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

#### 13. Strategy pattern opportunity in 'detect' (8 branches)

**Type**: StrategyOpportunity
**File**: `detect_project_type.py`
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

#### 14. Strategy pattern opportunity in 'detect' (7 branches)

**Type**: StrategyOpportunity
**File**: `detect_project_type.py`
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

#### 15. Strategy pattern opportunity in 'detect' (6 branches)

**Type**: StrategyOpportunity
**File**: `detect_project_type.py`
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

#### 16. Strategy pattern opportunity in 'detect' (5 branches)

**Type**: StrategyOpportunity
**File**: `detect_project_type.py`
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

### 🔵 LOW (3 issues)

#### 1. 3 unused imports detected

**Type**: UnusedImports
**File**: `assess.py`

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

#### 2. Multiple magic numbers detected (12 found)

**Type**: MagicNumbers
**File**: `assess.py`
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

#### 3. Multiple magic numbers detected (11 found)

**Type**: MagicNumbers
**File**: `detect_project_type.py`
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


---

## 4. Violations by Analysis Dimension

### SOLID Principles (4 issues)

- 🟡 **Class 'AssessmentOrchestrator' has too many methods (11)** - `assess.py:87`
- 🟡 **Fat interface: 'AssessmentOrchestrator' has 11 methods** - `assess.py:87`
- 🟡 **Class 'ProjectTypeDetector' has too many methods (18)** - `detect_project_type.py:36`
- 🟡 **Fat interface: 'ProjectTypeDetector' has 18 methods** - `detect_project_type.py:36`

### Design Patterns (16 issues)

- 🟠 **Long method detected: 'main' (161 lines)** - `assess.py:542`
- 🟠 **Complex method detected: 'main' (complexity: 18)** - `assess.py:542`
- 🟡 **Long method detected: 'run' (65 lines)** - `assess.py:128`
- 🟡 **Long method detected: '_discover_files' (63 lines)** - `assess.py:213`
- 🟡 **Long method detected: '_parse_files' (51 lines)** - `assess.py:277`
- 🟡 **Complex method detected: 'detect' (complexity: 14)** - `detect_project_type.py:49`
- 🟡 **Strategy pattern opportunity in 'detect' (11 branches)** - `detect_project_type.py:70`
- 🟡 **Strategy pattern opportunity in 'detect' (10 branches)** - `detect_project_type.py:72`
- 🟡 **Strategy pattern opportunity in 'detect' (9 branches)** - `detect_project_type.py:74`
- 🟡 **Strategy pattern opportunity in 'detect' (8 branches)** - `detect_project_type.py:76`
- 🟡 **Strategy pattern opportunity in 'detect' (7 branches)** - `detect_project_type.py:78`
- 🟡 **Strategy pattern opportunity in 'detect' (6 branches)** - `detect_project_type.py:80`
- 🟡 **Strategy pattern opportunity in 'detect' (5 branches)** - `detect_project_type.py:84`
- 🔵 **3 unused imports detected** - `assess.py`
- 🔵 **Multiple magic numbers detected (12 found)** - `assess.py:422`
- 🔵 **Multiple magic numbers detected (11 found)** - `detect_project_type.py:71`

### Coupling & Dependencies (3 issues)

- 🔴 **Circular dependency detected involving 2 modules** - `assess.py`
- 🟠 **Excessive coupling detected (FAN-OUT: 19)** - `assess.py`
- 🟡 **High coupling detected (FAN-OUT: 7)** - `detect_project_type.py`


---

## 5. Recommended Actions

### 🔴 Priority 0: Immediate Action Required

Address these 1 critical issue(s) immediately:

1. **Circular dependency detected involving 2 modules** in `assess.py`
   - Break the circular dependency by:
- Extracting shared code to a new module that both can depend on
- Using dependency injection to invert one of the dependencies
- Applying the Dependency Inversion Principle
- Refactoring to establish a clear dependency hierarchy

### 🟠 Priority 1: Address in Next Sprint

Plan to resolve these 3 high-priority issue(s):

1. **Excessive coupling detected (FAN-OUT: 19)** in `assess.py`
2. **Long method detected: 'main' (161 lines)** in `assess.py`
3. **Complex method detected: 'main' (complexity: 18)** in `assess.py`

### 🟡 Priority 2: Plan for Next Quarter

Consider addressing these 16 medium-priority improvement(s).

### 🔵 Priority 3: Nice to Have

Optional improvements: 3 low-priority suggestion(s).


---

## Appendix: Detailed Violation List

Total violations: 23

| ID | Type | Severity | File | Line | Message |
|---|---|---|---|---|---|
| CPL-003 | CircularDependency | CRITICAL | `assess.py` | - | Circular dependency detected involving 2 modules |
| CPL-001 | HighCoupling | HIGH | `assess.py` | - | Excessive coupling detected (FAN-OUT: 19) |
| PAT-002 | LongMethod | HIGH | `assess.py` | 542 | Long method detected: 'main' (161 lines) |
| PAT-006 | ComplexMethod | HIGH | `assess.py` | 542 | Complex method detected: 'main' (complexity: 18) |
| SRP-001 | SRPViolation | MEDIUM | `assess.py` | 87 | Class 'AssessmentOrchestrator' has too many met... |
| ISP-001 | ISPViolation | MEDIUM | `assess.py` | 87 | Fat interface: 'AssessmentOrchestrator' has 11 ... |
| PAT-003 | LongMethod | MEDIUM | `assess.py` | 128 | Long method detected: 'run' (65 lines) |
| PAT-004 | LongMethod | MEDIUM | `assess.py` | 213 | Long method detected: '_discover_files' (63 lines) |
| PAT-005 | LongMethod | MEDIUM | `assess.py` | 277 | Long method detected: '_parse_files' (51 lines) |
| CPL-002 | HighCoupling | MEDIUM | `detect_project_type.py` | - | High coupling detected (FAN-OUT: 7) |
| SRP-002 | SRPViolation | MEDIUM | `detect_project_type.py` | 36 | Class 'ProjectTypeDetector' has too many method... |
| ISP-002 | ISPViolation | MEDIUM | `detect_project_type.py` | 36 | Fat interface: 'ProjectTypeDetector' has 18 met... |
| PAT-009 | ComplexMethod | MEDIUM | `detect_project_type.py` | 49 | Complex method detected: 'detect' (complexity: 14) |
| PAT-010 | StrategyOpportunity | MEDIUM | `detect_project_type.py` | 70 | Strategy pattern opportunity in 'detect' (11 br... |
| PAT-011 | StrategyOpportunity | MEDIUM | `detect_project_type.py` | 72 | Strategy pattern opportunity in 'detect' (10 br... |
| PAT-012 | StrategyOpportunity | MEDIUM | `detect_project_type.py` | 74 | Strategy pattern opportunity in 'detect' (9 bra... |
| PAT-013 | StrategyOpportunity | MEDIUM | `detect_project_type.py` | 76 | Strategy pattern opportunity in 'detect' (8 bra... |
| PAT-014 | StrategyOpportunity | MEDIUM | `detect_project_type.py` | 78 | Strategy pattern opportunity in 'detect' (7 bra... |
| PAT-015 | StrategyOpportunity | MEDIUM | `detect_project_type.py` | 80 | Strategy pattern opportunity in 'detect' (6 bra... |
| PAT-016 | StrategyOpportunity | MEDIUM | `detect_project_type.py` | 84 | Strategy pattern opportunity in 'detect' (5 bra... |
| PAT-007 | UnusedImports | LOW | `assess.py` | - | 3 unused imports detected |
| PAT-001 | MagicNumbers | LOW | `assess.py` | 422 | Multiple magic numbers detected (12 found) |
| PAT-008 | MagicNumbers | LOW | `detect_project_type.py` | 71 | Multiple magic numbers detected (11 found) |

---

*Report generated by Architecture Quality Assessment Skill*
*Tool Version: 1.0.0*