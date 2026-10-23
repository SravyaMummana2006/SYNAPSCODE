def binary_search(arr, target):
    """LLM rewritten: Clean pythonic style with bisect semantics."""
    l, r = 0, len(arr) - 1
    found_idx = -1
    while l <= r:
        pivot = (l + r) >> 1
        current = arr[pivot]
        if current == target:
            found_idx = pivot
            r = pivot - 1
        elif current < target:
            l = pivot + 1
        else:
            r = pivot - 1
    return found_idx
