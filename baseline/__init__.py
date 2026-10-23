"""
Classical Baseline Plagiarism Detection Package using Rabin-Karp & Winnowing.
"""

from .tokenizer import tokenize_code, tokens_to_stream, CodeToken
from .rabin_karp import compute_rolling_hashes, direct_hash
from .winnowing import winnow, Fingerprint
from .detector import TokenWinnowingDetector, SimilarityResult

__all__ = [
    "tokenize_code",
    "tokens_to_stream",
    "CodeToken",
    "compute_rolling_hashes",
    "direct_hash",
    "winnow",
    "Fingerprint",
    "TokenWinnowingDetector",
    "SimilarityResult",
]
