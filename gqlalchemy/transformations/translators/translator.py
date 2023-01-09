from abc import ABC, abstractmethod
from typing import Callable, List, Set, Union, Type, Dict, Tuple
from collections import defaultdict
from constants import LABELS_CONCAT
from numbers import Number
from gqlalchemy.models import Node, Relationship
# TODO: fix the import order


class Translator(ABC):

    # Lambda function to concat list of labels
    merge_labels: Callable[[Set[str]], str] = lambda labels, default_node_label: LABELS_CONCAT.join([label for label in labels]) if len(labels) else default_node_label

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
        raise NotImplementedError("Subclasses must override this method to produce cypher queries for specific graph type.")

    @abstractmethod
    def get_instance():
        """Abstract method which doesn't know how to create the concrete instance so it needs to be overriden.

        Raises:
            NotImplementedError: The method must be override by a specific translator.
        """
        raise NotImplementedError("Subclasses must override this method to correctly parse query results for specific graph type.")

    @classmethod
    def get_entity_numeric_properties(cls, entity: Union[Node, Relationship]):
        """
        """
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
        return isinstance(obj, Number)

    def _parse_mem_graph(self, query_results):
        """
        """
        mem_indexes: Dict[str, int] = defaultdict(int)  # track current counter for the node type
        node_features: Dict[str, Dict[str, List[int]]] = defaultdict(dict)  # node_label to prop_name to list of features for all nodes of that label
        edge_features: Dict[Tuple[str, str, str], Dict[str, List[int]]] = defaultdict(dict)  # (source_node_label, edge_type, dest_node_label) to prop_name to list of features for all edges of that type
        src_nodes: Dict[Tuple[str, str, str], List[int]] = defaultdict(list)  # key=(source_node_label, edge_type, destination_node_label), value=list of source nodes
        dest_nodes: Dict[Tuple[str, str, str], List[int]] = defaultdict(list)  # key=(source_node_label, edge_type, destination_node_label), value=list of dest nodes
        reindex: Dict[str, Dict[int, int]] = defaultdict(dict)  # Reindex structure for saving node_label to old_index to new_index

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
                        for num_feature_key, num_feature_val in node_num_features.items():
                            if num_feature_key not in node_features[node_label]:
                                node_features[node_label][num_feature_key] = []
                            node_features[node_label][num_feature_key].append(num_feature_val)  # this should fail
                elif isinstance(entity, Relationship):
                    # Extract edge type and all numeric features
                    edge_type = entity._type if entity._type else self.default_edge_type
                    edge_num_features = Translator.get_entity_numeric_properties(entity)
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
