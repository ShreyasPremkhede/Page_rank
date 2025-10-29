import os
import time
import pickle
import networkx as nx
import matplotlib.pyplot as plt

GPICKLE = "dblp_filtered_graph.gpickle"
POS_CACHE = "graph_pos.pickle"
OUT = "graph.png"

def load_graph(path):
    with open(path, "rb") as f:
        return pickle.load(f)

def load_or_compute_pos(G, cache=POS_CACHE):
    # Try to reuse previously-computed layout to save time
    if os.path.exists(cache):
        try:
            with open(cache, "rb") as f:
                pos = pickle.load(f)
            # ensure cached positions match nodes
            if set(pos.keys()) == set(G.nodes()):
                print("Loaded cached positions from", cache)
                return pos
            else:
                print("Cached positions node-set mismatch; recomputing layout")
        except Exception:
            print("Failed to load position cache; recomputing layout")

    n = G.number_of_nodes()
    print(f"Computing layout for {n} nodes...")
    start = time.time()
    # Heuristics: avoid expensive layout for very large graphs
    if n > 3000:
        # fast but random-looking layout for huge graphs
        pos = nx.random_layout(G, seed=42)
    elif n > 500:
        # medium-sized: faster spring layout
        pos = nx.spring_layout(G, seed=42, iterations=50)
    else:
        # small graphs: more refined layout
        pos = nx.spring_layout(G, seed=42, iterations=200)
    print(f"Layout computed in {time.time()-start:.2f}s")

    # Cache positions for future runs (best-effort)
    try:
        with open(cache, "wb") as f:
            pickle.dump(pos, f)
    except Exception:
        pass

    return pos

def main():
    G = load_graph(GPICKLE)
    print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    pos = load_or_compute_pos(G)

    plt.figure(figsize=(12, 8))
    n = G.number_of_nodes()

    # For very large graphs, draw a sampled subgraph to keep things fast and readable
    if n > 5000:
        nodes = list(G.nodes())[:2000]
        subG = G.subgraph(nodes)
        nx.draw_networkx_nodes(subG, pos, node_color="skyblue", node_size=50, alpha=0.8)
        nx.draw_networkx_edges(subG, pos, alpha=0.2, width=0.2)
    else:
        node_size = 800 if n <= 200 else 50
        nx.draw_networkx_nodes(G, pos, node_color="skyblue", node_size=node_size)
        nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.5)

    # Only draw labels for small graphs (labels are expensive and cluttered)
    if n <= 200:
        nx.draw_networkx_labels(G, pos, font_size=10)

    plt.axis("off")
    plt.savefig(OUT, dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved", OUT)

if __name__ == '__main__':
    main()