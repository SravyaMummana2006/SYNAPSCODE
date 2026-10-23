"""
Unit Test Suite for Step 3: Improved AST-Normalized Engine.
Verifies:
1. Commutative operation canonicalization (e.g., x + y <=> y + x).
2. Comparison canonicalization (e.g., a > b <=> b < a, a >= b <=> b <= a).
3. Augmented assignment normalization (x += y <=> x = x + y).
4. Structural token extraction and variable abstraction.
5. End-to-end AST Winnowing properties (identity, symmetry, runtime tracking).
"""

import os
import sys
import unittest
import ast

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from ast_engine.normalizer import normalize_expr
from ast_engine.linearizer import extract_ast_structural_tokens, tokens_to_id_stream
from ast_engine.detector import ASTWinnowingDetector

class TestASTNormalizer(unittest.TestCase):
    def test_commutative_canonicalization(self):
        """Verify commutative binary operations normalize to the exact same string."""
        code1 = ast.parse("x = a + b").body[0].value
        code2 = ast.parse("x = b + a").body[0].value
        self.assertEqual(normalize_expr(code1), normalize_expr(code2))

    def test_comparison_canonicalization(self):
        """Verify inverted comparison operators normalize to equivalent canonical forms."""
        code1 = ast.parse("if a > b: pass").body[0].test
        code2 = ast.parse("if b < a: pass").body[0].test
        self.assertEqual(normalize_expr(code1), normalize_expr(code2))

    def test_equality_canonicalization(self):
        """Verify commutative equality comparisons normalize identically."""
        code1 = ast.parse("if a == b: pass").body[0].test
        code2 = ast.parse("if b == a: pass").body[0].test
        self.assertEqual(normalize_expr(code1), normalize_expr(code2))

    def test_augmented_assign_normalization(self):
        """Verify x += 1 produces equivalent structural assign tokens as x = x + 1."""
        code1 = "count += 1"
        code2 = "count = count + 1"
        toks1 = extract_ast_structural_tokens(code1)
        toks2 = extract_ast_structural_tokens(code2)
        # Both represent ASSIGN:VAR=BinOp(Add,VAR,CONST:num)
        self.assertEqual(toks1[0], toks2[0])

    def test_identifier_and_attribute_abstraction(self):
        """Verify that variable renaming and self.field encapsulation normalize consistently."""
        code1 = "total = current_val + 1"
        code2 = "self.accum = self.elem + 1"
        toks1 = extract_ast_structural_tokens(code1)
        toks2 = extract_ast_structural_tokens(code2)
        self.assertEqual(toks1[0], toks2[0])

class TestASTDetectorEndToEnd(unittest.TestCase):
    def setUp(self):
        self.detector = ASTWinnowingDetector(k=1, w=2)

    def test_identity_and_symmetry(self):
        code_a = '''def binary_search(arr, target):
    l = 0
    r = len(arr) - 1
    while l <= r:
        mid = (l + r) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            l = mid + 1
        else:
            r = mid - 1
    return -1
'''
        code_b = '''def lcs(s1, s2):
    m = len(s1)
    n = len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    return dp[m][n]
'''
        # Identity
        res_self = self.detector.compare_codes(code_a, code_a)
        self.assertAlmostEqual(res_self.jaccard, 1.0, places=4)
        self.assertAlmostEqual(res_self.dice, 1.0, places=4)
        self.assertGreater(res_self.execution_time_sec, 0.0)

        # Symmetry
        res_ab = self.detector.compare_codes(code_a, code_b)
        res_ba = self.detector.compare_codes(code_b, code_a)
        self.assertAlmostEqual(res_ab.jaccard, res_ba.jaccard, places=4)

if __name__ == "__main__":
    unittest.main()
