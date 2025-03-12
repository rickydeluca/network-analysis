"""Script to analyze network metrics."""

import json
import os

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from tqdm import tqdm

from utils.metrics import compute_metric
import argparse


def read_node_link_json(path):
    """
    Read a JSON file storing the network information in 
    node-link data format and return the corresponding
    NetworkX graph.
    """
    json_data = json.load(open(os.path.join(path, "G.json")))
    return nx.node_link_graph(json_data)


def read_edgelist(path):
    """
    Read a file storing the network information in
    edge list format and return the corresponding
    NetworkX graph with integer nodes.
    """
    # Read original graph.
    with open(path, 'r') as file:
        first_line = file.readline().strip().split()
        if len(first_line) == 2:
            G_original = nx.read_edgelist(path, nodetype=str)
        elif len(first_line) == 3:
            G_original = nx.read_weighted_edgelist(path, nodetype=str, delimiter=' ')
        else:
            raise ValueError("Unknown file format.")

    # Create new graph with integer nodes.
    G = nx.Graph()
    name2idx = {node: idx for idx, node in enumerate(G_original.nodes())}
    idx2name = {idx: node for node, idx in name2idx.items()}
    
    # Add nodes with original names as attributes.
    for node in G_original.nodes():
        G.add_node(name2idx[node], name=node)
    
    # Add edges using integer nodes.
    for u, v, data in G_original.edges(data=True):
        G.add_edge(name2idx[u], name2idx[v], **data)
    
    # Store the mapping as a graph attribute.
    G.graph['name2idx'] = name2idx
    G.graph['idx2name'] = idx2name
    
    return G


def global_metrics(G, metrics=None):
    """
    Compute the global metrics of the network G and return 
    them as a list.
    """
    result = []
    for metric in metrics:
        result.append(compute_metric(G, metric))
    
    return result


def plot_distribution(df, column, outfile=None, label_ticks=25):
    unique_values = df[column].unique()

    """Plot the histogram of the specified column."""
    plt.figure(figsize=(10, 6))
    df[column].value_counts().sort_index().plot(kind='bar', color='skyblue')
    plt.title(f'Distribution of {column}')
    plt.xlabel(column)
    plt.ylabel('Frequency')

    # Set x-axis ticks and labels for better readability.
    if label_ticks is not None and len(unique_values) > label_ticks:
        # Display labels for a subset of ticks.
        tick_positions = range(0, len(unique_values), len(unique_values) // label_ticks)
        tick_labels = [str(unique_values[i]) for i in tick_positions]
        plt.xticks(tick_positions, tick_labels)

    if outfile:
        plt.savefig(outfile)
    else:
        plt.show()


def analyze_networks(data_dir, outdir, compute_global=True, compute_local=True, plot=False):
    """
    Analyze global and local metrics of the network in `path`.
    The network must be provided in node-link data format.
    The results of the analysis will be stored in `outdir`.
    """

    # Get all networks in the data directory.
    networks = [net for net in os.listdir(data_dir)]
    print(f"\nNetworks to analyze: {networks}\n")

    # --- Global Metrics ---
    if compute_global:
                
        global_metrics = [
            "num_nodes",
            "num_edges",
            "avg_degree",
            # "longest_shortest_path",
            "avg_shortest_path",
            "radius",
            "diameter",
            "node_connectivity",
            "edge_connectivity",
            "avg_closeness_centrality",
            "avg_betweenness_centrality",
            "avg_degree_centrality",
            # "avg_pagerank",
            "avg_eigenvector_centrality",
            "avg_clustering",
            # "assortativity"
        ]

        global_result = {}

        for net in networks:
            # Generate network according the input data format.
            if net.endswith(".json"):
                G = read_node_link_json(f"{data_dir}/{net}")
            elif net.endswith(".edgelist") or net.endswith(".edgelist_weighted") or net.endswith(".txt"):
                G = read_edgelist(f"{data_dir}/{net}")
            else:
                raise ValueError("Unknown file format.")
            
            global_result[net] = []

            for metric in global_metrics:
                global_result[net].append(compute_metric(G, metric))

        # Export.
        if not os.path.exists(f"{outdir}"):
            os.makedirs(f"{outdir}") 
        
        df = pd.DataFrame.from_dict(
            global_result, 
            orient='index',
            columns=global_metrics
        )

        if outdir is not None:
            df.to_csv(f"{outdir}/globals.csv")
        
    # --- Local Metrics ---

    if compute_local:

        local_metrics = [
            "degree",
            "eccentricity",
            "closeness_centrality",
            "betweenness_centrality",
            "degree_centrality",
            "eigenvector_centrality",
            "clustering"
        ]

        for net in tqdm(networks, desc="Computing local metrics"):
            # Generate network according to the input data format.
            if net.endswith(".json"):
                G = read_node_link_json(f"{data_dir}/{net}")
            elif net.endswith(".edgelist") or net.endswith(".edgelist_weighted") or net.endswith(".txt"):
                G = read_edgelist(f"{data_dir}/{net}")
            else:
                raise ValueError("Unknown file format.")
        

            local_result = {}
            idx2name = G.graph['idx2name']
            
            for node in G.nodes:
                # Use original node name as key in results.
                original_name = idx2name[node]
                local_result[original_name] = []
                for metric in local_metrics:
                    # Compute metric using integer node.
                    local_result[original_name].append(compute_metric(G, metric, u=node))
                
            # Export.
            if not os.path.exists(f"{outdir}"):
                os.makedirs(f"{outdir}") 
        
            df = pd.DataFrame.from_dict(
                local_result, 
                orient='index',
                columns=local_metrics
            )

            if outdir is not None:
                net_name = os.path.splitext(net)[0]
                df.to_csv(f"{outdir}/{net_name}_locals.csv")

            if plot:
                for metric in local_metrics:
                    if net == "ppi":
                        label_ticks = 25
                    else:
                        label_ticks = None
                        
                    plot_distribution(df, column=metric, label_ticks=label_ticks, outfile=f'plots/{net}_{metric}_distribution.png')


if __name__ == '__main__':
    # Set up argument parser.
    parser = argparse.ArgumentParser(description="Analyze network metrics.")
    parser.add_argument('--data_dir', type=str, required=True, help='Directory containing network data files.')
    parser.add_argument('--outdir', type=str, default='output', help='Directory to store the output results.')
    parser.add_argument('--compute_global', action='store_true', help='Flag to compute global metrics.')
    parser.add_argument('--compute_local', action='store_true', help='Flag to compute local metrics.')
    parser.add_argument('--plot', action='store_true', help="Flag to plot the metric distributions.")

    # Parse arguments.
    args = parser.parse_args()

    # Set path names.
    DATA_DIR = args.data_dir
    OUTDIR = args.outdir

    # Compute network metrics.
    analyze_networks(DATA_DIR, 
                     OUTDIR, 
                     compute_global=args.compute_global, 
                     compute_local=args.compute_local, 
                     plot=args.plot)