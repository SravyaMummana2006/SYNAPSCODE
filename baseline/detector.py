"""
End-to-End Classical Token-Winnowing Plagiarism Detector (MOSS-style).
Integrates:
- Tokenization & Identifier Abstraction
- Rabin-Karp Rolling Hashes
- Winnowing Fingerprint Selection
- Pairwise Similarity Metrics (Jaccard, Containment, Dice)
- Execution time tracking (for evaluation metric: pairwise comparison time)
"""

import time
from typing import List, Set, Tuple
from dataclasses import dataclass

from .tokenizer import tokenize_code, tokens_to_stream, CodeToken
from .rabin_karp import compute_rolling_hashes
from .winnowing import winnow, Fingerprint

@dataclass
class SimilarityResult:
    jaccard: float
    dice: float
    containment_a: float
    containment_b: float
    shared_fingerprints_count: int
    total_fingerprints_a: int
    total_fingerprints_b: int
    execution_time_sec: float

class TokenWinnowingDetector:
    """
    Classical Token-level Winnowing Plagiarism Detector.
    Matches the baseline architecture of MOSS (Schleimer et al. 2003).
    """

    def __init__(
        self,
        k: int = 12,
        w: int = 8,
        abstract_identifiers: bool = True,
        abstract_literals: bool = True
    ):
        """
        Args:
            k: K-gram length in tokens (noise threshold).
            w: Winnowing window size in k-grams.
            abstract_identifiers: Abstract variables/functions to 'ID'.
            abstract_literals: Abstract numbers and strings to 'LIT'.
        """
        self.k = k
        self.w = w
        self.abstract_identifiers = abstract_identifiers
        self.abstract_literals = abstract_literals

    def extract_fingerprints(self, source_code: str) -> Tuple[List[Fingerprint], List[CodeToken]]:
        """
        Extracts winnowed fingerprints and parsed tokens from source code.
        """
        tokens = tokenize_code(
            source_code,
            abstract_identifiers=self.abstract_identifiers,
            abstract_literals=self.abstract_literals
        )
        token_stream = tokens_to_stream(tokens)
        rolling_hashes = compute_rolling_hashes(token_stream, self.k)
        fingerprints = winnow(rolling_hashes, self.w)
        return fingerprints, tokens

    def compare_codes(self, code_a: str, code_b: str) -> SimilarityResult:
        """
        Performs pairwise comparison between two source code strings.
        Returns detailed similarity metrics and execution time.
        """
        start_time = time.perf_counter()

        fp_a, _ = self.extract_fingerprints(code_a)
        fp_b, _ = self.extract_fingerprints(code_b)

        # Set of hash values (ignoring positions for set-based similarity)
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
