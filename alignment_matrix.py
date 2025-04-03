import argparse
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def parse_alignment_csv(csv_path):
    """
    Parse the alignment CSV file.
    
    Expected columns:
      - source_node: node id from the source network
      - target_node: node id from the target network
      - num_predictions: string like "X/100" where X is the alignment frequency
      - is_seed: boolean indicating if the alignment is a seed alignment
    
    Returns a DataFrame with an extra column 'frequency' (integer).
    """
    df = pd.read_csv(csv_path)
    df['frequency'] = df['num_predictions'].apply(lambda x: int(x.split('/')[0]))  # Extract frequency
    return df

def load_network_nodes(edge_list_path):
    """
    Load an edge list file and extract unique node identifiers.
    Assumes the edge list file is whitespace-separated.
    
    Returns a sorted list of unique nodes.
    """
    nodes = set()
    with open(edge_list_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split()
            nodes.add(parts[0])
    return sorted(nodes, key=lambda x: int(''.join(filter(str.isdigit, x)) or 0))

def construct_alignment_matrix(df, source_nodes, target_nodes):
    """
    Construct a matrix (2D numpy array) where rows correspond to source nodes and
    columns correspond to target nodes. Each cell contains the alignment frequency.
    
    Unlike previous versions, this does NOT sum the frequencies but instead plots each instance.
    
    Also creates a corresponding matrix for seed status.
    """
    matrix = np.zeros((len(source_nodes), len(target_nodes)))
    seed_matrix = np.zeros((len(source_nodes), len(target_nodes)), dtype=bool)
    
    source_index = {node: idx for idx, node in enumerate(source_nodes)}
    target_index = {node: idx for idx, node in enumerate(target_nodes)}
    
    for _, row in df.iterrows():
        s, t, freq = row['source_node'], row['target_node'], row['frequency']
        if s in source_index and t in target_index:
            i, j = source_index[s], target_index[t]
            matrix[i, j] = freq  # Keep each instance separately
            seed_matrix[i, j] = row['is_seed']
    
    return matrix, seed_matrix

def plot_alignment_matrix(matrix, seed_matrix, source_nodes, target_nodes, output_path=None):
    """
    Plot the alignment matrix:
    
    - Each alignment occurrence is plotted without aggregation.
    - Seed alignments are red.
    - Other alignments are shades of green, with intensity based on frequency.
    - Cell contours are drawn.
    
    If output_path is provided, the plot is saved to that location.
    """
    fig, ax = plt.subplots(figsize=(max(6, len(target_nodes)*0.5), max(6, len(source_nodes)*0.5)))
    
    nrows, ncols = matrix.shape
    max_freq = matrix.max() if matrix.max() > 0 else 1  # Avoid division by zero
    
    # Define a visually appealing green scale (from light green to bright green)
    min_green = np.array([0.8, 1.0, 0.8])  # Light green
    max_green = np.array([0.0, 0.8, 0.0])  # Bright green

    # Draw grid cells
    for i in range(nrows):
        for j in range(ncols):
            freq = matrix[i, j]
            if freq == 0:
                rect = patches.Rectangle((j, nrows - 1 - i), 1, 1, facecolor='white', edgecolor='black')
                ax.add_patch(rect)
                continue
            if seed_matrix[i, j]:
                color = (1, 0, 0)  # Red for seeds
            else:
                green_ratio = freq / max_freq
                color = tuple(min_green * (1 - green_ratio) + max_green * green_ratio)  # Interpolated green
            
            # Draw the cell
            rect = patches.Rectangle((j, nrows - 1 - i), 1, 1, facecolor=color, edgecolor='black')
            ax.add_patch(rect)
    
    # Configure axis ticks and labels
    ax.set_xlim(0, ncols)
    ax.set_ylim(0, nrows)
    ax.set_xticks(np.arange(ncols) + 0.5)
    ax.set_yticks(np.arange(nrows) + 0.5)
    ax.set_xticklabels(target_nodes, rotation=90, fontsize=8)
    ax.set_yticklabels(source_nodes, fontsize=8)
    
    # Add a legend manually
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='s', color='w', label='Seed Alignment', markerfacecolor='red', markersize=10, markeredgecolor='black'),
        Line2D([0], [0], marker='s', color='w', label='Predicted Alignment', markerfacecolor=(0, 0.8, 0), markersize=10, markeredgecolor='black')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    ax.set_title("Alignment Matrix: Seed (Red) vs Predicted (Green Gradient)")
    ax.set_xlabel("Target Network Nodes")
    ax.set_ylabel("Source Network Nodes")
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
        print(f"Plot saved to {output_path}")
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Plot network alignment matrix without frequency aggregation.")
    parser.add_argument("--alignment_file", "-a", required=True, help="Path to the alignment CSV file.")
    parser.add_argument("--source_edge_list", "-s", required=True, help="Path to the source network edge list file.")
    parser.add_argument("--target_edge_list", "-t", required=True, help="Path to the target network edge list file.")
    parser.add_argument("--output_dir", "-o", required=True, help="Directory to save the output plot.")
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    output_plot_path = os.path.join(args.output_dir, "alignment_matrix.png")
    
    df_alignments = parse_alignment_csv(args.alignment_file)
    source_nodes = load_network_nodes(args.source_edge_list)
    target_nodes = load_network_nodes(args.target_edge_list)
    
    alignment_matrix, seed_matrix = construct_alignment_matrix(df_alignments, source_nodes, target_nodes)
    
    plot_alignment_matrix(alignment_matrix, seed_matrix, source_nodes, target_nodes, output_path=output_plot_path)

if __name__ == "__main__":
    main()
