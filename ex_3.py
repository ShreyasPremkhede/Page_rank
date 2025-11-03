import os
import pickle
import networkx as nx
import numpy as np
from scipy.stats import pearsonr
import pandas as pd

def analyze_pagerank_correlations(graph_file, k=50, alpha_values=np.arange(0.15, 1.0, 0.10)):
    """
    PageRank with different damping factors, compute correlations with citation counts,
    Return top-10 papers for best worst correlation values
    """
    
    # Loadng the graph
    with open(graph_file, 'rb') as f:
        G = pickle.load(f)
    print(f"Graph loaded: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")
    print()

    # in-degree for the citations of the different nodes
    citation_counts = dict(G.in_degree())

    correlation_results = {}
    pagerank_results = {}

    # Going through different alpha values
    for alpha in alpha_values:
        pr = nx.pagerank(G, alpha=alpha)
        pagerank_results[alpha] = pr

        top_k = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:k]

        pr_values = [score for _, score in top_k]
        
        # obtaining the citation counts for the different nodes
        citation_values = [citation_counts.get(node, 0) for node, _ in top_k]

        corr, _ = pearsonr(pr_values, citation_values)
        correlation_results[alpha] = corr

    # Saving as df
    correlation_df = pd.DataFrame({
        'Damping Factor': list(correlation_results.keys()),
        'Pearson Correlation': list(correlation_results.values())
    }).round(5)
    print("Correlation Values for Different Damping Factors")
    print(correlation_df.to_string(index=False))

    b_alpha = max(correlation_results, key=correlation_results.get)
    w_alpha = min(correlation_results, key=correlation_results.get)

    print()
    print(f"Best correlation for damping factor = {b_alpha:.2f} ({correlation_results[b_alpha]:.4f})")
    print(f"Worst correlation for damping factor = {w_alpha:.2f} ({correlation_results[w_alpha]:.4f})")
    print()

    # To get the top papers for a given alpha, return df
    def top_papers(alpha, n=10):
        pr = pagerank_results[alpha]
        top_nodes = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:n]
        data = []
        for node, score in top_nodes:
            title = G.nodes[node].get('title', 'Unknown Title')
            data.append({'Title': title, 'PageRank Score': score})
        return pd.DataFrame(data)

    # Saving, Printing
    results_dir = "results_ex3"
    os.makedirs(results_dir, exist_ok=True)

    corr_path = os.path.join(results_dir, "correlation_values.csv")
    correlation_df.to_csv(corr_path, index=False)

    print()
    print("Top 10 Papers (Best Correlation)")
    top_best_df = top_papers(b_alpha)
    print(top_best_df.to_string(index=False))
    top_best_path = os.path.join(results_dir, f"top10_best_alpha_{b_alpha:.2f}.csv")
    top_best_df.to_csv(top_best_path, index=False)

    print()
    print("Top 10 Papers (Worst Correlation)")
    top_worst_df = top_papers(w_alpha)
    print(top_worst_df.to_string(index=False))
    top_worst_path = os.path.join(results_dir, f"top10_worst_alpha_{w_alpha:.2f}.csv")
    top_worst_df.to_csv(top_worst_path, index=False)

    return correlation_df, top_best_df, top_worst_df

correlation_df, top_best_df, top_worst_df = analyze_pagerank_correlations('dblp_filtered_graph.gpickle', k=50)
