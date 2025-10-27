import os
import json
import networkx as nx
from collections import deque
import pickle

MIN_CITATIONS = 60
START_YEAR = 2010
END_YEAR = 2015

def build_citation_graph(data_directory, min_citations, start_year, end_year):
    qualified_papers = {}
    json_files_to_process = [os.path.join(data_directory, f) for f in 
                             ["dblp-ref-0.json", "dblp-ref-1.json", "dblp-ref-2.json", "dblp-ref-3.json"]]

    for f_path in json_files_to_process:
        if not os.path.exists(f_path):
            print(f"Error: Data file '{f_path}' not found.")
            print(f"Please check the path in the DATA_DIR variable.")
            return None

    print(f"\nIdentifying qualified papers and titles:")
    print(f"Criteria: >= {min_citations} citations and year between {start_year}-{end_year}")
    
    total_line_count = 0
    for json_file in json_files_to_process:
        print(f"Processing file: {os.path.basename(json_file)}")
        e = 0
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                for line in f:
                    total_line_count += 1
                    try:
                        if not line.strip():
                            continue
                        paper = json.loads(line)
                        n_citation = paper.get("n_citation", 0)
                        year = paper.get("year", 0)
                        paper_id = paper.get("id")
                        
                        if (paper_id and
                            n_citation >= min_citations and
                            start_year <= year <= end_year):
                            qualified_papers[paper_id] = paper.get("title", "No Title Available")
                            
                    except json.JSONDecodeError:
                        print(f"\nWarning: Skipping malformed JSON line {total_line_count}")
                        e = 1
                if e == 0:
                    print(f"Scanned {total_line_count:,} papers, found {len(qualified_papers):,} qualified")
                else:
                    print(f"Scanned {total_line_count:,} papers with some errors, found {len(qualified_papers):,} qualified")
        except Exception as e:
            print(f"\nAn error occurred during identifying qualified papers on {json_file}: {e}")
            return None

    if not qualified_papers:
        print("\nNo papers matched the criteria.")
        return None

    print(f"\nFound {len(qualified_papers):,} qualified papers out of {total_line_count:,} total papers.")

    print("\nBuilding graph:")
    G = nx.DiGraph()
    
    # Add all qualified papers as nodes first, with their title attribute
    for paper_id, title in qualified_papers.items():
        G.add_node(paper_id, title=title)
    
    total_line_count = 0
    edge_count = 0
    for json_file in json_files_to_process:
        print(f"Processing file: {os.path.basename(json_file)}")
        e = 0
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                for line in f:
                    total_line_count += 1
                    
                    
                    try:
                        if not line.strip():
                            continue
                        paper = json.loads(line)
                        source_id = paper.get("id")
                        
                        if source_id in qualified_papers:
                            references = paper.get("references", [])
                            for target_id in references:
                                if target_id in qualified_papers:
                                    G.add_edge(source_id, target_id)
                                    edge_count += 1
                    except json.JSONDecodeError:
                        e = 1
                        pass
                if e == 0:
                    print(f"Scanned {total_line_count:,} papers, added {edge_count:,} edges.", end='\n')
                else:
                    print(f"Scanned {total_line_count:,} papers with some errors, added {edge_count:,} edges", end='\n')
        except Exception as e:
            print(f"\nAn error occurred during Pass 2 on {json_file}: {e}")
            return None

    print(f"\nGraph built with {G.number_of_nodes():,} nodes and {G.number_of_edges():,} edges.")
    return G

def report_statistics(G):
    if G is None or G.number_of_nodes() == 0:
        print("Graph is empty. No statistics to report.")
        return

    print("\nGraph Statistics Report ")
    
    num_nodes = G.number_of_nodes()
    print(f"Number of vertices (nodes): {num_nodes:,}")
    num_edges = G.number_of_edges()
    print(f"Number of edges (citations): {num_edges:,}")
    wcc_generator = nx.weakly_connected_components(G)
    wcc_list = list(wcc_generator)
    num_wcc = len(wcc_list)
    print(f"Number of weakly connected components (WCC): {num_wcc:,}")
    scc_generator = nx.strongly_connected_components(G)
    scc_list = list(scc_generator)
    num_scc = len(scc_list)
    print(f"Number of strongly connected components (SCC): {num_scc:,}")

    if num_wcc > 0:
        largest_wcc_nodes = max(wcc_list, key=len)
        num_nodes_largest_wcc = len(largest_wcc_nodes)
        print(f"Number of nodes in largest WCC: {num_nodes_largest_wcc:,}")
        largest_wcc_graph = G.subgraph(largest_wcc_nodes)
        num_edges_largest_wcc = largest_wcc_graph.number_of_edges()
        print(f"Number of edges in largest WCC: {num_edges_largest_wcc:,}")
    else:
        print("Number of nodes in largest WCC: 0")
        print("Number of edges in largest WCC: 0")

    if num_scc > 0:
        largest_scc_nodes = max(scc_list, key=len)
        num_nodes_largest_scc = len(largest_scc_nodes)
        print(f"Number of nodes in largest SCC: {num_nodes_largest_scc:,}")

        # 8. Number of edges in largest SCC
        largest_scc_graph = G.subgraph(largest_scc_nodes)
        num_edges_largest_scc = largest_scc_graph.number_of_edges()
        print(f"Number of edges in largest SCC: {num_edges_largest_scc:,}")
    else:
        print("Number of nodes in largest SCC: 0")
        print("Number of edges in largest SCC: 0")



def main():
    DATA_DIR = "./dblp.v10/dblp-ref"
    
    graph_file = "dblp_filtered_graph.gpickle"
    
    if os.path.exists(graph_file):
        print(f"Found existing graph file '{graph_file}'. Loading it")
        
        with open(graph_file, 'rb') as f:
            G = pickle.load(f) 
            
        print(f"Graph loaded: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges.")
    else:
        print(f"Graph file '{graph_file}' not found. Hence building graph from scratch.")
        
        G = build_citation_graph(
            DATA_DIR, 
            MIN_CITATIONS, 
            START_YEAR, 
            END_YEAR
        )
    
        if G:
            with open(graph_file, 'wb') as f:
                pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)
            print(f"Graph saved at {graph_file}")
        else:
            print("Graph building failed. Exiting")
            return
    if G:
        report_statistics(G)

if __name__ == "__main__":
    main()