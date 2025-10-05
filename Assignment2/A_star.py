def make_graph():
    graph = {}

    for i in range(NodeVertical):
        for j in range(NodeHorizontal-1):
            key = f"({i},{j})-({i},{j+1})"
            value = CostsHorizontal[j]
            graph[key] = value

    for i in range(NodeVertical-1):
        for j in range(NodeHorizontal):
            key = f"({i},{j})-({i+1},{j})"
            value = CostsVertical[i]
            graph[key] = value

    INF = float("inf")
    graph["(0,0)-(0,1)"] = INF
    graph["(0,6)-(0,7)"] = INF
    graph["(1,0)-(1,1)"] = INF
    graph["(1,6)-(1,7)"] = INF
    graph["(2,3)-(2,4)"] = INF
    graph["(3,0)-(3,1)"] = INF
    graph["(3,2)-(3,3)"] = INF
    graph["(3,4)-(3,5)"] = INF
    graph["(3,6)-(3,7)"] = INF
    graph["(4,0)-(4,1)"] = INF
    graph["(4,6)-(4,7)"] = INF
    graph["(0,0)-(1,0)"] = INF
    graph["(0,2)-(1,2)"] = INF
    graph["(0,3)-(1,3)"] = INF
    graph["(0,6)-(1,6)"] = INF
    graph["(0,7)-(1,7)"] = INF
    graph["(1,0)-(2,0)"] = INF
    graph["(1,7)-(2,7)"] = INF
    graph["(2,0)-(3,0)"] = INF
    graph["(2,2)-(3,2)"] = INF
    graph["(2,7)-(3,7)"] = INF
    graph["(3,0)-(4,0)"] = INF
    graph["(3,4)-(4,4)"] = INF
    graph["(3,7)-(4,7)"] = INF

    # reverse edges
    for i in range(NodeVertical):
        for j in range(NodeHorizontal-1):
            key = f"({i},{j+1})-({i},{j})"
            value = graph[f"({i},{j})-({i},{j+1})"]
            graph[key] = value

    for i in range(NodeVertical-1):
        for j in range(NodeHorizontal):
            key = f"({i+1},{j})-({i},{j})"
            value = graph[f"({i},{j})-({i+1},{j})"]
            graph[key] = value

    return graph


def h_est(start, end):
    h = 0
    min_distance = min(CostsHorizontal+CostsVertical)
    for i in range(start["i"], end["i"]):
        h += min_distance

    for j in range(start["j"], end["j"]):
        h += min_distance
    return h

def find_child(node):
    childs = []
    if node["i"]-1 >= 0:
        child = {}
        child["i"] = node["i"] - 1
        child["j"] = node["j"]
        childs.append(child)
    if node["i"]+1 < NodeVertical:
        child = {}
        child["i"] = node["i"] + 1
        child["j"] = node["j"]
        childs.append(child)
    if node["j"]-1 >= 0:
        child = {}
        child["i"] = node["i"]
        child["j"] = node["j"] - 1
        childs.append(child)
    if node["j"]+1 < NodeHorizontal:
        child = {}
        child["i"] = node["i"]
        child["j"] = node["j"] + 1
        childs.append(child)
    return childs


def A_star(start, end):
    G = {}
    start_key = f"({start['i']},{start['j']})"
    visited =[start_key]
    path_length = 0
    G[f"({start['i']},{start['j']})"] = 0
    Candidates = set()
    q = start

    while q != end:
        childs = find_child(q)

        q_key = f"({q['i']},{q['j']})"


        # update G
        for child in childs:
            child_key = f"({child['i']},{child['j']})"
            if child_key not in visited:
                Candidates.add(child_key)

                cost_key = q_key+"-"+child_key
                cost = graph[cost_key]

                # update child's current cost g
                if child_key not in G:
                    G[child_key] = G[q_key] + cost
                else:
                    if G[q_key] + cost < G[child_key]:
                        G[child_key] = G[q_key] + cost

        # calculate f = g+h
        F = {}
        for node_key in Candidates:
            node = {}
            node["i"] = int(node_key[1])
            node["j"] = int(node_key[3])
            h = h_est(node, end)
            F[node_key] = G[node_key] + h

        # find the element with smallest f
        node_key_opt = min(F, key=F.get)
        q["i"] = int(node_key_opt[1])
        q["j"] = int(node_key_opt[3])
        Candidates.remove(node_key_opt)

        visited.append(node_key_opt)
        path_length = G[node_key_opt]

    return path_length


NodeHorizontal = 8
NodeVertical = 5

CostsHorizontal = [7, 21, 25, 20, 18, 28, 8]
CostsVertical = [19, 17, 17, 17]

graph = make_graph()

if __name__ == "__main__":
    start = {"i": 2, "j": 0}
    end = {"i": 2, "j": 7}
    print(A_star(start, end))
