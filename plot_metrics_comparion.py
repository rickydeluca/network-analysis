import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

from utils.read_write_networks import read_edgelist

def get_network_name(file_path):
    """
    Get network name from its file path.
    """
    return os.path.splitext(os.path.basename(file_path))[0]


def compute_metrics(G):
    """
    Compute some local metrics of the graph G.
    """
    metrics = {
        "Degree": dict(G.degree(weight="weight")),
        "Closeness": nx.closeness_centrality(G),
        "Betweenness": nx.betweenness_centrality(G, weight="weight"),
        "Eigenvector": nx.eigenvector_centrality(G, weight="weight", max_iter=1000),
        "Katz": nx.katz_centrality(G, weight="weight", alpha=0.1, beta=1.0, max_iter=1000),
        "Clustering": nx.clustering(G, weight="weight")
    }
    return metrics


def plot_and_save_metrics(metrics1, metrics2, network_names, output_dir):
    """
    Plot local metric distributions of the network pair with network names as column titles.
    """
    measures = list(metrics1.keys())
    num_measures = len(measures)

    fig, axes = plt.subplots(num_measures, 2, figsize=(12, 3 * num_measures))
    fig.suptitle("Centrality & Clustering Distributions", fontsize=16, fontweight="bold")

    # Add column titles (network names)
    for j, name in enumerate(network_names):
        axes[0, j].set_title(name, fontsize=14, fontweight="bold")

    for i, measure in enumerate(measures):
        values1 = list(metrics1[measure].values())
        values2 = list(metrics2[measure].values())

        # Log transform for better visualization of skewed distributions
        if measure in ["Betweenness", "Katz"]:
            values1 = np.log1p(values1)
            values2 = np.log1p(values2)
            measure_title = f"{measure} (log)"
        else:
            measure_title = measure

        # First network plot
        sns.histplot(values1, bins=30, kde=True, ax=axes[i, 0], color="blue")
        axes[i, 0].set_xlabel(measure_title)
        axes[i, 0].set_ylabel("Frequency")

        # Second network plot
        sns.histplot(values2, bins=30, kde=True, ax=axes[i, 1], color="red")
        axes[i, 1].set_xlabel(measure_title)
        axes[i, 1].set_ylabel("Frequency")

    # Adjust layout and save plot
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    output_file = os.path.join(output_dir, f"{network_names[0]}_vs_{network_names[1]}_metrics.png")
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f"Plot saved as: {output_file}")


if __name__ == "__main__":
    # Replace with actual filenames
    file1 = "data/edi3/edgelist/age1.txt"
    file2 = "data/edi3/edgelist/age4.txt"

    # Output directory
    output_dir = "plots/net_comparison"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get networks
    name1 = get_network_name(file1)
    name2 = get_network_name(file2)

    G1 = read_edgelist(file1)
    G2 = read_edgelist(file2)

    # Compute centralities and clustering
    metrics1 = compute_metrics(G1)
    metrics2 = compute_metrics(G2)

    # Plot and save distributions
    plot_and_save_metrics(metrics1, metrics2, [name1, name2], output_dir)
