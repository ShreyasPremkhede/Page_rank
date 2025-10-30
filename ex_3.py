import os
import pickle
import networkx as nx
import numpy as np
from scipy.stats import pearsonr
import pandas as pd

def analyze_pagerank_correlations(graph_file, k=50, alpha_values=np.arange(0.15, 1.0, 0.10)):
    """
    Apply PageRank with varying damping factors, compute correlations with citation counts,
    and report top-10 papers for best and worst correlation values.
    Results are also saved to results_ex3/ folder.
    """
    # Load the graph
    with open(graph_file, 'rb') as f:
        G = pickle.load(f)
    print(f"Graph loaded: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

    # Compute in-degree (citation count) for each node
    citation_counts = dict(G.in_degree())

    correlation_results = {}
    pagerank_results = {}

    # Loop through damping factors
    for alpha in alpha_values:
        pr = nx.pagerank(G, alpha=alpha)
        pagerank_results[alpha] = pr

        # Sort by PageRank
        top_k = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:k]

        # Extract corresponding citation counts
        pr_values = [score for _, score in top_k]
        citation_values = [citation_counts.get(node, 0) for node, _ in top_k]

        # Compute Pearson correlation
        corr, _ = pearsonr(pr_values, citation_values)
        correlation_results[alpha] = corr

    # Convert to DataFrame
    correlation_df = pd.DataFrame({
        'Damping Factor (α)': list(correlation_results.keys()),
        'Pearson Correlation': list(correlation_results.values())
    })
    print("\n=== Correlation Values for Different Damping Factors ===")
    print(correlation_df.to_string(index=False))

    # Identify best and worst correlation alphas
    best_alpha = max(correlation_results, key=correlation_results.get)
    worst_alpha = min(correlation_results, key=correlation_results.get)

    print(f"\nBest correlation at α = {best_alpha:.2f} ({correlation_results[best_alpha]:.4f})")
    print(f"Worst correlation at α = {worst_alpha:.2f} ({correlation_results[worst_alpha]:.4f})")

    # Helper to get top-10 papers
    def top_papers(alpha, n=10):
        pr = pagerank_results[alpha]
        top_nodes = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:n]
        data = []
        for node, score in top_nodes:
            title = G.nodes[node].get('title', 'Unknown Title')
            data.append({'Title': title, 'PageRank Score': score})
        return pd.DataFrame(data)

    # Create results directory
    results_dir = "results_ex3"
    os.makedirs(results_dir, exist_ok=True)

    # Save correlation dataframe
    corr_path = os.path.join(results_dir, "correlation_values.csv")
    correlation_df.to_csv(corr_path, index=False)

    # Top 10 for best correlation
    print("\n=== Top 10 Papers (Best Correlation) ===")
    top_best_df = top_papers(best_alpha)
    print(top_best_df.to_string(index=False))
    top_best_path = os.path.join(results_dir, f"top10_best_alpha_{best_alpha:.2f}.csv")
    top_best_df.to_csv(top_best_path, index=False)

    # Top 10 for worst correlation
    print("\n=== Top 10 Papers (Worst Correlation) ===")
    top_worst_df = top_papers(worst_alpha)
    print(top_worst_df.to_string(index=False))
    top_worst_path = os.path.join(results_dir, f"top10_worst_alpha_{worst_alpha:.2f}.csv")
    top_worst_df.to_csv(top_worst_path, index=False)

    return correlation_df, top_best_df, top_worst_df

correlation_df, top_best_df, top_worst_df = analyze_pagerank_correlations('dblp_filtered_graph.gpickle', k=50)
