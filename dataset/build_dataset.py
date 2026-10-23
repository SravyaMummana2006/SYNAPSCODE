"""
Dataset generator and benchmark builder for code plagiarism detection.
Curates 5 representative algorithmic problem benchmarks (CodeNet/SOCO/IR-Plag style)
with:
- Independent original implementations (for false positive / negative testing)
- Manual obfuscation variants (identifier renaming, loop conversion, statement reordering)
- LLM paraphrase variants (light idiomatic rewriting, heavy structural evasion)
Includes verification test cases for each problem to ensure all variants are functionally equivalent.
"""

import os
import json
import ast

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BENCHMARKS_DIR = os.path.join(BASE_DIR, "benchmarks")

PROBLEMS = {
    "p01_binary_search": {
        "description": "Find the first index of target in sorted array, or -1 if not found.",
        "test_cases": [
            {"args": ([1, 2, 4, 4, 5, 8, 10], 4), "expected": 2},
            {"args": ([1, 2, 3], 5), "expected": -1},
            {"args": ([], 1), "expected": -1},
            {"args": ([7], 7), "expected": 0},
            {"args": ([2, 4, 6, 8, 10, 12, 14, 16], 14), "expected": 6},
        ],
        "files": {
            "orig_1.py": '''def binary_search(arr, target):
    # Standard iterative binary search
    left = 0
    right = len(arr) - 1
    result = -1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            result = mid
            right = mid - 1  # find first occurrence
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result
''',
            "orig_2.py": '''def binary_search(arr, target):
    # Completely independent recursive binary search implementation
    if not arr:
        return -1

    def _search(low, high):
        if low > high:
            return -1
        m = low + (high - low) // 2
        if arr[m] >= target:
            ans = _search(low, m - 1)
            if arr[m] == target and ans == -1:
                return m
            return ans
        else:
            return _search(m + 1, high)

    return _search(0, len(arr) - 1)
''',
            "orig_3.py": '''def binary_search(arr, target):
    # Independent bisect-style lower bound approach
    n = len(arr)
    if n == 0:
        return -1
    lo = 0
    hi = n
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    if lo < n and arr[lo] == target:
        return lo
    return -1
''',
            "manual_rename.py": '''def binary_search(nums, key):
    # Identifiers renamed, comments modified
    start_idx = 0
    end_idx = len(nums) - 1
    matched_pos = -1
    while start_idx <= end_idx:
        middle_pos = (start_idx + end_idx) // 2
        if nums[middle_pos] == key:
            matched_pos = middle_pos
            end_idx = middle_pos - 1
        elif nums[middle_pos] < key:
            start_idx = middle_pos + 1
        else:
            end_idx = middle_pos - 1
    return matched_pos
''',
            "manual_structure.py": '''def binary_search(arr, target):
    # While loop inverted to loop with break and helper variable
    left = 0
    right = len(arr) - 1
    ans = -1
    active = True
    while active:
        if left > right:
            active = False
            break
        mid = (left + right) // 2
        val = arr[mid]
        if val == target:
            ans = mid
            right = mid - 1
            continue
        if val < target:
            left = mid + 1
        else:
            right = mid - 1
    return ans
''',
            "llm_paraphrase_light.py": '''def binary_search(arr, target):
    """LLM rewritten: Clean pythonic style with bisect semantics."""
    l, r = 0, len(arr) - 1
    found_idx = -1
    while l <= r:
        pivot = (l + r) >> 1
        current = arr[pivot]
        if current == target:
            found_idx = pivot
            r = pivot - 1
        elif current < target:
            l = pivot + 1
        else:
            r = pivot - 1
    return found_idx
''',
            "llm_paraphrase_heavy.py": '''def binary_search(arr, target):
    """LLM rewritten: Heavy obfuscation to evade token matching."""
    def _bisect_left(data, val, lower_bound, upper_bound):
        candidate = -1
        while lower_bound <= upper_bound:
            center = (lower_bound + upper_bound) // 2
            element = data[center]
            if element >= val:
                if element == val:
                    candidate = center
                upper_bound = center - 1
            else:
                lower_bound = center + 1
        return candidate

    if len(arr) == 0:
        return -1
    return _bisect_left(arr, target, 0, len(arr) - 1)
'''
        }
    },
    "p02_merge_intervals": {
        "description": "Merge all overlapping intervals and return non-overlapping intervals sorted by start time.",
        "test_cases": [
            {"args": ([[1, 3], [2, 6], [8, 10], [15, 18]],), "expected": [[1, 6], [8, 10], [15, 18]]},
            {"args": ([[1, 4], [4, 5]],), "expected": [[1, 5]]},
            {"args": ([],), "expected": []},
            {"args": ([[2, 3], [4, 5], [6, 7]],), "expected": [[2, 3], [4, 5], [6, 7]]},
            {"args": ([[1, 10], [2, 3], [4, 8], [9, 12]],), "expected": [[1, 12]]},
        ],
        "files": {
            "orig_1.py": '''def merge_intervals(intervals):
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for current in intervals[1:]:
        previous = merged[-1]
        if current[0] <= previous[1]:
            previous[1] = max(previous[1], current[1])
        else:
            merged.append(current)
    return merged
''',
            "orig_2.py": '''def merge_intervals(intervals):
    # Independent approach using two separate lists of start and end points
    if not intervals:
        return []
    starts = sorted([iv[0] for iv in intervals])
    ends = sorted([iv[1] for iv in intervals])
    res = []
    start_ptr = 0
    for end_ptr in range(len(ends)):
        if end_ptr == len(ends) - 1 or starts[end_ptr + 1] > ends[end_ptr]:
            res.append([starts[start_ptr], ends[end_ptr]])
            start_ptr = end_ptr + 1
    return res
''',
            "orig_3.py": '''def merge_intervals(intervals):
    # Independent approach: reduce/fold style accumulator
    if not intervals:
        return []
    ordered = sorted(intervals, key=lambda pair: (pair[0], pair[1]))
    output = []
    curr_start, curr_end = ordered[0]
    for i in range(1, len(ordered)):
        s, e = ordered[i]
        if s <= curr_end:
            if e > curr_end:
                curr_end = e
        else:
            output.append([curr_start, curr_end])
            curr_start, curr_end = s, e
    output.append([curr_start, curr_end])
    return output
''',
            "manual_rename.py": '''def merge_intervals(segments):
    if not segments:
        return []
    segments.sort(key=lambda item: item[0])
    combined_list = [segments[0]]
    for item in segments[1:]:
        last_seg = combined_list[-1]
        if item[0] <= last_seg[1]:
            last_seg[1] = max(last_seg[1], item[1])
        else:
            combined_list.append(item)
    return combined_list
''',
            "manual_structure.py": '''def merge_intervals(intervals):
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
''',
            "llm_paraphrase_light.py": '''def merge_intervals(intervals):
    """LLM rewritten: Functional accumulator."""
    if not intervals:
        return []
    sorted_ivs = sorted(intervals, key=lambda x: x[0])
    result = [list(sorted_ivs[0])]
    for start, end in sorted_ivs[1:]:
        if start <= result[-1][1]:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return result
''',
            "llm_paraphrase_heavy.py": '''def merge_intervals(intervals):
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
'''
        }
    },
    "p03_knapsack": {
        "description": "0/1 Knapsack: Given weights, values, and capacity W, return the maximum achievable value.",
        "test_cases": [
            {"args": ([1, 2, 3], [10, 15, 40], 6), "expected": 65},
            {"args": ([3, 2, 5], [30, 20, 50], 4), "expected": 30},
            {"args": ([], [], 10), "expected": 0},
            {"args": ([5, 10, 20], [50, 60, 140], 5), "expected": 50},
            {"args": ([2, 3, 4, 5], [3, 4, 5, 6], 5), "expected": 7},
        ],
        "files": {
            "orig_1.py": '''def knapsack(weights, values, capacity):
    # Standard 2D dynamic programming table
    n = len(weights)
    if n == 0 or capacity <= 0:
        return 0
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w = weights[i - 1]
        v = values[i - 1]
        for c in range(capacity + 1):
            if w <= c:
                dp[i][c] = max(dp[i - 1][c], dp[i - 1][c - w] + v)
            else:
                dp[i][c] = dp[i - 1][c]
    return dp[n][capacity]
''',
            "orig_2.py": '''def knapsack(weights, values, capacity):
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
''',
            "orig_3.py": '''def knapsack(weights, values, capacity):
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
''',
            "manual_rename.py": '''def knapsack(w_list, v_list, max_weight):
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
''',
            "manual_structure.py": '''def knapsack(weights, values, capacity):
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
''',
            "llm_paraphrase_light.py": '''def knapsack(weights, values, capacity):
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
''',
            "llm_paraphrase_heavy.py": '''def knapsack(weights, values, capacity):
    """LLM rewritten: Class-based and helper extraction to circumvent token signatures."""
    class KnapsackSolver:
        def __init__(self, w, v, cap):
            self.w = w
            self.v = v
            self.cap = cap

        def compute(self):
            size = len(self.w)
            if size == 0 or self.cap <= 0:
                return 0
            memo_grid = [[0 for _ in range(self.cap + 1)] for _ in range(size + 1)]
            step = 1
            while step <= size:
                cost = self.w[step - 1]
                profit = self.v[step - 1]
                b = 0
                while b <= self.cap:
                    memo_grid[step][b] = memo_grid[step - 1][b]
                    if cost <= b:
                        new_val = profit + memo_grid[step - 1][b - cost]
                        memo_grid[step][b] = max(memo_grid[step][b], new_val)
                    b += 1
                step += 1
            return memo_grid[size][self.cap]

    return KnapsackSolver(weights, values, capacity).compute()
'''
        }
    },
    "p04_bfs_shortest_path": {
        "description": "Shortest path distance between start and end node in an unweighted undirected graph using BFS.",
        "test_cases": [
            {"args": ({0: [1, 2], 1: [0, 3], 2: [0, 3], 3: [1, 2]}, 0, 3), "expected": 2},
            {"args": ({0: [1], 1: [0, 2], 2: [1], 3: []}, 0, 3), "expected": -1},
            {"args": ({0: []}, 0, 0), "expected": 0},
            {"args": ({1: [2, 3], 2: [1, 4], 3: [1, 4], 4: [2, 3, 5], 5: [4]}, 1, 5), "expected": 3},
            {"args": ({}, 1, 2), "expected": -1},
        ],
        "files": {
            "orig_1.py": '''from collections import deque

def shortest_path(graph, start, end):
    # Standard queue-based BFS
    if start not in graph or end not in graph:
        return -1
    if start == end:
        return 0
    queue = deque([(start, 0)])
    visited = {start}
    while queue:
        current, dist = queue.popleft()
        if current == end:
            return dist
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    return -1
''',
            "orig_2.py": '''def shortest_path(graph, start, end):
    # Independent level-by-level frontier set BFS
    if start not in graph or end not in graph:
        return -1
    if start == end:
        return 0
    frontier = {start}
    seen = {start}
    steps = 0
    while frontier:
        next_frontier = set()
        steps += 1
        for node in frontier:
            for adj in graph.get(node, []):
                if adj == end:
                    return steps
                if adj not in seen:
                    seen.add(adj)
                    next_frontier.add(adj)
        frontier = next_frontier
    return -1
''',
            "orig_3.py": '''def shortest_path(graph, start, end):
    # Independent bidirectional BFS
    if start not in graph or end not in graph:
        return -1
    if start == end:
        return 0
    fwd = {start: 0}
    bwd = {end: 0}
    q_fwd = [start]
    q_bwd = [end]
    while q_fwd and q_bwd:
        curr_fwd = q_fwd.pop(0)
        d_fwd = fwd[curr_fwd]
        for nbr in graph.get(curr_fwd, []):
            if nbr in bwd:
                return d_fwd + 1 + bwd[nbr]
            if nbr not in fwd:
                fwd[nbr] = d_fwd + 1
                q_fwd.append(nbr)
        curr_bwd = q_bwd.pop(0)
        d_bwd = bwd[curr_bwd]
        for nbr in graph.get(curr_bwd, []):
            if nbr in fwd:
                return d_bwd + 1 + fwd[nbr]
            if nbr not in bwd:
                bwd[nbr] = d_bwd + 1
                q_bwd.append(nbr)
    return -1
''',
            "manual_rename.py": '''from collections import deque

def shortest_path(network, src, dst):
    if src not in network or dst not in network:
        return -1
    if src == dst:
        return 0
    fifo = deque([(src, 0)])
    explored = {src}
    while fifo:
        vertex, steps = fifo.popleft()
        if vertex == dst:
            return steps
        for nxt in network.get(vertex, []):
            if nxt not in explored:
                explored.add(nxt)
                fifo.append((nxt, steps + 1))
    return -1
''',
            "manual_structure.py": '''from collections import deque

def shortest_path(graph, start, end):
    # Flattened logic with list as queue instead of deque
    if start not in graph or end not in graph:
        return -1
    if start == end:
        return 0
    q = []
    q.append(start)
    dist = {}
    dist[start] = 0
    while len(q) > 0:
        cur = q.pop(0)
        d = dist[cur]
        if cur == end:
            return d
        neighbors = graph.get(cur, [])
        i = 0
        while i < len(neighbors):
            nb = neighbors[i]
            if nb not in dist:
                dist[nb] = d + 1
                q.append(nb)
            i += 1
    return -1
''',
            "llm_paraphrase_light.py": '''from collections import deque

def shortest_path(graph, start, end):
    """LLM rewritten: Defensive edge checks and tuple unpacking."""
    if not (start in graph and end in graph):
        return -1
    if start == end:
        return 0
    line = deque([(start, 0)])
    visited_nodes = {start}
    while len(line) > 0:
        head, depth = line.popleft()
        for adjacent in graph[head]:
            if adjacent == end:
                return depth + 1
            if adjacent not in visited_nodes:
                visited_nodes.add(adjacent)
                line.append((adjacent, depth + 1))
    return -1
''',
            "llm_paraphrase_heavy.py": '''def shortest_path(graph, start, end):
    """LLM rewritten: Object encapsulation with procedural generator exploration."""
    class GraphTraversal:
        def __init__(self, adj):
            self.adj = adj

        def execute_breadth_search(self, s, t):
            if s not in self.adj or t not in self.adj:
                return -1
            if s == t:
                return 0
            container = [(s, 0)]
            marked = set([s])
            head = 0
            while head < len(container):
                node, hop = container[head]
                head += 1
                edges = self.adj.get(node, [])
                for succ in edges:
                    if succ == t:
                        return hop + 1
                    if succ not in marked:
                        marked.add(succ)
                        container.append((succ, hop + 1))
            return -1

    engine = GraphTraversal(graph)
    return engine.execute_breadth_search(start, end)
'''
        }
    },
    "p05_lcs": {
        "description": "Compute length of Longest Common Subsequence of two strings s1 and s2.",
        "test_cases": [
            {"args": ("abcde", "ace"), "expected": 3},
            {"args": ("abc", "abc"), "expected": 3},
            {"args": ("abc", "def"), "expected": 0},
            {"args": ("", "abc"), "expected": 0},
            {"args": ("aggtab", "gxtxayb"), "expected": 4},
        ],
        "files": {
            "orig_1.py": '''def lcs(s1, s2):
    # Standard 2D table dynamic programming
    m = len(s1)
    n = len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]
''',
            "orig_2.py": '''def lcs(s1, s2):
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
''',
            "orig_3.py": '''def lcs(s1, s2):
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
''',
            "manual_rename.py": '''def lcs(seq_a, seq_b):
    len_a = len(seq_a)
    len_b = len(seq_b)
    table = [[0] * (len_b + 1) for _ in range(len_a + 1)]
    for row in range(1, len_a + 1):
        for col in range(1, len_b + 1):
            if seq_a[row - 1] == seq_b[col - 1]:
                table[row][col] = table[row - 1][col - 1] + 1
            else:
                table[row][col] = max(table[row - 1][col], table[row][col - 1])
    return table[len_a][len_b]
''',
            "manual_structure.py": '''def lcs(s1, s2):
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
''',
            "llm_paraphrase_light.py": '''def lcs(s1, s2):
    """LLM rewritten: Concise matrix initialization with zip and range."""
    rows, cols = len(s1), len(s2)
    matrix = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            matrix[r][c] = matrix[r - 1][c - 1] + 1 if s1[r - 1] == s2[c - 1] else max(matrix[r - 1][c], matrix[r][c - 1])
    return matrix[rows][cols]
''',
            "llm_paraphrase_heavy.py": '''def lcs(s1, s2):
    """LLM rewritten: Class based restructuring and dynamic table encapsulation."""
    class SubsequenceMatrix:
        def __init__(self, str1, str2):
            self.first = str1
            self.second = str2
            self.len1 = len(str1)
            self.len2 = len(str2)
            self.dp = [[0] * (self.len2 + 1) for _ in range(self.len1 + 1)]

        def populate(self):
            x = 1
            while x <= self.len1:
                y = 1
                while y <= self.len2:
                    match_found = (self.first[x - 1] == self.second[y - 1])
                    if match_found:
                        self.dp[x][y] = self.dp[x - 1][y - 1] + 1
                    else:
                        top = self.dp[x - 1][y]
                        left = self.dp[x][y - 1]
                        self.dp[x][y] = top if top > left else left
                    y += 1
                x += 1
            return self.dp[self.len1][self.len2]

    return SubsequenceMatrix(s1, s2).populate()
'''
        }
    }
}

def generate_benchmark_files():
    """Generates the benchmark problem directory tree and python files."""
    os.makedirs(BENCHMARKS_DIR, exist_ok=True)
    generated_count = 0
    for prob_name, prob_info in PROBLEMS.items():
        prob_dir = os.path.join(BENCHMARKS_DIR, prob_name)
        os.makedirs(prob_dir, exist_ok=True)
        for filename, code in prob_info["files"].items():
            filepath = os.path.join(prob_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            generated_count += 1
    print(f"Generated {generated_count} source files across {len(PROBLEMS)} problems.")

def generate_ground_truth_manifest():
    """
    Constructs all pairwise comparisons and assigns ground-truth labels.
    - Positive pairs (1): Plagiarized/rewritten variants compared against the original (orig_1.py).
    - Negative pairs (0):
      a) Independent solutions to the SAME problem (orig_1 vs orig_2, orig_1 vs orig_3, orig_2 vs orig_3)
      b) Solutions across DIFFERENT problems (cross-problem pairs)
    """
    pairs = []
    pair_id = 1

    # Within each problem
    for prob_name, prob_info in PROBLEMS.items():
        files = list(prob_info["files"].keys())
        
        # 1. Positives (orig_1 vs transformed variants)
        orig = f"{prob_name}/orig_1.py"
        positive_variants = [
            ("manual_rename.py", "plagiarism_manual_rename"),
            ("manual_structure.py", "plagiarism_manual_structure"),
            ("llm_paraphrase_light.py", "plagiarism_llm_light"),
            ("llm_paraphrase_heavy.py", "plagiarism_llm_heavy"),
        ]
        for variant_file, cat in positive_variants:
            pairs.append({
                "pair_id": pair_id,
                "file1": orig,
                "file2": f"{prob_name}/{variant_file}",
                "is_plagiarism": 1,
                "category": cat,
                "problem": prob_name
            })
            pair_id += 1

        # Also between variants of the same lineage (e.g. manual_rename vs llm_paraphrase_light)
        # to test cross-obfuscation detection
        pairs.append({
            "pair_id": pair_id,
            "file1": f"{prob_name}/manual_rename.py",
            "file2": f"{prob_name}/llm_paraphrase_heavy.py",
            "is_plagiarism": 1,
            "category": "plagiarism_cross_transformed",
            "problem": prob_name
        })
        pair_id += 1

        # 2. Negatives within same problem (independent implementations solving identical task)
        # This is the hardest challenge for plagiarism detectors: same algorithmic task, different authors!
        same_prob_negatives = [
            ("orig_1.py", "orig_2.py"),
            ("orig_1.py", "orig_3.py"),
            ("orig_2.py", "orig_3.py"),
            ("orig_2.py", "manual_rename.py"),
            ("orig_3.py", "llm_paraphrase_heavy.py"),
        ]
        for f1, f2 in same_prob_negatives:
            pairs.append({
                "pair_id": pair_id,
                "file1": f"{prob_name}/{f1}",
                "file2": f"{prob_name}/{f2}",
                "is_plagiarism": 0,
                "category": "independent_same_problem",
                "problem": prob_name
            })
            pair_id += 1

    # 3. Negatives across DIFFERENT problems (completely independent tasks)
    prob_keys = list(PROBLEMS.keys())
    for i in range(len(prob_keys)):
        for j in range(i + 1, len(prob_keys)):
            pA = prob_keys[i]
            pB = prob_keys[j]
            # Pair orig_1 of problem A with orig_1 of problem B
            pairs.append({
                "pair_id": pair_id,
                "file1": f"{pA}/orig_1.py",
                "file2": f"{pB}/orig_1.py",
                "is_plagiarism": 0,
                "category": "independent_diff_problem",
                "problem": f"{pA}_vs_{pB}"
            })
            pair_id += 1

    manifest_path = os.path.join(BASE_DIR, "ground_truth.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(pairs, f, indent=2)

    print(f"Generated ground truth manifest at {manifest_path} with {len(pairs)} labeled pairs.")
    return manifest_path

if __name__ == "__main__":
    generate_benchmark_files()
    generate_ground_truth_manifest()
