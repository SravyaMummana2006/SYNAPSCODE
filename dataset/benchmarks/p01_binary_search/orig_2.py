def binary_search(arr, target):
    # Completely independent recursive binary search implementation
    if not arr:
        return -1

    def _search(low, high):
        if low > high:
            return -1
        m = low + (high - low) // 2
        if arr[m] >= target:
            ans = _search(low, m - 1)
            if arr[m] == target and ans == -1:
                return m
            return ans
        else:
            return _search(m + 1, high)

    return _search(0, len(arr) - 1)
