from z3 import *

# define the graph =========================================================
NodeHorizontal = 8
NodeVertical = 5

CostsHorizontal = [7, 21, 25, 20, 18, 28, 8]
CostsVertical = [19, 17, 17, 17]

edges = []
weights = {}

for i in range(NodeVertical):
    for j in range(NodeHorizontal-1):
        edge = f"({i},{j})-({i},{j+1})"
        weight = CostsHorizontal[j]
        edges.append(edge)
        weights[edge] = weight

for i in range(NodeVertical-1):
    for j in range(NodeHorizontal):
        edge = f"({i},{j})-({i+1},{j})"
        weight = CostsVertical[i]
        edges.append(edge)
        weights[edge] = weight

edges_impossible = ["(0,0)-(0,1)",
                    "(0,6)-(0,7)",
                    "(1,0)-(1,1)",
                    "(1,6)-(1,7)",
                    "(2,3)-(2,4)",
                    "(3,0)-(3,1)",
                    "(3,2)-(3,3)",
                    "(3,4)-(3,5)",
                    "(3,6)-(3,7)",
                    "(4,0)-(4,1)",
                    "(4,6)-(4,7)",
                    "(0,0)-(1,0)",
                    "(0,2)-(1,2)",
                    "(0,3)-(1,3)",
                    "(0,6)-(1,6)",
                    "(0,7)-(1,7)",
                    "(1,0)-(2,0)",
                    "(1,7)-(2,7)",
                    "(2,0)-(3,0)",
                    "(2,2)-(3,2)",
                    "(2,7)-(3,7)",
                    "(3,0)-(4,0)",
                    "(3,4)-(4,4)",
                    "(3,7)-(4,7)"]
for edge in edges_impossible:
    edges.remove(edge)

nodes = []
for i in range(NodeVertical):
    for j in range(NodeHorizontal):
        node = f"({i},{j})"
        nodes.append(node)

edges_z3 = {e: Bool(e) for e in edges}
nodes_z3 = {n: Bool(n) for n in nodes}

opt = Optimize()

# constraints =========================================================
def find_neighbor_edges(node_key):
    node = {}
    node["i"] = int(node_key[1])
    node["j"] = int(node_key[3])

    neighbor_edges = []
    if node["i"]-1 >= 0:
        neighbor_node_key = f"({node['i']-1},{node['j']})"
        neighbor_edge = neighbor_node_key + "-" + node_key
        if neighbor_edge in edges:
            neighbor_edges.append(neighbor_edge)

    if node["i"]+1 < NodeVertical:
        neighbor_node_key = f"({node['i']+1},{node['j']})"
        neighbor_edge = node_key + "-" + neighbor_node_key
        if neighbor_edge in edges:
            neighbor_edges.append(neighbor_edge)

    if node["j"]-1 >= 0:
        neighbor_node_key = f"({node['i']},{node['j']-1})"
        neighbor_edge = neighbor_node_key + "-" + node_key
        if neighbor_edge in edges:
            neighbor_edges.append(neighbor_edge)

    if node["j"]+1 < NodeHorizontal:
        neighbor_node_key = f"({node['i']},{node['j']+1})"
        neighbor_edge = node_key + "-" + neighbor_node_key
        if neighbor_edge in edges:
            neighbor_edges.append(neighbor_edge)

    return neighbor_edges


# start / end nodes: only one outgoing / ingoing edge
start_node = "(2,2)"
neighbor_edges = find_neighbor_edges(start_node)
opt.add(Sum([If(edges_z3[e], 1, 0) for e in neighbor_edges]) == 1)
opt.add(nodes_z3[start_node] == True)

end_node = "(3,5)"
neighbor_edges = find_neighbor_edges(end_node)
opt.add(Sum([If(edges_z3[e], 1, 0) for e in neighbor_edges]) == 1)
opt.add(nodes_z3[end_node] == True)

# other nodes: if A is True → exactly two edges True; if not → all False
for node in nodes:
    if node != start_node and node != end_node:
        neighbor_edges = find_neighbor_edges(node)
        opt.add(Implies(nodes_z3[node], Sum([If(edges_z3[e],1,0) for e in neighbor_edges]) == 2))
        opt.add(Implies(Not(nodes_z3[node]), Sum([If(edges_z3[e],1,0) for e in neighbor_edges]) == 0))

# objective function =========================================================
length_z3 = Sum([weights[e]*If(edges_z3[e],1,0) for e in edges])
obj = opt.minimize(length_z3)

# solve the problem =========================================================
opt.set(timeout=600000)

paths = []
lengths = []

for i in range(10):  # find 10 shortest paths
    result = opt.check()
    if result == sat:
        m = opt.model()
        path = [e for e in edges if is_true(m[edges_z3[e]])]
        paths.append(path)

        length = opt.lower(obj)
        lengths.append(length)

        opt.add(Not(And([edges_z3[e] for e in path])))

        print(f"path {i}: length: {length}, route:", path)