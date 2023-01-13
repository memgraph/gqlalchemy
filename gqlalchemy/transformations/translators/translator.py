from abc import ABC, abstractmethod
from typing import Callable, List, Set, Union, Dict, Tuple
from collections import defaultdict
from numbers import Number

import torch

from gqlalchemy.transformations.constants import LABELS_CONCAT
from gqlalchemy.models import Node, Relationship
from gqlalchemy.utilities import to_cypher_properties

# TODO: fix the import order


class Translator(ABC):

    # Lambda function to concat list of labels
    merge_labels: Callable[[Set[str]], str] = (
        lambda labels, default_node_label: LABELS_CONCAT.join([label for label in sorted(labels)])
        if len(labels)
        else default_node_label
    )

    @abstractmethod
    def __init__(self, default_node_label="NODE", default_edge_type="RELATIONSHIP") -> None:
        super().__init__()
        self.default_node_label = default_node_label
        self.default_edge_type = default_edge_type

    @abstractmethod
    def to_cypher_queries(graph):
        """Abstract method which doesn't know how to produce cypher queries for a specific graph type and thus needs to be overriden.
        Args:
            graph: Can be of any type supported by the derived Translator object.

        Raises:
            NotImplementedError: The method must be override by a specific translator.
        """
        raise NotImplementedError(
            "Subclasses must override this method to produce cypher queries for specific graph type."
        )

    @abstractmethod
    def get_instance():
        """Abstract method which doesn't know how to create the concrete instance so it needs to be overriden.

        Raises:
            NotImplementedError: The method must be override by a specific translator.
        """
        raise NotImplementedError(
            "Subclasses must override this method to correctly parse query results for specific graph type."
        )

    @classmethod
    def get_entity_numeric_properties(cls, entity: Union[Node, Relationship]):
        """ """
        numeric_properties = {}
        for key, val in entity._properties.items():
            if Translator._is_most_inner_type_number(val):
                numeric_properties[key] = val
        return numeric_properties

    @classmethod
    def _is_most_inner_type_number(cls, obj):
        """Checks if the most inner object type is a type derived from Number. E.g For a List[List[int]] return True
        Args:
            obj: Object that will be checked.

        Returns:
            None if the object is empty(type cannot be inferred) or the type of the most inner object.
        """
        if isinstance(obj, list):
            return len(obj) and Translator._is_most_inner_type_number(obj[0])
        # Try to parser string into number
        return isinstance(obj, Number)

    @classmethod
    def validate_features(cls, features: List, expected_num: int):
        """Return true if features are okay to be set on all nodes/features.
        Args:
            features: To be set on all nodes. It can be anything that can be converted to torch tensor.
            expected_num: This can be number of nodes or number of edges depending on whether features will be set on nodes or edges.
        Returns:
            None if features cannot be set or tensor of same features.
        """
        if len(features) != expected_num:
            return None
        try:
            return torch.tensor(features, dtype=torch.float32)
        except ValueError:
            return None


    def _parse_mem_graph(self, query_results):
        """ """
        mem_indexes: Dict[str, int] = defaultdict(int)  # track current counter for the node type
        node_features: Dict[str, Dict[str, List[int]]] = defaultdict(
            dict
        )  # node_label to prop_name to list of features for all nodes of that label
        edge_features: Dict[Tuple[str, str, str], Dict[str, List[int]]] = defaultdict(
            dict
        )  # (source_node_label, edge_type, dest_node_label) to prop_name to list of features for all edges of that type
        src_nodes: Dict[Tuple[str, str, str], List[int]] = defaultdict(
            list
        )  # key=(source_node_label, edge_type, destination_node_label), value=list of source nodes
        dest_nodes: Dict[Tuple[str, str, str], List[int]] = defaultdict(
            list
        )  # key=(source_node_label, edge_type, destination_node_label), value=list of dest nodes
        reindex: Dict[str, Dict[int, int]] = defaultdict(
            dict
        )  # Reindex structure for saving node_label to old_index to new_index

        for row in query_results:
            row_values = row.values()
            # print(f"Row values: {row_values}")
            for entity in row_values:
                if isinstance(entity, Node):
                    # Extract node label and all numeric features
                    node_label = Translator.merge_labels(entity._labels, self.default_node_label)
                    # Index node to a new index
                    if entity._id not in reindex[node_label]:
                        reindex[node_label][entity._id] = mem_indexes[node_label]
                        mem_indexes[node_label] += 1
                        # Copy numeric features of a node
                        node_num_features = Translator.get_entity_numeric_properties(entity)
                        # node_num_features["test"] = 1
                        for num_feature_key, num_feature_val in node_num_features.items():
                            if num_feature_key not in node_features[node_label]:
                                node_features[node_label][num_feature_key] = []
                            node_features[node_label][num_feature_key].append(num_feature_val)  # this should fail
                elif isinstance(entity, Relationship):
                    # Extract edge type and all numeric features
                    edge_type = entity._type if entity._type else self.default_edge_type
                    edge_num_features = Translator.get_entity_numeric_properties(entity)
                    # edge_num_features["test"] = 2
                    # Find descriptions of source and destination nodes. Cheap because we search only over row values, this is better than querying the database again.
                    source_node_index, dest_node_index = None, None
                    source_node_label, dest_node_label = None, None
                    for new_entity in row_values:
                        if new_entity._id == entity._start_node_id and isinstance(new_entity, Node):
                            source_node_label = Translator.merge_labels(new_entity._labels, self.default_node_label)
                            source_node_index = reindex[source_node_label][new_entity._id]
                        elif new_entity._id == entity._end_node_id and isinstance(new_entity, Node):
                            dest_node_label = Translator.merge_labels(new_entity._labels, self.default_node_label)
                            dest_node_index = reindex[dest_node_label][new_entity._id]
                    # Append to the graph data
                    edge_triplet = (source_node_label, edge_type, dest_node_label)
                    src_nodes[edge_triplet].append(source_node_index)
                    dest_nodes[edge_triplet].append(dest_node_index)
                    # Save edge features
                    for num_feature_key, num_feature_val in edge_num_features.items():
                        if num_feature_key not in edge_features[edge_triplet]:
                            edge_features[edge_triplet][num_feature_key] = []
                        edge_features[edge_triplet][num_feature_key].append(num_feature_val)

        return src_nodes, dest_nodes, node_features, edge_features, mem_indexes

    def create_insert_query(
        self,
        source_node_label,
        source_node_properties,
        edge_type,
        edge_properties,
        dest_node_label,
        dest_node_properties,
    ):
        return (
            f"MERGE (n:{source_node_label} {to_cypher_properties(source_node_properties)}) "
            f"MERGE (m:{dest_node_label} {to_cypher_properties(dest_node_properties)}) "
            f"MERGE (n)-[r:{edge_type} {to_cypher_properties(edge_properties)}]->(m)"
        )

    def get_properties(properties, entity_id):
        properties_ret = {}
        for property_key, property_values in properties.items():
            properties_ret[property_key] = property_values[entity_id]
        return properties_ret
