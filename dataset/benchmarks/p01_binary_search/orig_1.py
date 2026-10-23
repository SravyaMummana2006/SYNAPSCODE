def binary_search(arr, target):
    # Standard iterative binary search
    left = 0
    right = len(arr) - 1
    result = -1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            result = mid
            right = mid - 1  # find first occurrence
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result
