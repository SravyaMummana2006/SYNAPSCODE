def lcs(s1, s2):
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
