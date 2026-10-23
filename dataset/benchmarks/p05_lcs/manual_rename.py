def lcs(seq_a, seq_b):
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
