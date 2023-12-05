"""Script to generate the networks from the raw CSV and RData."""

import json
import os

import networkx as nx
import pandas as pd
import pyreadr


def read_csv_matrix(filepath):
    """Read CSV file representig a matrix."""
    df = pd.read_csv(filepath, index_col=0, header=0)
    return df


def get_id2idx(dict):
    """
    Construct the dictionary mapping the node names (IDs) to the node indices.
    """
    id2idx = {}
    for idx, node in enumerate(dict['nodes']):
        id2idx[node['id']] = idx
        
    return id2idx


def generate_network(path, outdir):
    """
    Given the path of a CSV or an RData file, read it and generate the 
    corresponding network. The generated network will be saved in `outdir`
    folder using the node-link data format.

    Args:
        path: path for the row data.
        outdir: path where to store the generated networks
    
    Return:
        None
    """

    # Check if CSV or RData.
    filename, ext = path.split('.')
    _, filename = filename.split('/')
    if ext == "csv":
        df = read_csv_matrix(path)
    elif ext == "Rdata" or ext == "RData":
        result = pyreadr.read_r(path)
        key = list(result.keys())[0]
        df = result[key]
    else:
        raise FileNotFoundError("The input file has not valid extension.")
    
    # Get network.
    G = nx.from_pandas_adjacency(df)
    
    # Generate JSON node-link data format.
    json_data = nx.node_link_data(G)
    id2idx = get_id2idx(json_data)

    # Export.
    if not os.path.exists(f"{outdir}/{filename}"):
        os.makedirs(f"{outdir}/{filename}") 

    json_filepath = f"{outdir}/{filename}/G.json"
    id2idx_filepath = f"{outdir}/{filename}/id2idx.json"

    with open(json_filepath, 'w') as graph_file, open(id2idx_filepath, 'w') as id2idx_file:
        graph_file.write(json.dumps(json_data))
        id2idx_file.write(json.dumps(id2idx))


if __name__ == '__main__':
    # Set path names.
    DATA_DIR = "data/"
    FILENAMES = ["an_adj.Rdata", "bn_adj.Rdata", "cross_adj.RData", "age_adj_1.csv", "age_adj_2.csv", "age_adj_3.csv", "age_adj_4.csv"]

    OUTDIR = "networks/"

    # Convert each file to network.
    for FILE in FILENAMES:
        generate_network(DATA_DIR + FILE, OUTDIR)
