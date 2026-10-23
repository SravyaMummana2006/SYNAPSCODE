def binary_search(arr, target):
    # While loop inverted to loop with break and helper variable
    left = 0
    right = len(arr) - 1
    ans = -1
    active = True
    while active:
        if left > right:
            active = False
            break
        mid = (left + right) // 2
        val = arr[mid]
        if val == target:
            ans = mid
            right = mid - 1
            continue
        if val < target:
            left = mid + 1
        else:
            right = mid - 1
    return ans
