import networkx as nx
import json
import os

def read_edgelist(path):
    """
    Read a file storing the network information in
    edge list format and return the corresponding
    NetworkX graph with integer nodes.
    """
    # Read original graph
    with open(path, 'r') as file:
        first_line = file.readline().strip().split()
        if len(first_line) == 2:
            G = nx.read_edgelist(path)
        elif len(first_line) == 3:
            G= nx.read_weighted_edgelist(path)
        else:
            raise ValueError("Unknown file format.")
    
    return G

def read_node_link_json(path):
    """
    Read a JSON file storing the network information in 
    node-link data format and return the corresponding
    NetworkX graph.
    """
    json_data = json.load(open(os.path.join(path, "G.json")))
    return nx.node_link_graph(json_data)


def generate_nx_network(path):
    # Generate network according the input data format
    if path.endswith(".json"):
        G = read_node_link_json(path)
    elif path.endswith(".edgelist") or path.endswith(".edgelist_weighted") or path.endswith(".txt"):
        G = read_edgelist(path)
    else:
        raise ValueError("Unknown file format.")
    
    return G