from collections import deque

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
