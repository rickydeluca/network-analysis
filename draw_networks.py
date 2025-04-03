import networkx as nx
import matplotlib.pyplot as plt
import os
import argparse
from utils.read_write_networks import read_edgelist

def plot_and_save_graph(G, output_path):
    """
    Plot the given graph with node labels and save the figure
    to the specified output path.
    """
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G)  # Use a spring layout for clear visualization
    nx.draw(G, pos, with_labels=True, node_color='lightblue',
            edge_color='gray', node_size=500, font_size=10)
    plt.savefig(output_path)
    plt.close()

def process_networks(input_dir, output_dir):
    """
    Process each file in the input directory: read the edgelist,
    plot the corresponding graph, and save the image in the output directory.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for file in os.listdir(input_dir):
        if file.endswith('.txt') or file.endswith('.edgelist'):
            file_path = os.path.join(input_dir, file)
            try:
                G = read_edgelist(file_path)
            except Exception as e:
                print(f"Error reading {file}: {e}")
                continue

            output_file = os.path.join(output_dir, os.path.splitext(file)[0] + '.png')
            plot_and_save_graph(G, output_file)
            print(f"Saved graph image: {output_file}")

def main():
    """
    Parse command-line arguments and initiate the processing of network files.
    """
    parser = argparse.ArgumentParser(description='Process and plot edgelist networks.')
    parser.add_argument('input_dir', type=str, 
                        help='Directory containing edgelist files.')
    parser.add_argument('output_dir', type=str, 
                        help='Directory where the graph images will be saved.')
    args = parser.parse_args()
    
    process_networks(args.input_dir, args.output_dir)

if __name__ == '__main__':
    main()
