def knapsack(weights, values, capacity):
    # Independent 1D space-optimized dynamic programming
    if capacity <= 0 or not weights:
        return 0
    table = [0] * (capacity + 1)
    for wt, val in zip(weights, values):
        for cap in range(capacity, wt - 1, -1):
            with_item = table[cap - wt] + val
            if with_item > table[cap]:
                table[cap] = with_item
    return table[capacity]
