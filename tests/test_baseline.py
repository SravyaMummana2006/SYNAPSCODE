"""
Comprehensive Unit Test Suite for Step 2: Baseline Engine (Token-Level Winnowing).
Verifies:
1. Rabin-Karp mathematical correctness (rolling hash == direct polynomial hash).
2. Winnowing algorithm exact match against Schleimer et al. (2003) SIGMOD paper example.
3. Tokenizer normalization & identifier abstraction.
4. End-to-end detector properties (identity, symmetry, renaming invariance, runtime measurement).
"""

import os
import sys
import random
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from baseline.tokenizer import tokenize_code, tokens_to_stream
from baseline.rabin_karp import compute_rolling_hashes, direct_hash, PRIME_MODULUS, DEFAULT_BASE
from baseline.winnowing import winnow, Fingerprint
from baseline.detector import TokenWinnowingDetector

class TestRabinKarp(unittest.TestCase):
    def test_rolling_hash_matches_direct_hash(self):
        """Verify rolling hash values match direct O(k) polynomial calculation for all positions."""
        random.seed(42)
        sequence_len = 250
        k = 15
        tokens = [random.randint(1, 100) for _ in range(sequence_len)]

        rolling_results = compute_rolling_hashes(tokens, k)
        self.assertEqual(len(rolling_results), sequence_len - k + 1)

        for hash_val, pos in rolling_results:
            window = tokens[pos : pos + k]
            expected = direct_hash(window, DEFAULT_BASE, PRIME_MODULUS)
            self.assertEqual(hash_val, expected, f"Mismatch at position {pos}")

    def test_short_sequence(self):
        """Sequences shorter than k should produce one direct hash or empty if empty."""
        tokens = [1, 2, 3]
        res = compute_rolling_hashes(tokens, k=5)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], direct_hash(tokens))

        empty_res = compute_rolling_hashes([], k=5)
        self.assertEqual(empty_res, [])

class TestWinnowingPaperReference(unittest.TestCase):
    def test_schleimer_sigmod_2003_example(self):
        """
        Verify implementation against the exact numeric trace published in
        Section 3 of Schleimer, Wilkerson & Aiken (SIGMOD 2003).

        Input hashes:
        [77, 74, 42, 17, 98, 50, 17, 98, 8, 88, 67, 39, 77, 74, 42, 17, 98]
        with window size w = 4.
        
        Expected selected fingerprints (hash, position):
        (17, 3), (17, 6), (8, 8), (39, 11), (17, 15)
        """
        raw_hashes = [77, 74, 42, 17, 98, 50, 17, 98, 8, 88, 67, 39, 77, 74, 42, 17, 98]
        hashes_with_pos = [(h, idx) for idx, h in enumerate(raw_hashes)]
        w = 4

        fps = winnow(hashes_with_pos, window_size=w)

        expected_pairs = [(17, 3), (17, 6), (8, 8), (39, 11), (17, 15)]
        actual_pairs = [(fp.hash_value, fp.position) for fp in fps]

        self.assertEqual(actual_pairs, expected_pairs, 
                         f"Winnowing did not match SIGMOD 2003 paper example!\nExpected: {expected_pairs}\nActual: {actual_pairs}")

class TestTokenizer(unittest.TestCase):
    def test_identifier_abstraction_and_comment_stripping(self):
        code1 = '''# A sample function
def add_numbers(x, y):
    """Docstring explaining addition"""
    total = x + y  # inline comment
    return total
'''
        code2 = '''def compute_sum(first_val, second_val):
    accum = first_val + second_val
    return accum
'''
        tokens1 = tokenize_code(code1, abstract_identifiers=True, abstract_literals=True)
        tokens2 = tokenize_code(code2, abstract_identifiers=True, abstract_literals=True)

        type_seq1 = [t.type_str for t in tokens1]
        type_seq2 = [t.type_str for t in tokens2]

        # Both functions have identical syntax patterns: def ID(ID, ID): ID = ID + ID; return ID
        self.assertEqual(type_seq1, type_seq2)

class TestDetectorEndToEnd(unittest.TestCase):
    def setUp(self):
        self.detector = TokenWinnowingDetector(k=8, w=4)

    def test_identity_and_symmetry(self):
        code_a = '''def factorial(n):
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
'''
        code_b = '''def binary_search(arr, target):
    l = 0
    r = len(arr) - 1
    while l <= r:
        m = (l + r) // 2
        if arr[m] == target:
            return m
        elif arr[m] < target:
            l = m + 1
        else:
            r = m - 1
    return -1
'''
        # Self similarity must be 1.0
        res_self = self.detector.compare_codes(code_a, code_a)
        self.assertAlmostEqual(res_self.jaccard, 1.0, places=4)
        self.assertAlmostEqual(res_self.dice, 1.0, places=4)
        self.assertGreater(res_self.execution_time_sec, 0.0)

        # Symmetry: Jaccard(A, B) == Jaccard(B, A)
        res_ab = self.detector.compare_codes(code_a, code_b)
        res_ba = self.detector.compare_codes(code_b, code_a)
        self.assertAlmostEqual(res_ab.jaccard, res_ba.jaccard, places=4)
        self.assertAlmostEqual(res_ab.dice, res_ba.dice, places=4)

    def test_renamed_obfuscation_high_similarity(self):
        """Code with variable renames should have very high similarity in token winnowing."""
        code1 = '''def calculate_mean(values):
    count = len(values)
    if count == 0:
        return 0.0
    running_sum = 0
    for element in values:
        running_sum += element
    return running_sum / count
'''
        code2 = '''def get_average(items):
    n = len(items)
    if n == 0:
        return 0.0
    s = 0
    for x in items:
        s += x
    return s / n
'''
        res = self.detector.compare_codes(code1, code2)
        # Because identifiers are abstracted and structure is identical, Jaccard should be 1.0
        self.assertAlmostEqual(res.jaccard, 1.0, places=3)

    def test_independent_problems_low_similarity(self):
        """Unrelated problems should have near zero similarity."""
        code1 = '''def find_max(elements):
    if not elements:
        return None
    largest = elements[0]
    for val in elements:
        if val > largest:
            largest = val
    return largest
'''
        code2 = '''class Node:
    def __init__(self, key):
        self.left = None
        self.right = None
        self.val = key
'''
        res = self.detector.compare_codes(code1, code2)
        self.assertLess(res.jaccard, 0.2)

if __name__ == "__main__":
    unittest.main()
