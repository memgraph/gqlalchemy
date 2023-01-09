import dgl
from translators.translator import Translator
from gqlalchemy import Match
import torch
# TODO: check import order

class DGLTranslator(Translator):
    """Performs conversion from cypher queries to the DGL graph representation. DGL assigns to each edge a unique integer, called the edge ID,
    based on the order in which it was added to the graph. In DGL, all the edges are directed, and an edge (u,v) indicates that the direction goes
    from node u to node v. Only features of numerical types (e.g., float, double, and int) are allowed. They can be scalars, vectors or multi-dimensional
    tensors (DQL requirement). Each node feature has a unique name and each edge feature has a unique name. The features of nodes and edges can have
    the same name. A feature is created via tensor assignment, which assigns a feature to each node/edge in the graph. The leading dimension of that
    tensor must be equal to the number of nodes/edges in the graph. You cannot assign a feature to a subset of the nodes/edges in the graph. Features of the
    same name must have the same dimensionality and data type.
    """

    def __init__(self) -> None:
        super().__init__()

    # for now, assume we can handle heterographs and homogenous graphs in the same way
    def to_cypher_queries(self, graph):
        # For a graph of multiple edge types, it is required to specify the edge type in query.
        if isinstance(graph, dgl.DGLHeteroGraph):
            print(f"It is heterograph")
        elif isinstance(graph, dgl.DGLGraph):
            print(f"Homogeneous graph")
        edges = graph.edges()  # 1D tensors
        print(f"Edges: {edges}")


        return []

    # TODO: add support for processing isolated nodes
    def get_instance(self):
        # Get all nodes and edges from the database
        query_results = Match().node(variable='n').to(variable='r').node(variable='m').return_().execute()

        # Parse it into nice data structures
        src_nodes, dest_nodes, node_features, edge_features, _ = self._parse_mem_graph(query_results)

        graph_data = {}
        # Iterating over src_nodes and dest_nodes should be the same
        for type_triplet in src_nodes.keys():
            graph_data[type_triplet] = (torch.tensor(src_nodes[type_triplet], dtype=torch.int32), torch.tensor(dest_nodes[type_triplet], dtype=torch.int32))

        # Create heterograph
        graph = dgl.heterograph(graph_data)
        # Set node features
        for node_label, features_dict in node_features.items():
            for feature_name, features in features_dict.items():
                graph.nodes[node_label].data[feature_name] = torch.tensor(features, dtype=torch.float32)

        # Set edge features
        for edge_triplet, features_dict in edge_features.items():
            for feature_name, features in features_dict.items():
                graph[edge_triplet].data[feature_name] = torch.tensor(features, dtype=torch.float32)

        return graph