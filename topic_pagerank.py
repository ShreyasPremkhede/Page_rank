import networkx as nx
import pickle

TOPICS = ["security", "hashing", "streaming", "timeseries", "search"]
DAMPING_FACTOR = 0.85

def load_graph(path="dblp_filtered_graph.gpickle"):
    with open(path, "rb") as f:
        G = pickle.load(f)
    print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
    return G

def compute_topic_sensitive_pagerank(G, topic):
    topic = topic.lower()
    topic_nodes = [n for n, data in G.nodes(data=True)
                   if data.get("title") and topic in data["title"].lower()]
    
    if not topic_nodes:
        print(f"No papers found for topic '{topic}'.")
        return None

    personalization = {n: 0 for n in G.nodes()}
    for n in topic_nodes:
        personalization[n] = 1 / len(topic_nodes)

    pr_scores = nx.pagerank(G, alpha=DAMPING_FACTOR, personalization=personalization)
    ranked = sorted(pr_scores.items(), key=lambda x: x[1], reverse=True)[:10]

    print(f"\nTop 10 papers for topic '{topic}':")
    print(f"{'Rank':<4} {'Title':<70} {'PageRank':<10} {'Citations'}")
    print("-" * 100)
    for i, (pid, score) in enumerate(ranked, 1):
        title = G.nodes[pid].get("title", "No Title")
        citations = G.in_degree(pid)
        print(f"{i:<4} {title[:68]:<70} {score:<10.6f} {citations}")
    return ranked

def main():
    G = load_graph()
    for topic in TOPICS:
        compute_topic_sensitive_pagerank(G, topic)

if __name__ == "__main__":
    main()
