def binary_search(arr, target):
    # Independent bisect-style lower bound approach
    n = len(arr)
    if n == 0:
        return -1
    lo = 0
    hi = n
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    if lo < n and arr[lo] == target:
        return lo
    return -1
