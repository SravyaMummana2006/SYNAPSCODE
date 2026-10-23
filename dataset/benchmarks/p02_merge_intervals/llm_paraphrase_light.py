def merge_intervals(intervals):
    """LLM rewritten: Functional accumulator."""
    if not intervals:
        return []
    sorted_ivs = sorted(intervals, key=lambda x: x[0])
    result = [list(sorted_ivs[0])]
    for start, end in sorted_ivs[1:]:
        if start <= result[-1][1]:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return result
