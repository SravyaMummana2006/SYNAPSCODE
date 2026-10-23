def lcs(s1, s2):
    # Independent recursive approach with memoization
    cache = {}
    def match(i, j):
        if i == len(s1) or j == len(s2):
            return 0
        if (i, j) in cache:
            return cache[(i, j)]
        if s1[i] == s2[j]:
            res = 1 + match(i + 1, j + 1)
        else:
            res = max(match(i + 1, j), match(i, j + 1))
        cache[(i, j)] = res
        return res

    return match(0, 0)
