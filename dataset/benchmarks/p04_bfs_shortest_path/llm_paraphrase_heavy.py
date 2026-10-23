def shortest_path(graph, start, end):
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
