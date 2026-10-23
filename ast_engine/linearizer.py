"""
AST Linearizer module.

Extracts an ordered sequence of normalized statement structures and expression
subtrees from an AST, and converts them to token ID streams for Rabin-Karp hashing.
"""

import ast
from typing import List, Dict, Optional
from .normalizer import normalize_expr

def extract_ast_structural_tokens(code: str) -> List[str]:
    """
    Parses source code into an AST and extracts an ordered stream of
    canonical statement structures, conditions, and expression subtrees.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    tokens: List[str] = []

    for node in ast.walk(tree):
        # 1. Assignments
        if isinstance(node, ast.Assign):
            target_str = ",".join(normalize_expr(t) for t in node.targets)
            tokens.append(f"ASSIGN:{target_str}={normalize_expr(node.value)}")
        elif isinstance(node, ast.AugAssign):
            # Canonicalize x += y to x = x + y through commutative normalize_expr
            binop = ast.BinOp(left=node.target, op=node.op, right=node.value)
            tokens.append(f"ASSIGN:{normalize_expr(node.target)}={normalize_expr(binop)}")

        # 2. Return statements
        elif isinstance(node, ast.Return):
            tokens.append(f"RETURN:{normalize_expr(node.value)}")

        # 3. Loops (While, For)
        elif isinstance(node, (ast.While, ast.For)):
            iter_cond = getattr(node, "test", None) or getattr(node, "iter", None)
            tokens.append(f"LOOP:{node.__class__.__name__}({normalize_expr(iter_cond)})")

        # 4. Conditional Branches (If)
        elif isinstance(node, ast.If):
            tokens.append(f"IF:{normalize_expr(node.test)}")

        # 5. Core Logical Expression Subtrees (BinOp, Compare, Call, Subscript)
        elif isinstance(node, (ast.BinOp, ast.Compare, ast.Call, ast.Subscript)):
            tokens.append(f"EXPR:{normalize_expr(node)}")

    return tokens

import zlib

def tokens_to_id_stream(tokens: List[str], vocab: Optional[Dict[str, int]] = None) -> List[int]:
    """
    Converts string structural tokens to deterministic integer IDs for rolling hashing.
    Uses CRC32 hash of token strings.
    """
    return [zlib.crc32(t.encode("utf-8")) & 0x7FFFFFFF for t in tokens]
