#!/usr/bin/env python3
"""
Suggestion Engine for Code Duplication Analysis Skill

This module generates refactoring suggestions for duplicate code blocks.
It analyzes the context of duplicates (same file, same class, cross-module)
and recommends appropriate refactoring techniques.

Key Features:
- Context-aware suggestion generation
- Decision tree for technique selection
- LOC reduction estimation
- Implementation effort estimation
- Extensible suggestion framework
"""

from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path
from collections import defaultdict

from models import (
    DuplicateBlock,
    RefactoringSuggestion,
    RefactoringTechnique,
    DuplicateType,
    Config,
    CodeLocation
)


def generate_suggestions(
    duplicates: List[DuplicateBlock],
    config: Config
) -> List[DuplicateBlock]:
    """
    Generate refactoring suggestions for duplicate blocks.

    Analyzes each duplicate block's context and determines the most
    appropriate refactoring technique. Updates the duplicate blocks
    with RefactoringSuggestion objects.

    Args:
        duplicates: List of DuplicateBlock objects to analyze
        config: Configuration object with analysis settings

    Returns:
        List of DuplicateBlock objects with suggestions attached
        (returns the same list, modified in place)

    Example:
        >>> duplicates = detect_duplicates(files, config)
        >>> duplicates_with_suggestions = generate_suggestions(duplicates, config)
        >>> coverage = sum(1 for d in duplicates if d.suggestion) / len(duplicates)
        >>> assert coverage >= 0.8  # 80%+ coverage
    """
    # Process each duplicate block
    for duplicate in duplicates:
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
        'logger.',
        'log.',
        'logging.',
        'authenticate',
        'authorize',
        'permission',
        'validate',
        '@decorator',
        'timeit',
        'measure',
        'metric',
    ]

    # Check if code contains cross-cutting patterns
    matches = sum(1 for pattern in cross_cutting_patterns if pattern in code)

    # If 2+ patterns match, likely cross-cutting
    return matches >= 2


def _check_parameterizable(duplicate: DuplicateBlock) -> bool:
    """
    Check if duplicate code could be parameterized.

    Indicators of parameterizable code:
    - Structural duplicates (similar but not exact)
    - Contains literal values (strings, numbers)
    - Similar variable names with different values

    Args:
        duplicate: DuplicateBlock to analyze

    Returns:
        True if code appears parameterizable
    """
    # Structural duplicates are good candidates
    if duplicate.type == DuplicateType.STRUCTURAL:
        return True

    # Check for literal values in code
    code = duplicate.code_sample

    # Count string literals
    string_literals = code.count('"') + code.count("'")

    # Count numeric literals (simple heuristic)
    import re
    numeric_literals = len(re.findall(r'\b\d+\b', code))

    # If code has multiple literals, likely parameterizable
    total_literals = string_literals + numeric_literals

    return total_literals >= 4


def _estimate_loc_reduction(
    duplicate: DuplicateBlock,
    technique: RefactoringTechnique
) -> int:
    """
    Estimate lines of code reduction from refactoring.

    Calculation considers:
    - Current duplicate LOC
    - Overhead of abstraction (extracted function/class)
    - Number of instances

    Formula:
    - Base reduction: (instance_count - 1) * loc_per_instance
    - Overhead: depends on technique (function: ~3 lines, class: ~10 lines)
    - Net reduction: base - overhead

    Args:
        duplicate: DuplicateBlock being refactored
        technique: Refactoring technique to apply

    Returns:
        Estimated LOC reduction (positive number)
    """
    loc_per_instance = duplicate.loc_per_instance
    instance_count = duplicate.instance_count

    # Base reduction: all duplicates except one
    base_reduction = (instance_count - 1) * loc_per_instance

    # Overhead depends on technique
    overhead_map = {
        RefactoringTechnique.EXTRACT_FUNCTION: 3,  # Function definition
        RefactoringTechnique.EXTRACT_CLASS: 10,    # Class definition
        RefactoringTechnique.USE_INHERITANCE: 8,   # Base class setup
        RefactoringTechnique.USE_COMPOSITION: 8,
        RefactoringTechnique.EXTRACT_UTILITY: 5,   # Utility module overhead
        RefactoringTechnique.USE_TEMPLATE_METHOD: 12,  # Template pattern setup
        RefactoringTechnique.PARAMETERIZE_FUNCTION: 5,  # Parameterized function
    }

    overhead = overhead_map.get(technique, 5)

    # Account for call site overhead (1 line per call)
    call_overhead = instance_count * 1

    # Net reduction
    net_reduction = base_reduction - overhead - call_overhead

    # Ensure non-negative
    return max(0, net_reduction)


def _generate_description(
    duplicate: DuplicateBlock,
    technique: RefactoringTechnique,
    context: Dict[str, any]
) -> str:
    """
    Generate human-readable description of refactoring suggestion.

    Args:
        duplicate: DuplicateBlock being refactored
        technique: Selected refactoring technique
        context: Context analysis results

    Returns:
        Description string
    """
    instance_count = duplicate.instance_count
    loc_per_instance = duplicate.loc_per_instance
    file_count = context['file_count']

    # Build description based on technique
    descriptions = {
        RefactoringTechnique.EXTRACT_FUNCTION: (
            f"Extract duplicated logic ({loc_per_instance} lines) into a shared function. "
            f"Found {instance_count} instances across {file_count} file(s)."
        ),
        RefactoringTechnique.EXTRACT_CLASS: (
            f"Extract duplicated logic ({loc_per_instance} lines) into a separate class. "
            f"Found {instance_count} instances in the same class context."
        ),
        RefactoringTechnique.USE_INHERITANCE: (
            f"Create base class with shared logic ({loc_per_instance} lines). "
            f"Found {instance_count} instances across {file_count} related classes."
        ),
        RefactoringTechnique.USE_COMPOSITION: (
            f"Use composition pattern to share logic ({loc_per_instance} lines). "
            f"Found {instance_count} instances across {file_count} classes."
        ),
        RefactoringTechnique.EXTRACT_UTILITY: (
            f"Extract to utility module for cross-module reuse ({loc_per_instance} lines). "
            f"Found {instance_count} instances across {file_count} modules."
        ),
        RefactoringTechnique.USE_TEMPLATE_METHOD: (
            f"Apply template method pattern for cross-cutting concern ({loc_per_instance} lines). "
            f"Found {instance_count} instances with similar structure."
        ),
        RefactoringTechnique.PARAMETERIZE_FUNCTION: (
            f"Extract parameterized function to handle variations ({loc_per_instance} lines). "
            f"Found {instance_count} instances with similar logic but different values."
        ),
    }

    return descriptions.get(
        technique,
        f"Refactor duplicated code ({loc_per_instance} lines) found in {instance_count} locations."
    )


def _generate_implementation_steps(
    duplicate: DuplicateBlock,
    technique: RefactoringTechnique,
    context: Dict[str, any]
) -> List[str]:
    """
    Generate step-by-step implementation guide.

    Args:
        duplicate: DuplicateBlock being refactored
        technique: Selected refactoring technique
        context: Context analysis results

    Returns:
        List of implementation steps
    """
    steps_map = {
        RefactoringTechnique.EXTRACT_FUNCTION: _steps_extract_function,
        RefactoringTechnique.EXTRACT_CLASS: _steps_extract_class,
        RefactoringTechnique.USE_INHERITANCE: _steps_use_inheritance,
        RefactoringTechnique.USE_COMPOSITION: _steps_use_composition,
        RefactoringTechnique.EXTRACT_UTILITY: _steps_extract_utility,
        RefactoringTechnique.USE_TEMPLATE_METHOD: _steps_template_method,
        RefactoringTechnique.PARAMETERIZE_FUNCTION: _steps_parameterize,
    }

    generator = steps_map.get(technique, _steps_default)
    return generator(duplicate, context)


def _steps_extract_function(duplicate: DuplicateBlock, context: Dict[str, any]) -> List[str]:
    """Generate steps for extract function refactoring."""
    target_file = _suggest_target_file(duplicate, context)
    function_name = _suggest_function_name(duplicate)

    return [
        f"1. Create new function '{function_name}' in {target_file}",
        "2. Identify parameters needed (variables used in duplicated code)",
        "3. Move duplicated logic into the new function",
        "4. Add return value if needed",
        f"5. Replace all {duplicate.instance_count} duplicate instances with function calls",
        "6. Run tests to verify behavior unchanged",
        "7. Review and optimize function signature",
    ]


def _steps_extract_class(duplicate: DuplicateBlock, context: Dict[str, any]) -> List[str]:
    """Generate steps for extract class refactoring."""
    class_name = _suggest_class_name(duplicate)

    return [
        f"1. Create new class '{class_name}'",
        "2. Move duplicated logic into class method",
        "3. Identify required instance variables",
        "4. Create constructor to initialize state",
        f"5. Replace all {duplicate.instance_count} duplicate instances with class usage",
        "6. Run tests to verify behavior unchanged",
        "7. Consider additional methods to add to class",
    ]


def _steps_use_inheritance(duplicate: DuplicateBlock, context: Dict[str, any]) -> List[str]:
    """Generate steps for inheritance refactoring."""
    base_class_name = _suggest_base_class_name(duplicate)

    return [
        f"1. Create base class '{base_class_name}'",
        "2. Move shared logic into base class method",
        "3. Identify template method pattern opportunities",
        f"4. Modify {len(context['files'])} classes to inherit from base class",
        "5. Remove duplicated code from subclasses",
        "6. Override methods where needed for specialization",
        "7. Run tests to verify behavior unchanged",
    ]


def _steps_use_composition(duplicate: DuplicateBlock, context: Dict[str, any]) -> List[str]:
    """Generate steps for composition refactoring."""
    return [
        "1. Create helper/utility class with shared logic",
        "2. Add composition relationship to classes needing this functionality",
        "3. Delegate to helper class instead of duplicating code",
        f"4. Update all {duplicate.instance_count} instances to use delegation",
        "5. Run tests to verify behavior unchanged",
    ]


def _steps_extract_utility(duplicate: DuplicateBlock, context: Dict[str, any]) -> List[str]:
    """Generate steps for utility extraction refactoring."""
    module_name = _suggest_utility_module(duplicate, context)
    function_name = _suggest_function_name(duplicate)

    return [
        f"1. Create or update utility module: {module_name}",
        f"2. Add function '{function_name}' with duplicated logic",
        "3. Determine function parameters and return type",
        "4. Add comprehensive docstring and type hints",
        f"5. Replace all {duplicate.instance_count} instances with utility function calls",
        f"6. Add imports to {len(context['files'])} affected files",
        "7. Write unit tests for utility function",
        "8. Run integration tests to verify behavior unchanged",
    ]


def _steps_template_method(duplicate: DuplicateBlock, context: Dict[str, any]) -> List[str]:
    """Generate steps for template method pattern."""
    return [
        "1. Identify invariant and variant parts of duplicated code",
        "2. Create template method with invariant structure",
        "3. Extract variant parts into hook methods",
        "4. Create decorator or base class with template method",
        f"5. Apply pattern to all {duplicate.instance_count} instances",
        "6. Run tests to verify behavior unchanged",
    ]


def _steps_parameterize(duplicate: DuplicateBlock, context: Dict[str, any]) -> List[str]:
    """Generate steps for parameterization refactoring."""
    function_name = _suggest_function_name(duplicate)

    return [
        "1. Identify varying values across duplicate instances",
        "2. Design function signature with parameters for variations",
        f"3. Create parameterized function '{function_name}'",
        "4. Implement logic using parameters instead of hardcoded values",
        f"5. Replace all {duplicate.instance_count} instances with parameterized calls",
        "6. Consider using configuration/data-driven approach",
        "7. Run tests to verify behavior unchanged",
    ]


def _steps_default(duplicate: DuplicateBlock, context: Dict[str, any]) -> List[str]:
    """Generate default steps for refactoring."""
    return [
        "1. Analyze duplicate code to understand its purpose",
        "2. Identify the best refactoring approach for your context",
        "3. Create abstraction (function, class, or utility)",
        f"4. Replace all {duplicate.instance_count} duplicate instances",
        "5. Run tests to verify behavior unchanged",
        "6. Review code for further optimization opportunities",
    ]


def _estimate_difficulty(
    duplicate: DuplicateBlock,
    technique: RefactoringTechnique,
    context: Dict[str, any]
) -> str:
    """
    Estimate refactoring difficulty.

    Factors:
    - Technique complexity
    - Number of instances
    - Number of files affected
    - Code complexity

    Args:
        duplicate: DuplicateBlock being refactored
        technique: Selected refactoring technique
        context: Context analysis results

    Returns:
        Difficulty level: "easy", "medium", or "hard"
    """
    # Base difficulty by technique
    technique_difficulty = {
        RefactoringTechnique.EXTRACT_FUNCTION: 1,
        RefactoringTechnique.PARAMETERIZE_FUNCTION: 2,
        RefactoringTechnique.EXTRACT_UTILITY: 2,
        RefactoringTechnique.EXTRACT_CLASS: 3,
        RefactoringTechnique.USE_COMPOSITION: 3,
        RefactoringTechnique.USE_INHERITANCE: 4,
        RefactoringTechnique.USE_TEMPLATE_METHOD: 4,
    }

    base_difficulty = technique_difficulty.get(technique, 2)

    # Adjust for instance count (more instances = harder)
    if duplicate.instance_count > 10:
        base_difficulty += 1
    elif duplicate.instance_count > 5:
        base_difficulty += 0.5

    # Adjust for file count (cross-file = harder)
    if context['file_count'] > 5:
        base_difficulty += 1
    elif context['file_count'] > 2:
        base_difficulty += 0.5

    # Adjust for code size (longer = harder)
    if duplicate.loc_per_instance > 50:
        base_difficulty += 1
    elif duplicate.loc_per_instance > 20:
        base_difficulty += 0.5

    # Map to difficulty levels
    if base_difficulty <= 2:
        return "easy"
    elif base_difficulty <= 4:
        return "medium"
    else:
        return "hard"


def _suggest_target_file(duplicate: DuplicateBlock, context: Dict[str, any]) -> str:
    """
    Suggest target file for extracted code.

    Args:
        duplicate: DuplicateBlock being refactored
        context: Context analysis results

    Returns:
        Suggested file path
    """
    if context['same_file']:
        # Stay in same file
        return duplicate.instances[0].file_path
    elif context['same_directory']:
        # Create shared module in same directory
        directory = str(Path(duplicate.instances[0].file_path).parent)
        return f"{directory}/shared_utils.py"
    else:
        # Create in utils or common module
        return "src/utils/common.py"


def _suggest_function_name(duplicate: DuplicateBlock) -> str:
    """
    Suggest function name based on code content.

    Simple heuristic: extract keywords from code.

    Args:
        duplicate: DuplicateBlock to analyze

    Returns:
        Suggested function name
    """
    # This is a simplified heuristic
    # In real implementation, could use NLP or more sophisticated analysis
    code = duplicate.code_sample.lower()

    # Common operation keywords
    if 'validate' in code:
        return "validate_input"
    elif 'calculate' in code or 'compute' in code:
        return "calculate_total"
    elif 'format' in code:
        return "format_output"
    elif 'parse' in code:
        return "parse_data"
    elif 'fetch' in code or 'get' in code:
        return "fetch_data"
    elif 'save' in code or 'store' in code:
        return "save_data"
    else:
        return "extracted_function"


def _suggest_class_name(duplicate: DuplicateBlock) -> str:
    """Suggest class name for extracted class."""
    function_name = _suggest_function_name(duplicate)
    # Convert function name to class name
    return ''.join(word.capitalize() for word in function_name.split('_'))


def _suggest_base_class_name(duplicate: DuplicateBlock) -> str:
    """Suggest base class name for inheritance."""
    class_name = _suggest_class_name(duplicate)
    return f"Base{class_name}"


def _suggest_utility_module(duplicate: DuplicateBlock, context: Dict[str, any]) -> str:
    """Suggest utility module name."""
    if context['cross_module']:
        return "src/common/utils.py"
    else:
        directory = str(Path(duplicate.instances[0].file_path).parent)
        return f"{directory}/utils.py"


def _create_fallback_suggestion(duplicate: DuplicateBlock) -> RefactoringSuggestion:
    """
    Create fallback suggestion when automatic analysis fails.

    Args:
        duplicate: DuplicateBlock that failed analysis

    Returns:
        Generic RefactoringSuggestion
    """
    return RefactoringSuggestion(
        technique=RefactoringTechnique.EXTRACT_FUNCTION,
        description=(
            f"Refactor duplicated code ({duplicate.loc_per_instance} lines) "
            f"found in {duplicate.instance_count} locations. "
            "Manual review recommended to determine best approach."
        ),
        estimated_loc_reduction=duplicate.potential_loc_reduction,
        implementation_steps=[
            "1. Review duplicated code to understand its purpose",
            "2. Determine appropriate refactoring technique",
            "3. Create abstraction (function, class, or module)",
            f"4. Replace {duplicate.instance_count} duplicate instances",
            "5. Test thoroughly to ensure behavior is preserved",
        ],
        difficulty="medium"
    )


# Export public API
__all__ = [
    "generate_suggestions",
]
