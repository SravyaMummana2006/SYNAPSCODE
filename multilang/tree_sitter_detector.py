"""
Multi-Language AST Plagiarism Detector powered by Tree-Sitter.
Supports language-agnostic AST parsing for C++, Python, and other languages.
Extracts canonicalized structural nodes and applies Rabin-Karp Winnowing.
"""

import os
import sys
import time
from typing import List, Set, Tuple
import tree_sitter
import tree_sitter_cpp
import tree_sitter_python

# Import Rabin-Karp and Winnowing from baseline
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from baseline.rabin_karp import compute_rolling_hashes
from baseline.winnowing import winnow, Fingerprint
from baseline.detector import SimilarityResult
from ast_engine.linearizer import tokens_to_id_stream

LANGUAGES = {
    "cpp": tree_sitter.Language(tree_sitter_cpp.language()),
    "python": tree_sitter.Language(tree_sitter_python.language()),
}

COMMUTATIVE_OPERATORS = {"+", "*", "&", "|", "^", "==", "!="}

class TreeSitterDetector:
    """
    Multi-language AST Plagiarism Detector using Tree-Sitter grammars.
    """

    def __init__(self, lang: str = "cpp", k: int = 1, w: int = 2):
        if lang not in LANGUAGES:
            raise ValueError(f"Unsupported language: {lang}. Supported: {list(LANGUAGES.keys())}")
        self.lang_name = lang
        self.language = LANGUAGES[lang]
        self.parser = tree_sitter.Parser(self.language)
        self.k = k
        self.w = w

    def _normalize_node(self, node: tree_sitter.Node, source_bytes: bytes) -> str:
        ntype = node.type

        # 1. Identifier abstraction
        if ntype in ("identifier", "field_identifier", "type_identifier"):
            name = source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="ignore")
            # Common standard library names preserved
            if name in ("std", "vector", "string", "cout", "cin", "max", "min", "sort", "len", "range"):
                return f"LIB:{name}"
            return "VAR"

        # 2. Number / Literal abstraction
        if ntype in ("number_literal", "integer", "float", "string_literal", "char_literal"):
            return f"LIT:{ntype}"

        # 3. Binary Expressions: Canonicalize Commutative Operations
        if ntype == "binary_expression":
            left_child = None
            op_text = ""
            right_child = None
            for child in node.children:
                if child.type in ("+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=", "&&", "||", "&", "|", "^"):
                    op_text = child.type
                elif left_child is None:
                    left_child = child
                else:
                    right_child = child

            if left_child and right_child:
                left_s = self._normalize_node(left_child, source_bytes)
                right_s = self._normalize_node(right_child, source_bytes)
                # Commutative ordering
                if op_text in COMMUTATIVE_OPERATORS and left_s > right_s:
                    left_s, right_s = right_s, left_s
                # Relational inversion
                if op_text == ">":
                    return f"BinOp(Lt,{right_s},{left_s})"
                elif op_text == ">=":
                    return f"BinOp(LtE,{right_s},{left_s})"
                return f"BinOp({op_text},{left_s},{right_s})"

        # Default fallback: node type with children signatures
        child_sigs = [
            self._normalize_node(c, source_bytes)
            for c in node.children
            if c.type not in ("{", "}", "(", ")", ";", ",", "comment")
        ]
        return f"{ntype}({','.join(child_sigs)})"

    def extract_structural_tokens(self, source_code: str) -> List[str]:
        source_bytes = source_code.encode("utf-8")
        tree = self.parser.parse(source_bytes)
        tokens: List[str] = []

        def traverse(node: tree_sitter.Node):
            # Target substantial statement / control-flow / expression nodes
            if node.type in (
                "function_definition", "assignment_expression", "if_statement",
                "while_statement", "for_statement", "for_range_loop",
                "return_statement", "binary_expression", "call_expression",
                "subscript_expression"
            ):
                sig = self._normalize_node(node, source_bytes)
                tokens.append(f"TS_{node.type}:{sig}")

            for child in node.children:
                traverse(child)

        traverse(tree.root_node)
        return tokens

    def extract_fingerprints(self, source_code: str) -> Tuple[List[Fingerprint], List[str]]:
        tokens = self.extract_structural_tokens(source_code)
        int_stream = tokens_to_id_stream(tokens)
        rolling_hashes = compute_rolling_hashes(int_stream, self.k)
        fingerprints = winnow(rolling_hashes, self.w)
        return fingerprints, tokens

    def compare_codes(self, code_a: str, code_b: str) -> SimilarityResult:
        start_time = time.perf_counter()

        fp_a, _ = self.extract_fingerprints(code_a)
        fp_b, _ = self.extract_fingerprints(code_b)

        hashes_a: Set[int] = {fp.hash_value for fp in fp_a}
        hashes_b: Set[int] = {fp.hash_value for fp in fp_b}

        intersection = hashes_a.intersection(hashes_b)
        union = hashes_a.union(hashes_b)

        len_inter = len(intersection)
        len_union = len(union)
        len_a = len(hashes_a)
        len_b = len(hashes_b)

        jaccard = (len_inter / len_union) if len_union > 0 else 0.0
        dice = (2.0 * len_inter / (len_a + len_b)) if (len_a + len_b) > 0 else 0.0
        containment_a = (len_inter / len_a) if len_a > 0 else 0.0
        containment_b = (len_inter / len_b) if len_b > 0 else 0.0

        elapsed = time.perf_counter() - start_time

        return SimilarityResult(
            jaccard=jaccard,
            dice=dice,
            containment_a=containment_a,
            containment_b=containment_b,
            shared_fingerprints_count=len_inter,
            total_fingerprints_a=len_a,
            total_fingerprints_b=len_b,
            execution_time_sec=elapsed
        )

    def compare_files(self, file_a_path: str, file_b_path: str) -> SimilarityResult:
        with open(file_a_path, "r", encoding="utf-8") as fa:
            code_a = fa.read()
        with open(file_b_path, "r", encoding="utf-8") as fb:
            code_b = fb.read()
        return self.compare_codes(code_a, code_b)
