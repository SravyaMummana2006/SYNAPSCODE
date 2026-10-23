"""
Lexical tokenization and normalization module for Python source code.
Implements the MOSS/JPlag standard token abstraction:
- Eliminates formatting, comments, and docstrings.
- Maps language keywords and operators to canonical tokens.
- Abstracts user-defined identifiers (variables, functions, attributes) to a generic 'ID' token.
- Abstracts literal values (integers, floats, strings) to 'LIT'.
- Retains source code line/column metadata for match localization.
"""

import tokenize
import io
import token as token_module
from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class CodeToken:
    type_str: str          # e.g., 'KW_WHILE', 'ID', 'OP_ADD', 'LIT'
    raw_val: str           # Original text from source code
    start_line: int
    start_col: int
    end_line: int
    end_col: int

    def __repr__(self):
        return f"{self.type_str}@{self.start_line}:{self.start_col}"

PYTHON_KEYWORDS = {
    "def", "return", "if", "elif", "else", "while", "for", "in", "break",
    "continue", "pass", "yield", "class", "try", "except", "finally",
    "raise", "import", "from", "as", "is", "not", "and", "or", "lambda",
    "with", "global", "nonlocal", "assert", "del", "async", "await"
}

OPERATOR_MAP = {
    "+": "OP_ADD", "-": "OP_SUB", "*": "OP_MUL", "/": "OP_DIV",
    "//": "OP_FLOORDIV", "%": "OP_MOD", "**": "OP_POW",
    "==": "OP_EQ", "!=": "OP_NEQ", "<": "OP_LT", "<=": "OP_LTE",
    ">": "OP_GT", ">=": "OP_GTE", "=": "OP_ASSIGN",
    "+=": "OP_ADD_ASSIGN", "-=": "OP_SUB_ASSIGN", "*=": "OP_MUL_ASSIGN",
    "/=": "OP_DIV_ASSIGN", "//=": "OP_FLOORDIV_ASSIGN", "%=": "OP_MOD_ASSIGN",
    "&": "OP_BITAND", "|": "OP_BITOR", "^": "OP_BITXOR", "~": "OP_BITNOT",
    ">>": "OP_RSHIFT", "<<": "OP_LSHIFT",
    "(": "LPAREN", ")": "RPAREN", "[": "LBRACKET", "]": "RBRACKET",
    "{": "LBRACE", "}": "RBRACE", ",": "COMMA", ":": "COLON",
    ".": "DOT", ";": "SEMICOLON", "->": "ARROW"
}

import ast

def _get_docstring_spans(source_code: str):
    """Returns a set of (start_line, start_col, end_line, end_col) spans for docstrings."""
    spans = set()
    try:
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                ):
                    doc_node = node.body[0].value
                    spans.add((doc_node.lineno, doc_node.col_offset))
    except Exception:
        pass
    return spans

def tokenize_code(source_code: str, abstract_identifiers: bool = True, abstract_literals: bool = True) -> List[CodeToken]:
    """
    Tokenizes Python source code into a normalized token sequence.
    
    Args:
        source_code: Raw source code string.
        abstract_identifiers: If True, replace user identifiers with 'ID' (MOSS-style).
        abstract_literals: If True, replace numbers and strings with 'LIT'.
        
    Returns:
        List of CodeToken instances.
    """
    tokens: List[CodeToken] = []
    stream = io.StringIO(source_code)
    docstring_starts = _get_docstring_spans(source_code)

    try:
        token_gen = tokenize.generate_tokens(stream.readline)

        for tok_type, tok_string, (sline, scol), (eline, ecol), _ in token_gen:
            # 1. Strip comments and formatting/whitespace tokens
            if tok_type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, 
                            tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING, tokenize.ENDMARKER):
                continue

            # 2. Filter docstrings
            if tok_type == tokenize.STRING:
                if (sline, scol) in docstring_starts:
                    continue
                clean_str = tok_string.strip()
                if clean_str.startswith('"""') or clean_str.startswith("'''"):
                    continue

                token_str = "LIT" if abstract_literals else f"STR:{clean_str}"
                tokens.append(CodeToken(token_str, tok_string, sline, scol, eline, ecol))
                continue

            # 3. Numeric Literals
            if tok_type == tokenize.NUMBER:
                token_str = "LIT" if abstract_literals else f"NUM:{tok_string}"
                tokens.append(CodeToken(token_str, tok_string, sline, scol, eline, ecol))
                prev_tok_type = tok_type
                continue

            # 4. Names / Identifiers / Keywords
            if tok_type == tokenize.NAME:
                if tok_string in PYTHON_KEYWORDS:
                    token_str = f"KW_{tok_string.upper()}"
                elif tok_string in ("True", "False", "None"):
                    token_str = f"CONST_{tok_string.upper()}"
                else:
                    token_str = "ID" if abstract_identifiers else f"ID_{tok_string}"
                tokens.append(CodeToken(token_str, tok_string, sline, scol, eline, ecol))
                prev_tok_type = tok_type
                continue

            # 5. Operators and Delimiters
            if tok_type == tokenize.OP:
                op_name = OPERATOR_MAP.get(tok_string, f"OP_{tok_string}")
                tokens.append(CodeToken(op_name, tok_string, sline, scol, eline, ecol))
                prev_tok_type = tok_type
                continue

            # Fallback for other token types
            tokens.append(CodeToken(f"TOK_{tok_string}", tok_string, sline, scol, eline, ecol))
            prev_tok_type = tok_type

    except (tokenize.TokenError, IndentationError):
        # Fallback for malformed source (should not occur in clean benchmark)
        pass

    return tokens

import zlib

def tokens_to_stream(tokens: List[CodeToken]) -> List[int]:
    """
    Maps list of CodeToken instances to a deterministic integer sequence for rolling hashing.
    Uses CRC32 hash of token types to ensure consistent mapping across files.
    """
    return [zlib.crc32(t.type_str.encode("utf-8")) & 0x7FFFFFFF for t in tokens]
