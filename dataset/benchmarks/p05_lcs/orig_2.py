def lcs(s1, s2):
    # Independent rolling two-row dynamic programming
    m, n = len(s1), len(s2)
    if m == 0 or n == 0:
        return 0
    prev = [0] * (n + 1)
    for char1 in s1:
        curr = [0] * (n + 1)
        for j, char2 in enumerate(s2, 1):
            if char1 == char2:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev = curr
    return prev[n]
