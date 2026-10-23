"""
Winnowing Local Algorithm for Document and Code Fingerprinting.
Reference:
Schleimer, S., Wilkerson, D. & Aiken, A. (2003).
Winnowing: Local Algorithms for Document Fingerprinting. ACM SIGMOD.

Selects representative hashes from sliding windows with guaranteed detection
of matches >= (w + k - 1) tokens, discarding matches < k tokens.
"""

from typing import List, Tuple
from dataclasses import dataclass

@dataclass(frozen=True)
class Fingerprint:
    hash_value: int
    position: int     # Token index where the k-gram begins

    def __repr__(self):
        return f"FP({self.hash_value}@{self.position})"

def winnow(hashes: List[Tuple[int, int]], window_size: int) -> List[Fingerprint]:
    """
    Applies the Winnowing algorithm to a sequence of (hash, position) pairs.

    Args:
        hashes: Sequence of (hash_value, position) from rolling hash.
        window_size: Window size w.

    Returns:
        List of selected Fingerprints.
    """
    if not hashes:
        return []

    w = max(1, window_size)
    n = len(hashes)

    # If fewer hashes than window size, pick the minimum hash (rightmost on tie)
    if n <= w:
        min_pair = hashes[0]
        for pair in hashes[1:]:
            # Tie-breaking: <= picks rightmost
            if pair[0] <= min_pair[0]:
                min_pair = pair
        return [Fingerprint(min_pair[0], min_pair[1])]

    fingerprints: List[Fingerprint] = []
    last_selected_pos = -1

    # Sliding window of size w
    # Windows: [0 .. w-1], [1 .. w], ..., [n-w .. n-1]
    for i in range(n - w + 1):
        window = hashes[i : i + w]
        
        # Find minimum in window.
        # Tie breaking rule (Schleimer et al. 2003 Section 3):
        # In case of tie, select rightmost occurrence.
        min_hash, min_pos = window[0]
        for h, pos in window[1:]:
            if h <= min_hash:
                min_hash = h
                min_pos = pos

        # Deduplication: Record only if this minimum hasn't already been recorded
        if min_pos != last_selected_pos:
            fingerprints.append(Fingerprint(min_hash, min_pos))
            last_selected_pos = min_pos

    return fingerprints
