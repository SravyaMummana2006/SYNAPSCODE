"""
AST-Normalized Winnowing Plagiarism Detector.

Integrates:
- AST Parsing & Normalization
- Commutative operation sorting and comparison operator canonicalization
- Scope abstraction and built-in function preservation
- Ordered structural statement & expression token stream extraction
- Rabin-Karp Rolling Hashes and Local Winnowing
- High-resolution pairwise comparison runtime tracking
"""

import time
from typing import List, Set, Tuple
from dataclasses import dataclass

from .linearizer import extract_ast_structural_tokens, tokens_to_id_stream
from baseline.rabin_karp import compute_rolling_hashes
from baseline.winnowing import winnow, Fingerprint
from baseline.detector import SimilarityResult

class ASTWinnowingDetector:
    """
    Improved Plagiarism Detector using AST-level Normalization and Winnowing.
    Overcomes LLM-based paraphrasing, identifier scrambling, and control flow rewrites.
    """

    def __init__(self, k: int = 1, w: int = 2):
        """
        Args:
            k: K-gram length for AST structural tokens (default 1 for statement/subtree granularity).
            w: Winnowing sliding window size (default 2 for local density reduction).
        """
        self.k = k
        self.w = w

    def extract_fingerprints(self, source_code: str) -> Tuple[List[Fingerprint], List[str]]:
        """
        Parses source code into canonical structural tokens and applies
        Rabin-Karp hashing and Winnowing.
        """
        tokens = extract_ast_structural_tokens(source_code)
        int_stream = tokens_to_id_stream(tokens)
        rolling_hashes = compute_rolling_hashes(int_stream, self.k)
        fingerprints = winnow(rolling_hashes, self.w)
        return fingerprints, tokens

    def compare_codes(self, code_a: str, code_b: str) -> SimilarityResult:
        """
        Performs pairwise comparison between two source code strings using AST Winnowing.
        Returns Jaccard, Dice, Containment, and execution time in seconds.
        """
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
        """Loads and compares two files from disk."""
        with open(file_a_path, "r", encoding="utf-8") as fa:
            code_a = fa.read()
        with open(file_b_path, "r", encoding="utf-8") as fb:
            code_b = fb.read()
        return self.compare_codes(code_a, code_b)
