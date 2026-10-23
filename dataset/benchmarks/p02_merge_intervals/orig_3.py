def merge_intervals(intervals):
    # Independent approach: reduce/fold style accumulator
    if not intervals:
        return []
    ordered = sorted(intervals, key=lambda pair: (pair[0], pair[1]))
    output = []
    curr_start, curr_end = ordered[0]
    for i in range(1, len(ordered)):
        s, e = ordered[i]
        if s <= curr_end:
            if e > curr_end:
                curr_end = e
        else:
            output.append([curr_start, curr_end])
            curr_start, curr_end = s, e
    output.append([curr_start, curr_end])
    return output
