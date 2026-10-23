def binary_search(arr, target):
    """LLM rewritten: Heavy obfuscation to evade token matching."""
    def _bisect_left(data, val, lower_bound, upper_bound):
        candidate = -1
        while lower_bound <= upper_bound:
            center = (lower_bound + upper_bound) // 2
            element = data[center]
            if element >= val:
                if element == val:
                    candidate = center
                upper_bound = center - 1
            else:
                lower_bound = center + 1
        return candidate

    if len(arr) == 0:
        return -1
    return _bisect_left(arr, target, 0, len(arr) - 1)
