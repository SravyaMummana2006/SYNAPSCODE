def knapsack(weights, values, capacity):
    """LLM rewritten: Clean matrix DP with dict indexing avoided."""
    total_items = len(weights)
    if not total_items or capacity <= 0:
        return 0
    matrix = [[0] * (capacity + 1) for _ in range(total_items + 1)]
    for item_idx in range(1, total_items + 1):
        weight_cost = weights[item_idx - 1]
        gain = values[item_idx - 1]
        for current_weight in range(1, capacity + 1):
            matrix[item_idx][current_weight] = matrix[item_idx - 1][current_weight]
            if weight_cost <= current_weight:
                alternative = matrix[item_idx - 1][current_weight - weight_cost] + gain
                if alternative > matrix[item_idx][current_weight]:
                    matrix[item_idx][current_weight] = alternative
    return matrix[total_items][capacity]
