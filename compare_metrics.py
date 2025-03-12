import networkx as nx
import pandas as pd
import argparse
import csv
import os

from utils.read_write_networks import generate_nx_network

def read_input():
    parser = argparse.ArgumentParser(description="Compare the metrics for a set of source-target node pairs.")
    parser.add_argument('--source_net', type=str, required=True, help="Path to the source network.")
    parser.add_argument('--target_net', type=str, required=True, help="Path to the target network.")
    parser.add_argument('--node_pairs', type=str, required=True, help="Path to the list of node pairs.")
    args = parser.parse_args()
    return args

def shortest_path_between_nodes(G, node1, node2):
    """
    Compute the shortest path length between two nodes in the graph G.
    If either node is not in the graph or no path exists, return -1.
    """
    if node1 in G and node2 in G:
        try:
            return nx.shortest_path_length(G, source=node1, target=node2)
        except nx.NetworkXNoPath:
            return -1
    return -1

def compute_similarity(val_source, val_target):
    """
    Compute the similarity between two metric values. If both are None, similarity is 0.
    If one is None, similarity is also 0.
    Otherwise, use a normalized difference similarity measure.
    """
    if val_source is None or val_target is None:
        return 0
    return 1 - abs(val_source - val_target) / max(val_source, val_target, 1e-9)

def compare_metric(G_source, G_target, node_pairs, metric=None):
    source_nodes = list(node_pairs.keys())
    target_nodes = list(node_pairs.values())

    print('source_nodes:', source_nodes)
    print('target_nodes:', target_nodes)

    if metric == 'degree':
        source_metric = dict(G_source.degree())
        target_metric = dict(G_target.degree())
    elif metric == 'shortes_path':
        source_metric = {src: shortest_path_between_nodes(G_source, src, tgt) for src, tgt in node_pairs.items()}
        target_metric = {tgt: shortest_path_between_nodes(G_target, tgt, src) for src, tgt in node_pairs.items()}
    elif metric == 'closeness':
        source_metric = nx.closeness_centrality(G_source)
        target_metric = nx.closeness_centrality(G_target)
    elif metric == 'clustering':
        source_metric = nx.clustering(G_source)
        target_metric = nx.clustering(G_target)
    elif metric == 'betweenness':
        source_metric = nx.betweenness_centrality(G_source)
        target_metric = nx.betweenness_centrality(G_target)
    else:
        raise ValueError("Unsupported metric: {}".format(metric))

    rows = []

    for src, tgt in node_pairs.items():
        val_source = source_metric.get(src, None)
        val_target = target_metric.get(tgt, None)
        similarity = compute_similarity(val_source, val_target)

        rows.append({
            "source_nodes": src,
            "metric_value_source": val_source,
            "similarity_between_metrics": similarity,
            "metric_value_target": val_target,
            "target_nodes": tgt
        })

    df = pd.DataFrame(rows)
    return df

if __name__ == '__main__':
    args = read_input()

    source_name = os.path.splitext(os.path.basename(args.source_net))[0]
    target_name = os.path.splitext(os.path.basename(args.target_net))[0]

    G_source = generate_nx_network(args.source_net)
    G_target = generate_nx_network(args.target_net)

    source_target_pairs = {}
    with open(args.node_pairs, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            source = row['source_node']
            target = row['target_node']
            source_target_pairs[source] = target

    local_metrics = [
        "degree",
        "shortes_path",
        "closeness",
        "clustering",
        "betweenness",
    ]

    for metric in local_metrics:
        comparison_df = compare_metric(G_source, G_target, source_target_pairs, metric=metric)
        output_filename = f"output/compare_node_pairs/{source_name}_{target_name}_{metric}.csv"
        comparison_df.to_csv(output_filename, index=False)
        print(f"CSV file for metric '{metric}' has been generated: {output_filename}")
