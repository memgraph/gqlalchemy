# Copyright (c) 2016-2023 Memgraph Ltd. [https://memgraph.com]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from abc import ABC, abstractmethod
from typing import Callable, List, Set, Dict, Tuple
from collections import defaultdict
from numbers import Number

try:
    import torch
except ModuleNotFoundError:
    torch = None

from gqlalchemy.exceptions import raise_if_not_imported
from gqlalchemy.transformations.constants import LABELS_CONCAT, DEFAULT_NODE_LABEL, DEFAULT_EDGE_TYPE
from gqlalchemy.memgraph_constants import (
    MG_HOST,
    MG_PORT,
    MG_USERNAME,
    MG_PASSWORD,
    MG_ENCRYPTED,
    MG_CLIENT_NAME,
    MG_LAZY,
)
from gqlalchemy.models import Node, Relationship
from gqlalchemy.utilities import to_cypher_properties
from gqlalchemy import Memgraph, Match


class Translator(ABC):
    # Lambda function to concat list of labels
    merge_labels: Callable[[Set[str]], str] = (
        lambda labels, default_node_label: LABELS_CONCAT.join([label for label in sorted(labels)])
        if len(labels)
        else default_node_label
    )

    @abstractmethod
    def __init__(
        self,
        host: str = MG_HOST,
        port: int = MG_PORT,
        username: str = MG_USERNAME,
        password: str = MG_PASSWORD,
        encrypted: bool = MG_ENCRYPTED,
        client_name: str = MG_CLIENT_NAME,
        lazy: bool = MG_LAZY,
    ) -> None:
        super().__init__()
        self.connection = Memgraph(host, port, username, password, encrypted, client_name, lazy)

    @abstractmethod
    def to_cypher_queries(graph):
        """Abstract method which doesn't know how to produce cypher queries for a specific graph type and thus needs to be overridden.
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
        """Abstract method which doesn't know how to create the concrete instance so it needs to be overridden.

        Raises:
            NotImplementedError: The method must be override by a specific translator.
        """
        raise NotImplementedError(
            "Subclasses must override this method to correctly parse query results for specific graph type."
        )

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
        raise_if_not_imported(dependency=torch, dependency_name="torch")

        if len(features) != expected_num:
            return None
        try:
            return torch.tensor(features, dtype=torch.float32)
        except ValueError:
            return None

    @classmethod
    def get_properties(cls, properties, entity_id):
        properties_ret = {}
        for property_key, property_values in properties.items():
            properties_ret[property_key] = property_values[entity_id]
        return properties_ret

    def _parse_memgraph(self):
        """Returns Memgraph's data parsed in a nice way to be used for creating DGL and PyG graphs."""
        mem_indexes: Dict[str, int] = defaultdict(int)  # track current counter for the node type
        node_features: Dict[str, Dict[str, List[int]]] = defaultdict(
            lambda: defaultdict(list)
        )  # node_label to prop_name to list of features for all nodes of that label
        edge_features: Dict[Tuple[str, str, str], Dict[str, List[int]]] = defaultdict(
            lambda: defaultdict(list)
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

        rel_results = self.get_all_edges_from_db()

        for row in rel_results:
            row_values = row.values()
            for entity in row_values:
                entity_num_features = dict(
                    filter(lambda pair: Translator._is_most_inner_type_number(pair[1]), entity._properties.items())
                )
                if isinstance(entity, Node):
                    # Extract node label and all numeric features
                    node_label = Translator.merge_labels(entity._labels, DEFAULT_NODE_LABEL)
                    # Index node to a new index
                    if entity._id not in reindex[node_label]:
                        reindex[node_label][entity._id] = mem_indexes[node_label]
                        mem_indexes[node_label] += 1
                        # Copy numeric features of a node
                        for num_feature_key, num_feature_val in entity_num_features.items():
                            node_features[node_label][num_feature_key].append(num_feature_val)  # this should fail
                elif isinstance(entity, Relationship):
                    # Extract edge type and all numeric features
                    edge_type = entity._type if entity._type else DEFAULT_EDGE_TYPE
                    # Find descriptions of source and destination nodes. Cheap because we search only over row values, this is better than querying the database again.
                    source_node_index, dest_node_index = None, None
                    source_node_label, dest_node_label = None, None
                    for new_entity in row_values:
                        if new_entity._id == entity._start_node_id and isinstance(new_entity, Node):
                            source_node_label = Translator.merge_labels(new_entity._labels, DEFAULT_NODE_LABEL)
                            source_node_index = reindex[source_node_label][new_entity._id]
                        elif new_entity._id == entity._end_node_id and isinstance(new_entity, Node):
                            dest_node_label = Translator.merge_labels(new_entity._labels, DEFAULT_NODE_LABEL)
                            dest_node_index = reindex[dest_node_label][new_entity._id]
                    # Append to the graph data
                    edge_triplet = (source_node_label, edge_type, dest_node_label)
                    src_nodes[edge_triplet].append(source_node_index)
                    dest_nodes[edge_triplet].append(dest_node_index)
                    # Save edge features
                    for num_feature_key, num_feature_val in entity_num_features.items():
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

    def get_all_edges_from_db(self):
        """Returns all edges from the database.
        Returns:
            Query results when finding all edges.
        """
        return (
            Match(connection=self.connection).node(variable="n").to(variable="r").node(variable="m").return_().execute()
        )

    def get_all_isolated_nodes_from_db(self):
        """Returns all isolated nodes from the database.
        Returns:
            Query results for finding all isolated nodes.
        """
        return (
            Match(connection=self.connection)
            .node(variable="n")
            .add_custom_cypher("WHERE degree(n) = 0")
            .return_()
            .execute()
        )
