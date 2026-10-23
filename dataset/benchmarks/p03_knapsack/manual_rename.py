def knapsack(w_list, v_list, max_weight):
    item_count = len(w_list)
    if item_count == 0 or max_weight <= 0:
        return 0
    grid = [[0] * (max_weight + 1) for _ in range(item_count + 1)]
    for row in range(1, item_count + 1):
        cur_wt = w_list[row - 1]
        cur_val = v_list[row - 1]
        for col in range(max_weight + 1):
            if cur_wt <= col:
                grid[row][col] = max(grid[row - 1][col], grid[row - 1][col - cur_wt] + cur_val)
            else:
                grid[row][col] = grid[row - 1][col]
    return grid[item_count][max_weight]
