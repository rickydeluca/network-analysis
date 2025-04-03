import networkx as nx
import matplotlib.pyplot as plt
import argparse
import os
import matplotlib.cm as cm

# Ensure text is rendered as plain text (so underscores remain unchanged)
plt.rcParams['text.usetex'] = False

def read_edgelist(path):
    """
    Read a file storing the network information in edge list format
    and return the corresponding NetworkX graph with nodes.
    """
    with open(path, 'r') as file:
        first_line = file.readline().strip().split()
        if len(first_line) == 2:
            G = nx.read_edgelist(path)  # Do not enforce int conversion to allow underscores in names.
        elif len(first_line) == 3:
            G = nx.read_weighted_edgelist(path)  # Same here.
        else:
            raise ValueError("Unknown file format.")
    return G

def build_union_graph(G1, G2):
    """
    Build a union graph containing all nodes from G1 and G2.
    Edges from both networks are added for layout purposes.
    """
    union_nodes = set(G1.nodes()).union(set(G2.nodes()))
    union_graph = nx.Graph()
    union_graph.add_nodes_from(union_nodes)
    union_graph.add_edges_from(G1.edges())
    union_graph.add_edges_from(G2.edges())
    return union_graph

def compute_global_layout(G_union, seed=42):
    """
    Compute a global layout for the union of nodes,
    ensuring that nodes with the same name have the same position.
    """
    pos = nx.spring_layout(G_union, seed=seed)
    return pos

def compute_max_degree_diff(G1, G2):
    """
    Compute the maximum absolute difference in degree among nodes
    that are present in both networks.
    """
    common_nodes = set(G1.nodes()).intersection(set(G2.nodes()))
    if not common_nodes:
        return 1  # Avoid division by zero.
    max_diff = max(abs(G1.degree(n) - G2.degree(n)) for n in common_nodes)
    return max_diff if max_diff > 0 else 1

def get_node_color(node, current_graph, other_graph, max_diff, cmap, 
                   default_color='lightblue', unique_color='purple', missing_color='lightgray'):
    """
    Determine the color for a node in the given network subplot.
    
    - If the node is present in current_graph:
        - If it is unique (not present in the other graph), return unique_color (purple).
        - Otherwise, if the degree difference is zero, return default_color (lightblue).
        - Else, compute the normalized degree difference and return a color
          from the colormap (yellow for low difference, red for high difference).
    - If the node is absent from current_graph, return missing_color.
    """
    if node in current_graph:
        if node not in other_graph:
            return unique_color
        diff = abs(current_graph.degree(node) - other_graph.degree(node))
        if diff == 0:
            return default_color
        normalized = diff / max_diff  # Normalize between 0 and 1.
        return cmap(normalized)
    else:
        return missing_color

def compare_and_plot(G1, G2, pos, output_path, name1, name2):
    """
    Create a side-by-side comparison plot of the two networks using a fixed layout.
    
    For each subplot:
      - Nodes present in the network are colored based on degree differences if
        they are present in both networks (yellow=low difference, red=high difference).
      - Nodes unique to the network (present in one but not the other) are colored purple.
      - Nodes absent in the network are drawn in light gray.
    
    Each subplot is titled with the corresponding network file name (without extension).
    """
    union_nodes = set(pos.keys())
    
    # Define a colormap for degree differences.
    cmap = cm.get_cmap("YlOrRd")
    max_diff = compute_max_degree_diff(G1, G2)
    
    fig, axs = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot for Network 1.
    ax = axs[0]
    ax.set_title(name1)
    G1_edges = [(u, v) for u, v in G1.edges() if u in pos and v in pos]
    nx.draw_networkx_edges(G1, pos, edgelist=G1_edges, ax=ax, edge_color='gray')
    node_colors_G1 = [get_node_color(node, G1, G2, max_diff, cmap) for node in union_nodes]
    nx.draw_networkx_nodes(G1, pos, nodelist=list(union_nodes), node_color=node_colors_G1, ax=ax, node_size=500)
    # Use the original node names (underscores maintained)
    nx.draw_networkx_labels(G1, pos, labels={node: node for node in union_nodes}, ax=ax, font_size=10)
    
    # Plot for Network 2.
    ax = axs[1]
    ax.set_title(name2)
    G2_edges = [(u, v) for u, v in G2.edges() if u in pos and v in pos]
    nx.draw_networkx_edges(G2, pos, edgelist=G2_edges, ax=ax, edge_color='gray')
    node_colors_G2 = [get_node_color(node, G2, G1, max_diff, cmap) for node in union_nodes]
    nx.draw_networkx_nodes(G2, pos, nodelist=list(union_nodes), node_color=node_colors_G2, ax=ax, node_size=500)
    nx.draw_networkx_labels(G2, pos, labels={node: node for node in union_nodes}, ax=ax, font_size=10)
    
    for ax in axs:
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def main():
    """
    Parse command-line arguments, compare the two networks,
    and produce a side-by-side comparison plot.
    
    The output file name is automatically generated as: name1_name2.png
    (keeping underscores from the network file names).
    """
    parser = argparse.ArgumentParser(
        description="Compare two edgelist networks, highlighting differences in node presence and degree."
    )
    parser.add_argument("network1", type=str, help="Path to the first network edgelist file.")
    parser.add_argument("network2", type=str, help="Path to the second network edgelist file.")
    args = parser.parse_args()
    
    # Extract file names without extension to use as subplot titles.
    name1 = os.path.splitext(os.path.basename(args.network1))[0]
    name2 = os.path.splitext(os.path.basename(args.network2))[0]
    output_file = f"{name1}_{name2}.png"
    
    # Read the networks.
    G1 = read_edgelist(args.network1)
    G2 = read_edgelist(args.network2)
    
    # Build a union graph and compute a consistent layout.
    union_graph = build_union_graph(G1, G2)
    pos = compute_global_layout(union_graph)
    
    # Generate and save the comparison plot.
    compare_and_plot(G1, G2, pos, output_file, name1, name2)
    print(f"Comparison plot saved to {output_file}")

if __name__ == "__main__":
    main()
