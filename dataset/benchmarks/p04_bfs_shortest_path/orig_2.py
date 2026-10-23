def shortest_path(graph, start, end):
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
