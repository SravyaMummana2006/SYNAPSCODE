from collections import deque

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
