def knapsack(weights, values, capacity):
    n = len(weights)
    if n == 0 or capacity <= 0:
        return 0
    dp = []
    idx = 0
    while idx <= n:
        dp.append([0] * (capacity + 1))
        idx += 1
    i = 1
    while i <= n:
        w = weights[i - 1]
        v = values[i - 1]
        c = 0
        while c <= capacity:
            prev = dp[i - 1][c]
            if c >= w:
                candidate = dp[i - 1][c - w] + v
                if candidate > prev:
                    dp[i][c] = candidate
                else:
                    dp[i][c] = prev
            else:
                dp[i][c] = prev
            c += 1
        i += 1
    return dp[n][capacity]
