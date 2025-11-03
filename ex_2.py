import os
import pickle
from collections import Counter
from itertools import combinations


def load_graph(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def top_k_from_counter(counter, k=10):
    return counter.most_common(k)


def compute_co_citation(G):
    """
    Co-citation: number of papers that cite both i and j.
    For each citing paper (source) look at its cited targets and increment counts for each pair.
    """
    counts = Counter()
    # iterate over each paper that cites others
    for source in G.nodes():
        # targets that `source` cites: outgoing neighbors
        targets = list(G.successors(source))
        if len(targets) < 2:
            continue
        # increment for each unordered pair of targets
        for a, b in combinations(sorted(targets), 2):
            counts[(a, b)] += 1
    return counts


def compute_bibliographic_coupling(G):
    """
    Bibliographic coupling: number of shared references between i and j.
    For each cited paper (target), look at its citing sources (predecessors) and increment counts for each pair of sources.
    """
    counts = Counter()
    for target in G.nodes():
        sources = list(G.predecessors(target))
        if len(sources) < 2:
            continue
        for a, b in combinations(sorted(sources), 2):
            counts[(a, b)] += 1
    return counts


def id_to_title(G, node_id):
    return G.nodes[node_id].get("title") if G.nodes[node_id].get("title") else str(node_id)


def print_top(title, pairs, G):
    print("\n" + title)
    print("S.No.\tScore\tTitle A\tTitle B")
    for i, ((a, b), score) in enumerate(pairs, start=1):
        ta = id_to_title(G, a)
        tb = id_to_title(G, b)
        print(f"{i}.\t{score}\t{ta}\t{tb}")


def main():
    base = os.path.dirname(__file__)
    gpath = os.path.join(base, "dblp_filtered_graph.gpickle")
    if not os.path.exists(gpath):
        print("Graph file not found at", gpath)
        return

    print("Loading graph from:", gpath)
    G = load_graph(gpath)
    n = G.number_of_nodes()
    m = G.number_of_edges()
    print(f"Graph loaded: {n} nodes, {m} edges")

    # Compute co-citation
    print("Computing co-citation counts...")
    cocounts = compute_co_citation(G)
    top_coc = top_k_from_counter(cocounts, 10)
    # print_top("Top-10 Similar Papers based on Co-citation Score", top_coc, G)
    # save the results to a file
    output_path = os.path.join(base, "results_ex2/top_co_citation.txt")
    print(f"Saving co-citation results to: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("S.No.\tScore\tTitle A\tTitle B\n")
        for i, ((a, b), score) in enumerate(top_coc, start=1):
            ta = id_to_title(G, a)
            tb = id_to_title(G, b)
            f.write(f"{i}.\t{score}\t{ta}\t{tb}\n")
    print("Co-citation results saved successfully.")

    # Compute bibliographic coupling
    print("Computing bibliographic coupling counts...")
    bibcounts = compute_bibliographic_coupling(G)
    top_bib = top_k_from_counter(bibcounts, 10)
    # print_top("Top-10 Similar Papers based on Bibliographic Coupling Score", top_bib, G)
    output_path = os.path.join(base, "results_ex2/top_bibliographic_coupling.txt")
    print(f"Saving bibliographic coupling results to: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("S.No.\tScore\tTitle A\tTitle B\n")
        for i, ((a, b), score) in enumerate(top_bib, start=1):
            ta = id_to_title(G, a)
            tb = id_to_title(G, b)
            f.write(f"{i}.\t{score}\t{ta}\t{tb}\n")
    print("Bibliographic coupling results saved successfully.")

if __name__ == "__main__":
    main()
