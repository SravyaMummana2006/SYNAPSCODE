def lcs(s1, s2):
    # Inverted nested loops to while loops with temporary variables
    m = len(s1)
    n = len(s2)
    grid = []
    r = 0
    while r <= m:
        grid.append([0] * (n + 1))
        r += 1
    i = 1
    while i <= m:
        c1 = s1[i - 1]
        j = 1
        while j <= n:
            c2 = s2[j - 1]
            if c1 == c2:
                grid[i][j] = grid[i - 1][j - 1] + 1
            else:
                left_val = grid[i][j - 1]
                up_val = grid[i - 1][j]
                grid[i][j] = left_val if left_val >= up_val else up_val
            j += 1
        i += 1
    return grid[m][n]
