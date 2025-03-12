"""Set of utilities to compute global and local metrics of a network."""

import networkx as nx
import numpy as np


def compute_metric(G, metric, u=None):
    """
    Compute the specified metric for the graph G.
    """
    if metric == "num_nodes":
        return G.number_of_nodes()
    elif metric == "num_edges":
        return G.number_of_edges()
    elif metric == "avg_degree":
        return np.mean([d for _, d in G.degree()])
    elif metric == "longest_shortest_path":
        return max(list(nx.shortest_path_length(G)))
    elif metric == "avg_shortest_path":
        return nx.average_shortest_path_length(G)
    elif metric == "radius":
        return nx.radius(G)
    elif metric == "diameter":
        return nx.diameter(G)
    elif metric == "node_connectivity":
        return nx.node_connectivity(G)
    elif metric == "edge_connectivity":
        return nx.edge_connectivity(G)
    elif metric == "avg_closeness_centrality":
        return np.mean(list(nx.closeness_centrality(G).values()))
    elif metric == "avg_betweenness_centrality":
        return np.mean(list(nx.betweenness_centrality(G).values()))
    elif metric == "avg_degree_centrality":
        return np.mean(list(nx.degree_centrality(G).values()))
    elif metric == "avg_pagerank":
        return np.mean(list(nx.pagerank(G).values()))
    elif metric == "avg_eigenvector_centrality":
        return np.mean(list(nx.eigenvector_centrality(G).values()))
    elif metric == "avg_clustering":
        return nx.average_clustering(G)
    elif metric == "degree_assortativity":
        return nx.degree_assortativity_coefficient(G)
    elif metric == "degree":
        return nx.degree(G, u)
    elif metric == "eccentricity":
        return nx.eccentricity(G, u)
    elif metric == "closeness_centrality":
        return nx.closeness_centrality(G, u)
    elif metric == "betweenness_centrality":
        bet_dict = nx.betweenness_centrality(G)
        return bet_dict[u]
    elif metric == "degree_centrality":
        deg_dict = nx.degree_centrality(G)
        return deg_dict[u]
    elif metric == "eigenvector_centrality":
        eig_dict = nx.eigenvector_centrality(G)
        return eig_dict[u]
    elif metric == "clustering":
        return nx.clustering(G, u)
    else:
        raise NameError(f"{metric} is not a valid metric.")