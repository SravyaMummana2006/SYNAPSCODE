def merge_intervals(intervals):
    # Loop converted to index-based while loop
    if len(intervals) == 0:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = []
    merged.append(intervals[0])
    i = 1
    n = len(intervals)
    while i < n:
        cur = intervals[i]
        last = merged[-1]
        can_merge = cur[0] <= last[1]
        if can_merge:
            if cur[1] > last[1]:
                last[1] = cur[1]
        else:
            merged.append(cur)
        i += 1
    return merged
