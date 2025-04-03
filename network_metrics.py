import os
import csv
import networkx as nx
import argparse

def compute_metrics(input_folder, output_folder, missing_marker='-'):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Init metrics dictionary
    metrics = {
        'degree': {},
        'strength': {},
        'closeness': {},
        'betweenness': {},
        'eigenvector': {},
        'clustering': {}
    }

    # Network identifiers (from file names)
    network_ids = []

    # Accumulate unique nodes across all networks
    all_nodes = set()

    # Process each file in the directory that ends with '.txt'
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            network_id = os.path.splitext(filename)[0]  # Use file name without extension as network id
            network_ids.append(network_id)
            file_path = os.path.join(input_folder, filename)
            
            G = nx.Graph()
            
            # Read weighted edge list file
            with open(file_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) < 3:
                        continue  # Skip lines that do not contain enough data
                    node1, node2, weight = parts[0], parts[1], float(parts[2])
                    G.add_edge(node1, node2, weight=weight)
            
            # Update the set of all nodes encountered
            all_nodes.update(G.nodes())
            
            # Compute metrics for this network

            # 1. Degree: unweighted degree count
            degree_dict = dict(G.degree())
            metrics['degree'][network_id] = degree_dict
            
            # 2. Strength: sum of weights for each node
            strength_dict = dict(G.degree(weight='weight'))
            metrics['strength'][network_id] = strength_dict
            
            # 3. Closeness Centrality, no weights
            closeness_dict = nx.closeness_centrality(G)
            metrics['closeness'][network_id] = closeness_dict
            
            # 4. Betweenness Centrality: using weights
            betweenness_dict = nx.betweenness_centrality(G, weight='weight', normalized=True)
            metrics['betweenness'][network_id] = betweenness_dict
            
            # 5. Eigenvector Centrality: using weights
            try:
                eigenvector_dict = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
            except nx.PowerIterationFailedConvergence:
                eigenvector_dict = {node: missing_marker for node in G.nodes()}
            metrics['eigenvector'][network_id] = eigenvector_dict
            
            # 6. Clustering Coefficient: weighted version.
            clustering_dict = nx.clustering(G, weight='weight')
            metrics['clustering'][network_id] = clustering_dict

    # Ensure consistent ordering of network IDs across CSV files
    network_ids.sort()

    # For each metric, create a CSV file with nodes as rows and networks as columns
    for metric_name, network_data in metrics.items():
        csv_filename = os.path.join(output_folder, f"{metric_name}.csv")
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            header = ['nodes'] + network_ids
            writer.writerow(header)
            
            # Iterate through all nodes (sorted for consistency)
            for node in sorted(all_nodes):
                row = [node]
                # For each network, check if the node has a computed metric
                for network_id in network_ids:
                    value = network_data.get(network_id, {}).get(node, missing_marker)
                    row.append(value)
                writer.writerow(row)

    print(f"CSV files for degree, strength, closeness, betweenness, eigenvector, and clustering metrics have been created in the '{output_folder}' folder.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Network Metrics", 
                                     description="Compute a series of local metrics for each network in the given directory. Returns one file for each metric in the specified output folder.")
    parser.add_argument('dir', help='path/to/input/directory')
    parser.add_argument('--output', default='output', help='path/to/output/folder (default: "output").')
    parser.add_argument('--missing_marker', default='-', help='Marker for missing nodes (default: "-").')
    args = parser.parse_args()

    compute_metrics(input_folder=args.dir,
                    output_folder=args.output,
                    missing_marker=args.missing_marker)
