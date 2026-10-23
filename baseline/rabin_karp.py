"""
Rabin-Karp Rolling Hash implementation.
Reference:
Karp, R. & Rabin, M. (1987). Efficient Randomized Pattern-Matching Algorithms. IBM J. Res. Dev.

Computes rolling polynomial hashes over k-grams of token sequences in O(N) time.
"""

from typing import List, Tuple, Sequence

# Large prime modulus (Mersenne prime 2^31 - 1) and base
PRIME_MODULUS = 2147483647
DEFAULT_BASE = 257

def direct_hash(window: Sequence[int], base: int = DEFAULT_BASE, mod: int = PRIME_MODULUS) -> int:
    """Computes direct polynomial hash for a k-gram."""
    h = 0
    for val in window:
        h = (h * base + val) % mod
    return h

def compute_rolling_hashes(
    tokens: Sequence[int],
    k: int,
    base: int = DEFAULT_BASE,
    mod: int = PRIME_MODULUS
) -> List[Tuple[int, int]]:
    """
    Computes Rabin-Karp rolling hashes for all k-grams in a token sequence.

    Args:
        tokens: Sequence of integer token representations.
        k: Length of the k-gram.
        base: Multiplier base for polynomial rolling hash.
        mod: Prime modulus.

    Returns:
        List of tuples (hash_value, token_start_idx) for each k-gram.
        If len(tokens) < k, returns an empty list (or a single direct hash if non-empty).
    """
    n = len(tokens)
    if n < k:
        if n == 0:
            return []
        # Fallback for very small sequences: return a single hash of all tokens
        return [(direct_hash(tokens, base, mod), 0)]

    # Precompute base^(k-1) % mod
    base_k_minus_1 = pow(base, k - 1, mod)

    # 1. Compute hash of the initial k-gram
    curr_hash = 0
    for i in range(k):
        curr_hash = (curr_hash * base + tokens[i]) % mod

    results = [(curr_hash, 0)]

    # 2. Roll through the remaining tokens in O(1) per step
    for i in range(1, n - k + 1):
        prev_val = tokens[i - 1]
        next_val = tokens[i + k - 1]

        # H_{new} = ((H_{prev} - prev_val * base^(k-1)) * base + next_val) % mod
        curr_hash = (curr_hash - (prev_val * base_k_minus_1) % mod) % mod
        curr_hash = (curr_hash * base + next_val) % mod

        results.append((curr_hash, i))

    return results
