import argparse
import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def parse_alignment_csv(csv_path):
    df = pd.read_csv(csv_path)
    df['frequency'] = df['num_predictions'].apply(lambda x: int(x.split('/')[0]))  # Extract frequency
    return df

def load_network_nodes(edge_list_path):
    nodes = set()
    with open(edge_list_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split()
            nodes.add(parts[0])
    return sorted(nodes, key=lambda x: int(''.join(filter(str.isdigit, x)) or 0))

def construct_alignment_matrix(df, source_nodes, target_nodes):
    matrix = np.zeros((len(source_nodes), len(target_nodes)))
    seed_matrix = np.zeros((len(source_nodes), len(target_nodes)), dtype=bool)

    source_index = {node: idx for idx, node in enumerate(source_nodes)}
    target_index = {node: idx for idx, node in enumerate(target_nodes)}

    for _, row in df.iterrows():
        s, t, freq = row['source_node'], row['target_node'], row['frequency']
        if s in source_index and t in target_index:
            i, j = source_index[s], target_index[t]
            matrix[i, j] = freq
            seed_matrix[i, j] = row['is_seed']

    return matrix, seed_matrix

def extract_network_name(filepath):
    """Extracts the base filename without extension as network name."""
    return os.path.splitext(os.path.basename(filepath))[0]

def plot_alignment_matrix(matrix, seed_matrix, source_nodes, target_nodes, source_net, target_net, mode="minimal", output_path=None):
    max_freq = matrix.max() if matrix.max() > 0 else 1
    norm_matrix = matrix / max_freq

    green_cmap = sns.light_palette("green", as_cmap=True)
    fig_size = (max(8, len(target_nodes) * 0.2), max(8, len(source_nodes) * 0.2))
    plt.figure(figsize=fig_size)
    
    ax = sns.heatmap(norm_matrix, cmap=green_cmap, cbar=False, linewidths=0.5, linecolor="white")

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if seed_matrix[i, j]:
                ax.add_patch(plt.Rectangle((j, i), 1, 1, color="red", lw=0))

    if mode == "minimal":
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_xlabel("")
        ax.set_ylabel("")
        plt.axis("off")
    elif mode == "full":
        ax.set_title(f"{source_net} vs {target_net} Alignment Matrix", fontsize=14, fontweight="bold")
        ax.set_xticks(np.arange(len(target_nodes)) + 0.5)
        ax.set_yticks(np.arange(len(source_nodes)) + 0.5)
        ax.set_xticklabels(target_nodes, rotation=90, fontsize=8)
        ax.set_yticklabels(source_nodes, fontsize=8)
        ax.set_xlabel(f"{target_net} Nodes")
        ax.set_ylabel(f"{source_net} Nodes")

    if output_path:
        plt.savefig(output_path, bbox_inches="tight", pad_inches=0, dpi=300)
        print(f"Plot saved to {output_path}")

    plt.show()

def get_output_filename(alignment_file, output_dir, mode):
    base_name = os.path.splitext(os.path.basename(alignment_file))[0]
    filename = f"{base_name}_{mode}.png"
    return os.path.join(output_dir, filename)

def main():
    parser = argparse.ArgumentParser(description="Plot network alignment matrix with minimal or full view.")
    parser.add_argument("--alignment_file", "-a", required=True, help="Path to the alignment CSV file.")
    parser.add_argument("--source_edge_list", "-s", required=True, help="Path to the source network edge list file.")
    parser.add_argument("--target_edge_list", "-t", required=True, help="Path to the target network edge list file.")
    parser.add_argument("--output_dir", "-o", required=True, help="Directory to save the output plot.")
    parser.add_argument("--mode", "-m", choices=["minimal", "full"], default="minimal",
                        help="Choose visualization mode: 'minimal' (no labels) or 'full' (with labels and title).")
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    output_plot_path = get_output_filename(args.alignment_file, args.output_dir, args.mode)

    df_alignments = parse_alignment_csv(args.alignment_file)
    source_nodes = load_network_nodes(args.source_edge_list)
    target_nodes = load_network_nodes(args.target_edge_list)

    source_net_name = extract_network_name(args.source_edge_list)
    target_net_name = extract_network_name(args.target_edge_list)

    alignment_matrix, seed_matrix = construct_alignment_matrix(df_alignments, source_nodes, target_nodes)

    plot_alignment_matrix(alignment_matrix, seed_matrix, source_nodes, target_nodes, source_net_name, target_net_name, mode=args.mode, output_path=output_plot_path)

if __name__ == "__main__":
    main()
