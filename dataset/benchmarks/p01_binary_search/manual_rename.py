def binary_search(nums, key):
    # Identifiers renamed, comments modified
    start_idx = 0
    end_idx = len(nums) - 1
    matched_pos = -1
    while start_idx <= end_idx:
        middle_pos = (start_idx + end_idx) // 2
        if nums[middle_pos] == key:
            matched_pos = middle_pos
            end_idx = middle_pos - 1
        elif nums[middle_pos] < key:
            start_idx = middle_pos + 1
        else:
            end_idx = middle_pos - 1
    return matched_pos
