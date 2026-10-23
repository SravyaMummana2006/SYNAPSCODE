from collections import deque

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
