def shortest_path(graph, start, end):
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
