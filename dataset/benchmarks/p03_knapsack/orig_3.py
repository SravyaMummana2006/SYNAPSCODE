def knapsack(weights, values, capacity):
    # Independent memoized top-down recursion
    memo = {}
    def solve(idx, rem_cap):
        if idx >= len(weights) or rem_cap <= 0:
            return 0
        state = (idx, rem_cap)
        if state in memo:
            return memo[state]
        skip = solve(idx + 1, rem_cap)
        take = 0
        if weights[idx] <= rem_cap:
            take = values[idx] + solve(idx + 1, rem_cap - weights[idx])
        memo[state] = max(skip, take)
        return memo[state]

    return solve(0, capacity)
