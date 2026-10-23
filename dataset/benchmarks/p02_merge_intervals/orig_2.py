def merge_intervals(intervals):
    # Independent approach using two separate lists of start and end points
    if not intervals:
        return []
    starts = sorted([iv[0] for iv in intervals])
    ends = sorted([iv[1] for iv in intervals])
    res = []
    start_ptr = 0
    for end_ptr in range(len(ends)):
        if end_ptr == len(ends) - 1 or starts[end_ptr + 1] > ends[end_ptr]:
            res.append([starts[start_ptr], ends[end_ptr]])
            start_ptr = end_ptr + 1
    return res
