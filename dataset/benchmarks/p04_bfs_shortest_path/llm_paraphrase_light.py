from collections import deque

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
