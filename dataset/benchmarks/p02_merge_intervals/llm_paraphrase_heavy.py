def merge_intervals(intervals):
    """LLM rewritten: Extracted helper, modularized restructuring to hide resemblance."""
    def overlaps(span_a, span_b):
        return span_b[0] <= span_a[1]

    def consolidate(span_a, span_b):
        return [span_a[0], span_a[1] if span_a[1] >= span_b[1] else span_b[1]]

    if not intervals:
        return []

    pool = sorted(intervals, key=lambda s: s[0])
    stack = [pool[0]]
    idx = 1
    while idx < len(pool):
        candidate = pool[idx]
        top = stack[-1]
        if overlaps(top, candidate):
            stack[-1] = consolidate(top, candidate)
        else:
            stack.append(candidate)
        idx += 1
    return stack
