# Code Duplication Analysis Report

**Generated:** 2026-02-24 14:55:00

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Duplicate Blocks](#duplicate-blocks)
3. [Recommendations](#recommendations)

---

## 📊 Executive Summary

### Overall Metrics

- **Files Analyzed:** 14
- **Total Lines of Code:** 4,414
- **Duplicate Lines:** 2,448
- **Duplication Percentage:** 55.46%
- **Duplicate Blocks Found:** 8

### Breakdown by Type

- **🔴 Exact Duplicates:** 4
- **🟡 Structural Duplicates:** 1
- **🔵 Pattern Duplicates:** 3

### Assessment

🔴 **Critical** - Excessive duplication, immediate action required

### 🎯 Top File Offenders

Files with the most duplicate code:

1. `/home/artsmc/.claude/skills/code-duplication/scripts/suggestion_engine.py` - 302/564 LOC (53.5%, 2 blocks)
2. `/home/artsmc/.claude/skills/code-duplication/scripts/cli.py` - 106/549 LOC (19.3%, 8 blocks)
3. `/home/artsmc/.claude/skills/code-duplication/scripts/git_integration.py` - 40/351 LOC (11.4%, 8 blocks)
4. `/home/artsmc/.claude/skills/code-duplication/scripts/pattern_detector.py` - 15/277 LOC (5.4%, 5 blocks)
5. `/home/artsmc/.claude/skills/code-duplication/scripts/models.py` - 10/323 LOC (3.1%, 2 blocks)
6. `/home/artsmc/.claude/skills/code-duplication/scripts/file_discovery.py` - 4/307 LOC (1.3%, 1 blocks)
7. `/home/artsmc/.claude/skills/code-duplication/scripts/exact_detector.py` - 1/227 LOC (0.4%, 1 blocks)

### 🗺️ Duplication Heatmap

```
Duplication Heatmap:
================================================================================
Legend: ░=Low(1-10%) ▒=Med(10-25%) ▓=High(25-50%) █=Critical(50%+)

█ /home/artsmc/.claude/skills/code-duplication/scripts/suggestion_engine.py   53.5% (302/564 LOC)
▒ /home/artsmc/.claude/skills/code-duplication/scripts/cli.py   19.3% (106/549 LOC)
▒ /home/artsmc/.claude/skills/code-duplication/scripts/git_integration.py   11.4% (40/351 LOC)
░ /home/artsmc/.claude/skills/code-duplication/scripts/pattern_detector.py    5.4% (15/277 LOC)
░ /home/artsmc/.claude/skills/code-duplication/scripts/models.py    3.1% (10/323 LOC)
░ /home/artsmc/.claude/skills/code-duplication/scripts/file_discovery.py    1.3% (4/307 LOC)
░ /home/artsmc/.claude/skills/code-duplication/scripts/exact_detector.py    0.4% (1/227 LOC)
  /home/artsmc/.claude/skills/code-duplication/scripts/utils.py    0.0% (0/288 LOC)
  /home/artsmc/.claude/skills/code-duplication/scripts/config_loader.py    0.0% (0/215 LOC)
  /home/artsmc/.claude/skills/code-duplication/scripts/heatmap_renderer.py    0.0% (0/155 LOC)
  /home/artsmc/.claude/skills/code-duplication/scripts/gitignore_parser.py    0.0% (0/235 LOC)
  /home/artsmc/.claude/skills/code-duplication/scripts/report_generator.py    0.0% (0/422 LOC)
  /home/artsmc/.claude/skills/code-duplication/scripts/structural_detector.py    0.0% (0/292 LOC)
  /home/artsmc/.claude/skills/code-duplication/scripts/metrics_calculator.py    0.0% (0/209 LOC)
```

## 📋 Duplicate Blocks

Found **8 duplicate blocks** across the codebase.

### 🔴 Duplicate #1/8 - EXACT

**Type:** exact
**Instances:** 3
**Similarity:** 100.0%
**Hash:** `f0e49f514adf...`

**Found in:**
- `/home/artsmc/.claude/skills/code-duplication/scripts/git_integration.py:L174-178` (5 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/git_integration.py:L190-194` (5 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/git_integration.py:L206-210` (5 lines)

**Code Sample:**
```python
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            file_path = git_root / line
```

---

### 🔴 Duplicate #2/8 - EXACT

**Type:** exact
**Instances:** 3
**Similarity:** 100.0%
**Hash:** `72021d71a0b4...`

**Found in:**
- `/home/artsmc/.claude/skills/code-duplication/scripts/git_integration.py:L176-180` (5 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/git_integration.py:L192-196` (5 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/git_integration.py:L208-212` (5 lines)

**Code Sample:**
```python
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            file_path = git_root / line
                            if file_path.exists():
                                modified_files.add(file_path)
```

---

### 🔴 Duplicate #3/8 - EXACT

**Type:** exact
**Instances:** 2
**Similarity:** 100.0%
**Hash:** `c1de95b9f15f...`

**Found in:**
- `/home/artsmc/.claude/skills/code-duplication/scripts/pattern_detector.py:L246-251` (6 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/pattern_detector.py:L357-362` (6 lines)

**Code Sample:**
```python
    for file_path, content, language in files_content:
        if language != 'python':
            continue  # Only Python patterns for now
        for pattern in patterns:
            matches = match_pattern(content, pattern, file_path)
```

---

### 🔴 Duplicate #4/8 - EXACT

**Type:** exact
**Instances:** 2
**Similarity:** 100.0%
**Hash:** `85dbba35d3f6...`

**Found in:**
- `/home/artsmc/.claude/skills/code-duplication/scripts/git_integration.py:L255-259` (5 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/git_integration.py:L308-312` (5 lines)

**Code Sample:**
```python
        files = []
        for line in result.stdout.strip().split('\n'):
            if line:
                file_path = git_root / line
                if file_path.exists():
```

---

### 🟡 Duplicate #5/8 - STRUCTURAL

**Type:** structural
**Instances:** 2
**Similarity:** 100.0%
**Hash:** `cdaacdcefa46...`

**Found in:**
- `/home/artsmc/.claude/skills/code-duplication/scripts/models.py:L170-174` (5 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/models.py:L265-269` (5 lines)

**Code Sample:**
```python
@VAR_1
def FUNC_0(VAR_0) -> VAR_2:
    """STRING"""
    if VAR_0.total_loc == 0:
        return 0
    return VAR_0.duplicate_loc / VAR_0.total_loc * 0
```

---

### 🔵 Duplicate #6/8 - PATTERN

**Type:** pattern
**Instances:** 9
**Similarity:** 100.0%
**Hash:** `try-catch-lo...`

**Found in:**
- `/home/artsmc/.claude/skills/code-duplication/scripts/suggestion_engine.py:L58-358` (301 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/cli.py:L303-314` (12 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/cli.py:L367-383` (17 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/cli.py:L471-483` (13 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/cli.py:L500-512` (13 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/cli.py:L529-541` (13 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/cli.py:L557-571` (15 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/cli.py:L580-594` (15 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/cli.py:L611-618` (8 lines)

**Code Sample:**
```python
try:
            suggestion = _generate_suggestion_for_duplicate(duplicate, config)
            duplicate.suggestion = suggestion
        except Exception as e:
            # Don't fail entire analysis if suggestion generation fails
            # Log error but continue (could enhance with logging module)
            duplicate.suggestion = _create_fallback_suggestion(duplicate)

    return duplicates


def _generate_suggestion_for_duplicate(
    duplicate: DuplicateBlock,
    config: Config
) -> RefactoringSuggestion:
... (truncated)
```

**💡 Refactoring Suggestion:**
- **Technique:** extract_function
- **Difficulty:** medium
- **Estimated LOC Reduction:** 45 lines

**Description:** Extract into a @retry_with_logging decorator or error handling utility function

**Implementation Steps:**
1. Identify all 9 instances of this pattern
2. Extract common logic into a utility function/decorator
3. Replace all instances with the utility call
4. Test thoroughly to ensure behavior is preserved

**Example Refactored Code:**
```python
try:
            suggestion = _generate_suggestion_for_duplicate(duplicate, config)
            duplicate.suggestion = suggestion
        except Exception as e:
            # Don't fail entire analysis if suggestion generation fails
            # Log error but continue (could enhance with logging module)
            duplicate.suggestion = _create_fallback_suggestion(duplicate)

    return duplicates


def _generate_suggestion_for_duplicate(
    duplicate: DuplicateBlock,
    config: Config
) -> RefactoringSuggestion:
    """
    Generate a specific refactoring suggestion for a duplicate block.

    Uses decision tree to select appropriate technique based on:
    - Duplicate type (exact, structural, pattern)
    - Code location context (same file, same class, cross-module)
    - Instance count and distribution

    Args:
        duplicate: DuplicateBlock to analyze
        config: Configuration object

    Returns:
        RefactoringSuggestion object with technique and steps
    """
    # Analyze context
    context = _analyze_duplicate_context(duplicate)

    # Select refactoring technique using decision tree
    technique = _select_refactoring_technique(duplicate, context)

    # Generate description
    description = _generate_description(duplicate, technique, context)

    # Estimate LOC reduction
    loc_reduction = _estimate_loc_reduction(duplicate, technique)

    # Generate implementation steps
    steps = _generate_implementation_steps(duplicate, technique, context)

    # Determine difficulty
    difficulty = _estimate_difficulty(duplicate, technique, context)

    # Create example code (optional enhancement for future)
    example_code = None

    return RefactoringSuggestion(
        technique=technique,
        description=description,
        estimated_loc_reduction=loc_reduction,
        implementation_steps=steps,
        example_code=example_code,
        difficulty=difficulty
    )


def _analyze_duplicate_context(duplicate: DuplicateBlock) -> Dict[str, any]:
    """
    Analyze the context of duplicate instances.

    Determines relationships between duplicate instances:
    - Are they in the same file?
    - Are they in the same directory/module?
    - Are they in related classes?
    - What is the file distribution pattern?

    Args:
        duplicate: DuplicateBlock to analyze

    Returns:
        Dictionary containing context information:
        - same_file: bool
        - same_directory: bool
        - same_class: bool
        - related_classes: bool
        - cross_module: bool
        - file_count: int
        - directory_count: int
        - is_cross_cutting: bool
        - is_parameterizable: bool
    """
    instances = duplicate.instances

    # Get unique files and directories
    files = set(loc.file_path for loc in instances)
    directories = set(str(Path(loc.file_path).parent) for loc in instances)

    # Analyze file patterns
    same_file = len(files) == 1
    same_directory = len(directories) == 1

    # Analyze class relationships (heuristic based on file names)
    same_class = _check_same_class(instances)
    related_classes = _check_related_classes(instances)

    # Check for cross-module duplicates
    cross_module = _check_cross_module(instances)

    # Check for cross-cutting concerns (heuristic based on code patterns)
    is_cross_cutting = _check_cross_cutting_concern(duplicate)

    # Check if code appears parameterizable
    is_parameterizable = _check_parameterizable(duplicate)

    return {
        'same_file': same_file,
        'same_directory': same_directory,
        'same_class': same_class,
        'related_classes': related_classes,
        'cross_module': cross_module,
        'file_count': len(files),
        'directory_count': len(directories),
        'is_cross_cutting': is_cross_cutting,
        'is_parameterizable': is_parameterizable,
        'files': files,
        'directories': directories,
    }


def _select_refactoring_technique(
    duplicate: DuplicateBlock,
    context: Dict[str, any]
) -> RefactoringTechnique:
    """
    Select appropriate refactoring technique using decision tree.

    Decision tree logic:
    1. If all instances in same class → extract_method
    2. If instances in related classes → use_inheritance
    3. If cross-cutting concern (error handling, logging) → use_template_method
    4. If instances across modules → extract_function
    5. If similar logic with different values → parameterize_function
    6. If complex pattern → extract_utility
    7. Default → extract_function

    Args:
        duplicate: DuplicateBlock being analyzed
        context: Context dictionary from _analyze_duplicate_context

    Returns:
        RefactoringTechnique enum value
    """
    # Decision tree implementation

    # Rule 1: Same class → extract method
    if context['same_class']:
        return RefactoringTechnique.EXTRACT_CLASS

    # Rule 2: Related classes → use inheritance
    if context['related_classes'] and duplicate.instance_count >= 3:
        return RefactoringTechnique.USE_INHERITANCE

    # Rule 3: Cross-cutting concern → template method pattern
    if context['is_cross_cutting']:
        return RefactoringTechnique.USE_TEMPLATE_METHOD

    # Rule 4: Parameterizable → extract parameterized function
    if context['is_parameterizable']:
        return RefactoringTechnique.PARAMETERIZE_FUNCTION

    # Rule 5: Cross-module → extract function to utility module
    if context['cross_module']:
        return RefactoringTechnique.EXTRACT_UTILITY

    # Rule 6: Multiple files in same directory → extract function
    if not context['same_file'] and context['same_directory']:
        return RefactoringTechnique.EXTRACT_FUNCTION

    # Rule 7: Same file → extract function (local refactoring)
    if context['same_file']:
        return RefactoringTechnique.EXTRACT_FUNCTION

    # Default: Extract function to shared utility
    return RefactoringTechnique.EXTRACT_FUNCTION


def _check_same_class(instances: List[CodeLocation]) -> bool:
    """
    Check if all instances are in the same class.

    Uses heuristics to determine if code blocks are within the same class:
    - Same file
    - Line ranges suggest same class scope (within ~100 lines)

    Args:
        instances: List of CodeLocation objects

    Returns:
        True if instances appear to be in same class
    """
    # Same file is prerequisite
    files = set(loc.file_path for loc in instances)
    if len(files) != 1:
        return False

    # Check if instances are close together (within ~200 lines suggests same class)
    lines = [loc.start_line for loc in instances] + [loc.end_line for loc in instances]
    line_span = max(lines) - min(lines)

    # If within 200 lines, likely same class
    return line_span <= 200


def _check_related_classes(instances: List[CodeLocation]) -> bool:
    """
    Check if instances are in related classes.

    Heuristics:
    - Similar file names (e.g., UserService, OrderService, PaymentService)
    - Same directory
    - Common naming patterns

    Args:
        instances: List of CodeLocation objects

    Returns:
        True if instances appear to be in related classes
    """
    files = [Path(loc.file_path) for loc in instances]

    # Must be in same directory
    directories = set(f.parent for f in files)
    if len(directories) != 1:
        return False

    # Check for similar naming patterns
    file_names = [f.stem for f in files]

    # Common suffixes indicating related classes
    common_suffixes = ['Service', 'Controller', 'Handler', 'Manager', 'Validator', 'Helper']

    for suffix in common_suffixes:
        matching_files = [name for name in file_names if name.endswith(suffix)]
        if len(matching_files) >= 2:
            return True

    return False


def _check_cross_module(instances: List[CodeLocation]) -> bool:
    """
    Check if duplicate instances span multiple modules.

    Determines if duplicates are in different top-level directories,
    suggesting they cross module boundaries.

    Args:
        instances: List of CodeLocation objects

    Returns:
        True if instances are in different modules
    """
    files = [Path(loc.file_path) for loc in instances]

    # Get top-level directories (module roots)
    # Assumes structure like: src/module1/..., src/module2/...
    modules = set()
    for file_path in files:
        parts = file_path.parts
        # Take first 2 parts as module identifier
        if len(parts) >= 2:
            modules.add(parts[:2])
        elif len(parts) >= 1:
            modules.add(parts[:1])

    # Cross-module if more than one unique module
    return len(modules) > 1


def _check_cross_cutting_concern(duplicate: DuplicateBlock) -> bool:
    """
    Check if duplicate represents a cross-cutting concern.

    Cross-cutting concerns include:
    - Error handling (try/except, try/catch)
    - Logging
    - Authentication/authorization checks
    - Input validation
    - Performance monitoring

    Uses pattern matching on code content.

    Args:
        duplicate: DuplicateBlock to analyze

    Returns:
        True if appears to be cross-cutting concern
    """
    code = duplicate.code_sample.lower()

    # Patterns indicating cross-cutting concerns
    cross_cutting_patterns = [
        'try:',
        'except',
        'catch',
        'logger.
```

---

### 🔵 Duplicate #7/8 - PATTERN

**Type:** pattern
**Instances:** 3
**Similarity:** 100.0%
**Hash:** `input-valida...`

**Found in:**
- `/home/artsmc/.claude/skills/code-duplication/scripts/pattern_detector.py:L179-179` (1 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/pattern_detector.py:L235-235` (1 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/pattern_detector.py:L349-349` (1 lines)

**Code Sample:**
```python
if not value: raise ValueError('Invalid')
```

**💡 Refactoring Suggestion:**
- **Technique:** extract_function
- **Difficulty:** easy
- **Estimated LOC Reduction:** 12 lines

**Description:** Create a validation decorator or use a validation library (pydantic, marshmallow)

**Implementation Steps:**
1. Identify all 3 instances of this pattern
2. Extract common logic into a utility function/decorator
3. Replace all instances with the utility call
4. Test thoroughly to ensure behavior is preserved

**Example Refactored Code:**
```python
if not value: raise ValueError('Invalid')
```

---

### 🔵 Duplicate #8/8 - PATTERN

**Type:** pattern
**Instances:** 3
**Similarity:** 100.0%
**Hash:** `list-compreh...`

**Found in:**
- `/home/artsmc/.claude/skills/code-duplication/scripts/suggestion_engine.py:L295-295` (1 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/exact_detector.py:L376-376` (1 lines)
- `/home/artsmc/.claude/skills/code-duplication/scripts/file_discovery.py:L231-234` (4 lines)

**Code Sample:**
```python
[name for name in file_names if name.endswith(suffix)]
```

**💡 Refactoring Suggestion:**
- **Technique:** extract_function
- **Difficulty:** easy
- **Estimated LOC Reduction:** 6 lines

**Description:** Extract complex list comprehensions into named functions for readability

**Implementation Steps:**
1. Identify all 3 instances of this pattern
2. Extract common logic into a utility function/decorator
3. Replace all instances with the utility call
4. Test thoroughly to ensure behavior is preserved

**Example Refactored Code:**
```python
[name for name in file_names if name.endswith(suffix)]
```

---

## 💡 Recommendations

**Potential LOC Reduction:** ~63 lines

### Priority Actions

**🟢 Quick Wins (2 easy tasks):**
- Start with exact duplicates and simple patterns
- Low risk, immediate impact
- Estimated time: 1-2 hours

**🟡 Moderate Refactoring (1 medium tasks):**
- Tackle structural duplicates
- Extract common utilities
- Estimated time: 4-8 hours

### Best Practices Going Forward

1. **Extract Common Utilities:** Create shared functions for repeated logic
2. **Use Design Patterns:** Apply appropriate patterns (Factory, Strategy, Template Method)
3. **Code Reviews:** Flag duplication during reviews
4. **Automated Detection:** Run this analysis regularly (CI/CD integration)
5. **Documentation:** Document shared utilities and patterns

---

*Report generated by Code Duplication Analysis Skill*
