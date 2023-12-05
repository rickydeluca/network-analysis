"""Script to analyze network metrics."""

import json
import os

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from tqdm import tqdm

from utils.metrics import compute_metric


def read_node_link_json(path):
    """
    Read a JSON file storing the network information in 
    node-link data format and return the corresponding
    NetworkX graph.
    """
    json_data = json.load(open(os.path.join(path, "G.json")))
    return nx.node_link_graph(json_data)


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
        # Display labels for a subset of ticks
        tick_positions = range(0, len(unique_values), len(unique_values) // label_ticks)
        tick_labels = [str(unique_values[i]) for i in tick_positions]
        plt.xticks(tick_positions, tick_labels)

    if outfile:
        plt.savefig(outfile)
    else:
        plt.show()


def analyze_networks(data_dir, outdir, compute_global=True, compute_local=True):
    """
    Analyze global and local metrics of the network in `path`.
    The network must be provided in node-link data format.
    The results of the analysis will be stored in `outdir`.
    """

    # Get all networks.
    networks = [net for net in os.listdir(data_dir)]

    # GLOBAL METRICS
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
            "assortativity"
        ]

        global_result = {}

        for net in tqdm(networks, desc="Computing global metrics"):
            G = read_node_link_json(f"{data_dir}/{net}")
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
            df.to_csv(f"{outdir}/global_metrics.csv")
        
    # LOCAL METRICS
    if compute_local:
        local_metrics = [
            "degree",
            # "eccentricity",
            # "closeness_centrality",
            # "betweenness_centrality",
            # "degree_centrality",
            # "eigenvector_centrality",
            # "clustering"
        ]

        for net in tqdm(networks, desc="Computing local metrics"):
            G = read_node_link_json(f"{data_dir}/{net}")
            local_result = {}
            for node in G.nodes:
                local_result[node] = []
                for metric in local_metrics:
                    local_result[node].append(compute_metric(G, metric, u=node))
                
            # Export.
            if not os.path.exists(f"{outdir}"):
                os.makedirs(f"{outdir}") 
        
            df = pd.DataFrame.from_dict(
                local_result, 
                orient='index',
                columns=local_metrics
            )

            if outdir is not None:
                df.to_csv(f"{outdir}/local_metrics_{net}.csv")

            for metric in local_metrics:
                if net == "ppi":
                    label_ticks = 25
                else:
                    label_ticks = None
                    
                plot_distribution(df, column=metric, label_ticks=label_ticks, outfile=f'plots/{net}_{metric}_distribution_plot.png')


if __name__ == '__main__':
    # Set path names.
    DATA_DIR = "networks/"
    OUTDIR = "results/"

    # Compute network metrics.
    analyze_networks(DATA_DIR, OUTDIR, compute_global=True)