from collections import defaultdict
from typing import Dict, List, Tuple
import dgl
from translators.translator import Translator
from gqlalchemy import Match
from gqlalchemy.models import Node, Relationship
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

    def __init__(self, default_node_label="NODE", default_edge_type="RELATIONSHIP") -> None:
        super().__init__()
        self.default_node_label = default_node_label
        self.default_edge_type = default_edge_type

    def to_cypher_queries(self, graph):
        return super().to_cypher_queries()

    def get_instance(self, query_results=None):
        # reindex[type][old_index] = new_index, not sure if need back reference also
        # TODO: offer an option for encoding string features maybe?
        mem_indexes: Dict[str, int] = defaultdict(int)  # track current counter for the node type
        node_features: Dict[str, Dict[str, List[int]]] = defaultdict(dict)  # node_label to prop_name to list of features for all nodes of that label
        edge_features: Dict[str, Dict[str, List[int]]] = defaultdict(dict)  # edge_type to prop_name to list of features for all edges of that type
        src_nodes: Dict[Tuple[str, str, str], List[int]] = defaultdict(list) # key=(source_node_label, edge_type, destination_node_label), value=list of source nodes
        dest_nodes: Dict[Tuple[str, str, str], List[int]] = defaultdict(list) # key=(source_node_label, edge_type, destination_node_label), value=list of dest nodes
        reindex: Dict[str, Dict[int, int]] = defaultdict(dict)  # Reindex structure for saving node_label to old_index to new_index

        # Offer an option to convert automatically so the user doesn't need to execute any query by herself/himself.
        if query_results is None:
            query_results = Match().node(variable='n').to(variable='r').node(variable='m').return_().execute()

        # Here will come different ways of handling query_results depending on the info that is inside
        # Currently assume that we executed a query for finding all nodes and relationships
        for row in query_results:
            row_values = row.values()
            print(f"Row values: {row_values}")

            for entity in row_values:
                if isinstance(entity, Node):
                    # Extract node label and all numeric features
                    node_label = Translator.merge_labels(entity._labels, self.default_node_label)
                    node_num_features = Translator.get_entity_numeric_properties(entity)
                    node_num_features = {"hey": 1, "numa": 2}
                    # Index node to a new index
                    reindex[node_label][entity._id] = mem_indexes[node_label]
                    mem_indexes[node_label] += 1
                    # Copy numeric features of a node
                    for num_feature_key, num_feature_val in node_num_features.items():
                        if num_feature_key not in node_features[node_label]:
                            node_features[node_label][num_feature_key] = []
                        node_features[node_label][num_feature_key].append(num_feature_val)  # this should fail
                elif isinstance(entity, Relationship):
                    # Extract edge type and all numeric features
                    edge_type = entity._type if entity._type else self.default_edge_type
                    edge_num_features = Translator.get_entity_numeric_properties(entity)
                    for num_feature_key, num_feature_val in edge_num_features.items():
                        if num_feature_key not in edge_features[edge_type]:
                            edge_features[edge_type][num_feature_key] = []
                        edge_features[edge_type][num_feature_key].append(num_feature_val)  # this should fail

                    # Now find descriptions of source and destination nodes. Cheap because we search only over row values, this is better than querying the database again.
                    source_node_index, dest_node_index = None, None
                    source_node_label, dest_node_label = None, None
                    for new_entity in row_values:
                        if new_entity._id == entity._start_node_id:
                            source_node_label = Translator.merge_labels(new_entity._labels, self.default_node_label)
                            source_node_index = reindex[source_node_label][new_entity._id]
                        elif new_entity._id == entity._end_node_id:
                            dest_node_label = Translator.merge_labels(new_entity._labels, self.default_node_label)
                            dest_node_index = reindex[dest_node_label][new_entity._id]
                    # Append to the graph data
                    src_nodes[(source_node_label, edge_type, dest_node_label)].append(source_node_index)
                    dest_nodes[(source_node_label, edge_type, dest_node_label)].append(dest_node_index)

        # Create heterograph
        graph_data = {}
        # Iterating over src_nodes and dest_nodes should be the same
        for type_triplet in src_nodes.keys():
            graph_data[type_triplet] = (torch.tensor(src_nodes[type_triplet], dtype=torch.int32), torch.tensor(dest_nodes[type_triplet], dtype=torch.int32))

        # Create heterograph
        print(f"Graph data: {graph_data}")
        graph = dgl.heterograph(graph_data)
        for node_label, features_dict in node_features.items():
            for feature_name, features in features_dict.items():
                graph.nodes[node_label].data[feature_name] = torch.tensor(features, dtype=torch.float32)

        print(f"Graph: {graph.nodes['NODE']}")

        return graph