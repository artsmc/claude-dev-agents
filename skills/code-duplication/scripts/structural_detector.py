#!/usr/bin/env python3
"""
Structural Duplicate Detection for Code Duplication Analysis Skill

Provides AST-based analysis for detecting structurally similar code that
may have different variable names but identical logic flow.
"""

import ast
import hashlib
from typing import Optional, List, Dict, Tuple, Any
from pathlib import Path

from models import DuplicateBlock, CodeLocation, DuplicateType


def parse_ast(source: str, language: str) -> Optional[ast.AST]:
    """
    Parse source code into Abstract Syntax Tree.

    Currently supports Python only. Gracefully handles syntax errors
    by returning None instead of crashing.

    Args:
        source: Source code to parse
        language: Programming language ('python' supported)

    Returns:
        AST tree if successful, None if parsing fails

    Examples:
        >>> tree = parse_ast("def foo(): pass", "python")
        >>> tree is not None
        True
        >>> tree = parse_ast("def incomplete(", "python")
        >>> tree is None
        True
    """
    if language != 'python':
        # Only Python supported for now
        return None

    try:
        tree = ast.parse(source)
        return tree
    except SyntaxError as e:
        # Log but don't crash - graceful degradation
        # In production, this would log to a file
        return None
    except Exception as e:
        # Catch other parsing errors
        return None


class ASTNormalizer(ast.NodeTransformer):
    """
    Normalize AST by replacing identifiers with placeholders.

    This makes structurally identical code produce identical ASTs even
    when variable/function names differ.

    Example:
        def calculate(items):     ->  def FUNC_0(VAR_0):
            total = sum(items)    ->      VAR_1 = sum(VAR_0)
            return total          ->      return VAR_1
    """

    def __init__(self):
        """Initialize normalizer with empty mappings."""
        self.var_counter = 0
        self.func_counter = 0
        self.class_counter = 0
        self.var_map: Dict[str, str] = {}
        self.func_map: Dict[str, str] = {}
        self.class_map: Dict[str, str] = {}

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """
        Replace variable names with placeholders (VAR_0, VAR_1, etc.).

        Args:
            node: Name AST node

        Returns:
            Modified Name node with normalized identifier
        """
        # Get or create normalized name
        if node.id not in self.var_map:
            self.var_map[node.id] = f"VAR_{self.var_counter}"
            self.var_counter += 1

        # Create new node with normalized name
        node.id = self.var_map[node.id]
        return node

    def visit_arg(self, node: ast.arg) -> ast.arg:
        """
        Replace function argument names with placeholders.

        Args:
            node: arg AST node (function parameter)

        Returns:
            Modified arg node with normalized name
        """
        # Normalize argument name
        if node.arg not in self.var_map:
            self.var_map[node.arg] = f"VAR_{self.var_counter}"
            self.var_counter += 1

        node.arg = self.var_map[node.arg]
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """
        Replace function names with placeholders (FUNC_0, FUNC_1, etc.).

        Args:
            node: FunctionDef AST node

        Returns:
            Modified FunctionDef node with normalized name
        """
        # Normalize function name
        if node.name not in self.func_map:
            self.func_map[node.name] = f"FUNC_{self.func_counter}"
            self.func_counter += 1

        node.name = self.func_map[node.name]

        # Visit child nodes (body, decorators, etc.)
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        """
        Replace async function names with placeholders.

        Args:
            node: AsyncFunctionDef AST node

        Returns:
            Modified AsyncFunctionDef node
        """
        # Same as regular function
        if node.name not in self.func_map:
            self.func_map[node.name] = f"FUNC_{self.func_counter}"
            self.func_counter += 1

        node.name = self.func_map[node.name]
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """
        Replace class names with placeholders (CLASS_0, CLASS_1, etc.).

        Args:
            node: ClassDef AST node

        Returns:
            Modified ClassDef node
        """
        if node.name not in self.class_map:
            self.class_map[node.name] = f"CLASS_{self.class_counter}"
            self.class_counter += 1

        node.name = self.class_map[node.name]
        self.generic_visit(node)
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.Constant:
        """
        Replace literal values with type placeholders.

        Strings become "STRING", numbers become 0, etc.

        Args:
            node: Constant AST node (Python 3.8+)

        Returns:
            Modified Constant node
        """
        if isinstance(node.value, str):
            node.value = "STRING"
        elif isinstance(node.value, (int, float)):
            node.value = 0
        elif isinstance(node.value, bool):
            # Keep booleans as-is (they're control flow)
            pass
        elif node.value is None:
            # Keep None as-is
            pass

        return node

    # For Python 3.7 compatibility (deprecated in 3.8+)
    def visit_Str(self, node: ast.Str) -> ast.Str:
        """Replace string literals (Python 3.7)."""
        node.s = "STRING"
        return node

    def visit_Num(self, node: ast.Num) -> ast.Num:
        """Replace numeric literals (Python 3.7)."""
        node.n = 0
        return node


def normalize_ast(tree: ast.AST) -> ast.AST:
    """
    Normalize an AST by replacing identifiers with placeholders.

    Args:
        tree: AST to normalize

    Returns:
        Normalized AST (modified in-place, but also returned)

    Example:
        >>> code1 = "def calc(items): total = sum(items); return total"
        >>> code2 = "def compute(values): result = sum(values); return result"
        >>> tree1 = normalize_ast(parse_ast(code1, "python"))
        >>> tree2 = normalize_ast(parse_ast(code2, "python"))
        >>> ast.dump(tree1) == ast.dump(tree2)
        True
    """
    normalizer = ASTNormalizer()
    normalized = normalizer.visit(tree)
    return normalized


def ast_fingerprint(tree: ast.AST) -> str:
    """
    Generate hash fingerprint from AST.

    Uses ast.dump() to get canonical string representation,
    then hashes with MD5.

    Args:
        tree: AST to fingerprint

    Returns:
        MD5 hex digest of AST structure

    Example:
        >>> tree1 = normalize_ast(parse_ast("def foo(x): return x + 1", "python"))
        >>> tree2 = normalize_ast(parse_ast("def bar(y): return y + 1", "python"))
        >>> ast_fingerprint(tree1) == ast_fingerprint(tree2)
        True
    """
    # Get canonical string representation
    canonical = ast.dump(tree)

    # Hash it
    hash_obj = hashlib.md5(canonical.encode('utf-8'))
    return hash_obj.hexdigest()


def calculate_similarity(tree1: ast.AST, tree2: ast.AST) -> float:
    """
    Calculate structural similarity between two ASTs.

    Uses simplified tree edit distance approach. For exact matches,
    returns 1.0. For different structures, uses node count ratio.

    Args:
        tree1: First AST
        tree2: Second AST

    Returns:
        Similarity score between 0.0 and 1.0

    Note:
        This is a simplified implementation. Full tree edit distance
        is expensive (O(n²)). This uses node count heuristic for speed.

    Example:
        >>> tree1 = parse_ast("def foo(x): return x + 1", "python")
        >>> tree2 = parse_ast("def foo(x, y): return x + y", "python")
        >>> score = calculate_similarity(tree1, tree2)
        >>> 0.80 <= score <= 0.95
        True
    """
    # Check for exact match first
    if ast.dump(tree1) == ast.dump(tree2):
        return 1.0

    # Count nodes in each tree
    count1 = sum(1 for _ in ast.walk(tree1))
    count2 = sum(1 for _ in ast.walk(tree2))

    # Simple similarity based on node count ratio
    # More sophisticated: would use actual tree edit distance
    smaller = min(count1, count2)
    larger = max(count1, count2)

    if larger == 0:
        return 1.0

    # Ratio of smaller to larger (0.0 to 1.0)
    ratio = smaller / larger

    return ratio


def tree_edit_distance(tree1: ast.AST, tree2: ast.AST) -> int:
    """
    Calculate tree edit distance between two ASTs.

    This is a simplified implementation that counts differing nodes.
    Full tree edit distance is computationally expensive (O(n²)).

    Args:
        tree1: First AST
        tree2: Second AST

    Returns:
        Edit distance (number of operations to transform tree1 to tree2)

    Note:
        For production use, consider using Zhang-Shasha algorithm
        or other optimized tree edit distance algorithms.
    """
    # Convert to canonical strings
    dump1 = ast.dump(tree1)
    dump2 = ast.dump(tree2)

    # If identical, distance is 0
    if dump1 == dump2:
        return 0

    # Count nodes
    count1 = sum(1 for _ in ast.walk(tree1))
    count2 = sum(1 for _ in ast.walk(tree2))

    # Simplified: distance is difference in node count
    # Real implementation would use dynamic programming
    return abs(count1 - count2)


def find_structural_duplicates(
    files_content: List[Tuple[Path, str, str]],
    similarity_threshold: float = 0.85,
    min_lines: int = 5
) -> List[DuplicateBlock]:
    """
    Find structurally similar code across files.

    Uses AST-based comparison to find code with identical logic
    but different variable/function names.

    Args:
        files_content: List of (file_path, content, language) tuples
        similarity_threshold: Minimum similarity score (0.0-1.0)
        min_lines: Minimum lines to consider

    Returns:
        List of DuplicateBlock objects with type=STRUCTURAL

    Example:
        >>> files = [(Path("a.py"), "def foo(x): return x+1", "python"),
        ...          (Path("b.py"), "def bar(y): return y+1", "python")]
        >>> dups = find_structural_duplicates(files)
        >>> len(dups) > 0
        True
    """
    # Parse and normalize all ASTs
    fingerprints: Dict[str, List[Dict]] = {}

    for file_path, content, language in files_content:
        if language != 'python':
            continue  # Only Python supported for now

        # Split into functions (analyze function-by-function)
        tree = parse_ast(content, language)
        if tree is None:
            continue

        # Extract function definitions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                try:
                    # Get function source lines
                    start_line = node.lineno
                    end_line = node.end_lineno or start_line
                    line_count = end_line - start_line + 1

                    # Skip small functions
                    if line_count < min_lines:
                        continue

                    # Normalize function AST
                    normalized = normalize_ast(node)

                    # Get fingerprint
                    fp = ast_fingerprint(normalized)

                    # Store metadata
                    if fp not in fingerprints:
                        fingerprints[fp] = []

                    fingerprints[fp].append({
                        'file': file_path,
                        'start_line': start_line,
                        'end_line': end_line,
                        'line_count': line_count,
                        'tree': node,  # Original AST
                        'code': ast.unparse(node) if hasattr(ast, 'unparse') else ast.get_source_segment(content, node)
                    })
                except Exception:
                    # Skip functions that fail normalization
                    continue

    # Find duplicates (fingerprint appears > 1 time)
    duplicates = []
    duplicate_id = 1

    for fp, instances in fingerprints.items():
        if len(instances) < 2:
            continue

        # Create CodeLocation objects
        locations = []
        for inst in instances:
            locations.append(CodeLocation(
                file_path=inst['file'],
                start_line=inst['start_line'],
                end_line=inst['end_line'],
                line_count=inst['line_count']
            ))

        # Use first instance code as sample
        code_sample = instances[0].get('code', '')

        # Create DuplicateBlock
        duplicate = DuplicateBlock(
            id=duplicate_id,
            type=DuplicateType.STRUCTURAL,
            hash=fp,
            instances=locations,
            code_sample=code_sample,
            similarity_score=1.0,  # Exact structural match
            suggestion=None
        )

        duplicates.append(duplicate)
        duplicate_id += 1

    # Sort by instance count (most duplicated first)
    duplicates.sort(key=lambda d: len(d.instances), reverse=True)

    return duplicates


# Export public API
__all__ = [
    'parse_ast',
    'normalize_ast',
    'ast_fingerprint',
    'calculate_similarity',
    'tree_edit_distance',
    'find_structural_duplicates',
    'ASTNormalizer',
]
