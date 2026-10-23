def lcs(s1, s2):
    """LLM rewritten: Concise matrix initialization with zip and range."""
    rows, cols = len(s1), len(s2)
    matrix = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            matrix[r][c] = matrix[r - 1][c - 1] + 1 if s1[r - 1] == s2[c - 1] else max(matrix[r - 1][c], matrix[r][c - 1])
    return matrix[rows][cols]
