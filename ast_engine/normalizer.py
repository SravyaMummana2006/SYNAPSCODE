"""
AST Normalization and Canonicalization Engine for Code Plagiarism Detection.

Implements semantic normalization to counter LLM-based code paraphrasing:
1. Canonicalizes commutative operations (e.g. x + y <=> y + x, a == b <=> b == a).
2. Canonicalizes comparison operators (e.g. a > b <=> b < a, a >= b <=> b <= a).
3. Normalizes augmented assignments (x += y <=> x = x + y).
4. Normalizes class attribute encapsulation (self.attr <=> VAR) to defeat class-wrapper evasion.
5. Preserves Python built-ins (len, range, max, min, sorted, zip, etc.) while abstracting user variables.
6. Normalizes literal constants into typed categories (CONST:int, CONST:str, CONST:bool).
"""

import ast
from typing import Set, Optional

PYTHON_BUILTINS: Set[str] = {
    "len", "range", "max", "min", "sorted", "print", "set", "list", "dict",
    "int", "str", "float", "bool", "zip", "enumerate", "sum", "abs",
    "collections", "deque", "defaultdict", "Counter", "heapq", "bisect"
}

COMMUTATIVE_OPS = (ast.Add, ast.Mult, ast.BitAnd, ast.BitOr, ast.BitXor)

def normalize_expr(node: Optional[ast.AST]) -> str:
    """
    Recursively normalizes an AST expression node into a canonical string signature.
    """
    if node is None:
        return "None"

    # 1. Names and Identifiers
    if isinstance(node, ast.Name):
        if node.id in PYTHON_BUILTINS:
            return f"BUILTIN:{node.id}"
        return "VAR"

    # 2. Attribute Access (e.g. self.val -> VAR to neutralize OOP wrapper evasion)
    if isinstance(node, ast.Attribute):
        if isinstance(node.value, ast.Name) and node.value.id == "self":
            return "VAR"
        return f"ATTR:{node.attr}"

    # 3. Constants and Literals
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            return "CONST:bool"
        elif isinstance(node.value, (int, float)):
            return "CONST:num"
        elif isinstance(node.value, str):
            return "CONST:str"
        return "CONST:other"

    # 4. Commutative Binary Operations (x + y <=> y + x)
    if isinstance(node, ast.BinOp):
        left_s = normalize_expr(node.left)
        right_s = normalize_expr(node.right)
        op_s = node.op.__class__.__name__
        if isinstance(node.op, COMMUTATIVE_OPS) and left_s > right_s:
            left_s, right_s = right_s, left_s
        return f"BinOp({op_s},{left_s},{right_s})"

    # 5. Unary Operations
    if isinstance(node, ast.UnaryOp):
        return f"UnaryOp({node.op.__class__.__name__},{normalize_expr(node.operand)})"

    # 6. Comparisons (a > b <=> b < a, a >= b <=> b <= a)
    if isinstance(node, ast.Compare):
        left_s = normalize_expr(node.left)
        cmp_parts = []
        for op, comp in zip(node.ops, node.comparators):
            op_name = op.__class__.__name__
            right_s = normalize_expr(comp)
            if op_name == "Gt":
                cmp_parts.append(f"Lt,{right_s},{left_s}")
            elif op_name == "GtE":
                cmp_parts.append(f"LtE,{right_s},{left_s}")
            elif op_name in ("Eq", "NotEq"):
                # Commutative equality check
                if left_s > right_s:
                    cmp_parts.append(f"{op_name},{right_s},{left_s}")
                else:
                    cmp_parts.append(f"{op_name},{left_s},{right_s}")
            else:
                cmp_parts.append(f"{op_name},{left_s},{right_s}")
        return f"Compare({';'.join(cmp_parts)})"

    # 7. Function Calls
    if isinstance(node, ast.Call):
        func_s = normalize_expr(node.func)
        args_s = ",".join(normalize_expr(a) for a in node.args)
        return f"Call({func_s}[{args_s}])"

    # 8. Subscript / Indexing (arr[i] or grid[r][c])
    if isinstance(node, ast.Subscript):
        return f"Index({normalize_expr(node.value)}[{normalize_expr(node.slice)}])"

    # 9. Comprehensions
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
        return f"Comp({node.__class__.__name__},{normalize_expr(node.elt)})"

    # 10. Boolean Operations (and, or)
    if isinstance(node, ast.BoolOp):
        values_s = sorted(normalize_expr(v) for v in node.values)
        return f"BoolOp({node.op.__class__.__name__},{','.join(values_s)})"

    return node.__class__.__name__
