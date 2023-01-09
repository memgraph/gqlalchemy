from translators.translator import Translator
from torch_geometric.data import HeteroData
from typing import Dict, List, Tuple
from collections import defaultdict
from gqlalchemy import Match
from gqlalchemy.models import Node, Relationship
import torch

# TODO: Solve order import
class PyGTranslator(Translator):

    def __init__(self) -> None:
        super().__init__()

    def to_cypher_queries(self, graph):
        return super().to_cypher_queries()

    def get_instance(self):
        # Get all nodes and edges from the database
        query_results = Match().node(variable='n').to(variable='r').node(variable='m').return_().execute()

        # Parse it into nice data structures
        src_nodes, dest_nodes, node_features, edge_features, mem_indexes = self._parse_mem_graph(query_results)

        # Create PyG heterograph
        graph = HeteroData()

        # Create edges in COO format
        # TODO: research about COO format
        for type_triplet in src_nodes.keys():
            graph[type_triplet].edge_index = torch.tensor([src_nodes[type_triplet], dest_nodes[type_triplet]], dtype=torch.int32)

        # Set node features
        for node_label, features_dict in node_features.items():
            for feature_name, features in features_dict.items():
                setattr(graph[node_label], feature_name, torch.tensor(features, dtype=torch.float32))

        # Set number of nodes, otherwise PyG inferes automatically and warnings can occur
        for node_label, num_nodes_label in mem_indexes.items():
            graph[node_label].num_nodes = num_nodes_label

        # Set edge features
        for edge_triplet, features_dict in edge_features.items():
            for feature_name, features in features_dict.items():
                setattr(graph[edge_triplet], feature_name, torch.tensor(features, dtype=torch.float32))

        # PyG offers a method to validate graph so if something is wrong an error will occur
        graph.validate(raise_on_error=True)
        return graph