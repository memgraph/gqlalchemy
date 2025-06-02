# Copyright (c) 2016-2025 Memgraph Ltd. [https://memgraph.com]
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


from typing import List, Dict, Any, Set, Tuple
import tensorflow as tf
import tensorflow_gnn as tfgnn
from collections import defaultdict
from gqlalchemy.transformations.constants import DEFAULT_NODE_LABEL, TFGNN_ID
from gqlalchemy.transformations.translators.translator import Translator
import numpy as np

from gqlalchemy.memgraph_constants import (
    MG_HOST,
    MG_PORT,
    MG_USERNAME,
    MG_PASSWORD,
    MG_ENCRYPTED,
    MG_CLIENT_NAME,
    MG_LAZY,
)


class TFGNNTranslator(Translator):
    """Translator for converting between Memgraph and TF-GNN graph representations.

    TF-GNN represents graphs as GraphTensor objects, which are composite tensors
    that can be used directly in TensorFlow operations. This translator handles
    the conversion between Memgraph's graph model and TF-GNN's GraphTensor.
    """

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
        super().__init__(host, port, username, password, encrypted, client_name, lazy)

    def get_instance(self) -> tfgnn.GraphTensor:
        """Creates a TF-GNN GraphTensor instance from the data residing inside Memgraph.

        Returns:
            tfgnn.GraphTensor: The created GraphTensor instance.
        """
        memgraph = self.connection
        # Get all nodes
        nodes = memgraph.execute_and_fetch("MATCH (n) RETURN id(n), labels(n), properties(n)")

        # node data container
        node_data = defaultdict(dict)
        for node in nodes:
            memgraph_id = node["id(n)"]
            labels = node["labels(n)"] or [DEFAULT_NODE_LABEL]
            properties = node["properties(n)"]

            for label in labels:
                node_data[label][memgraph_id] = properties

        # Create node sets
        node_sets = {}
        for label, memgraph_id_properties in node_data.items():
            sizes = tf.constant([len(memgraph_id_properties)])
            features = self._convert_properties_to_tensors(memgraph_id_properties.values())
            node_sets[label] = tfgnn.NodeSet.from_fields(sizes=sizes, features=features)

        # Create mapping from Memgraph ID to TF-GNN ID
        # TFGNN has node id for each node type starting from 0 to N
        # the edges have schema describing the node types for source and target
        memgraph_id_to_tfgnn_id = defaultdict(dict)
        for label, memgraph_id_properties in node_data.items():
            for tfgnn_id, memgraph_id in enumerate(memgraph_id_properties.keys()):
                memgraph_id_to_tfgnn_id[label][memgraph_id] = tfgnn_id

        # Get all edges
        edges = memgraph.execute_and_fetch(
            "MATCH (source)-[r]->(target) RETURN id(r), type(r), properties(r), id(source), id(target), labels(source), labels(target)"
        )

        # data containers for edges
        edges_properties = defaultdict(list)
        edges_source_memgraph_ids = defaultdict(list)
        edges_target_memgraph_ids = defaultdict(list)
        # in tfgnn the edges have schema describing the node types for source and target
        edge_type_source_name = defaultdict(set)
        edge_type_target_name = defaultdict(set)

        for edge in edges:
            edge_type = edge["type(r)"]
            memgraph_id_source = edge["id(source)"]
            memgraph_id_target = edge["id(target)"]
            properties = edge["properties(r)"]
            source_labels = edge["labels(source)"] or [DEFAULT_NODE_LABEL]
            target_labels = edge["labels(target)"] or [DEFAULT_NODE_LABEL]

            edges_source_memgraph_ids[edge_type].append(memgraph_id_source)
            edges_target_memgraph_ids[edge_type].append(memgraph_id_target)
            edges_properties[edge_type].append(properties)

            for source_label in source_labels:
                for target_label in target_labels:
                    edge_type_source_name[edge_type].add(source_label)
                    edge_type_target_name[edge_type].add(target_label)

        edge_types = list(edge_type_source_name.keys())
        edge_sets = {}
        for edge_type in edge_types:
            if len(edge_type_source_name[edge_type]) > 1 or len(edge_type_target_name[edge_type]) > 1:
                multiple_node_types_share_edge_type = True
            else:
                multiple_node_types_share_edge_type = False
            for source_label in edge_type_source_name[edge_type]:
                for target_label in edge_type_target_name[edge_type]:
                    tfgnn_source_ids = [
                        memgraph_id_to_tfgnn_id[source_label][i] for i in edges_source_memgraph_ids[edge_type]
                    ]
                    tfgnn_target_ids = [
                        memgraph_id_to_tfgnn_id[target_label][i] for i in edges_target_memgraph_ids[edge_type]
                    ]
                    if multiple_node_types_share_edge_type:
                        edge_name = f"{source_label}_{edge_type}_{target_label}"
                    else:
                        edge_name = edge_type

                    edge_sets[edge_name] = tfgnn.EdgeSet.from_fields(
                        sizes=tf.constant([len(tfgnn_source_ids)]),
                        adjacency=tfgnn.Adjacency.from_indices(
                            source=(source_label, tf.constant(tfgnn_source_ids, dtype=tf.int64)),
                            target=(target_label, tf.constant(tfgnn_target_ids, dtype=tf.int64)),
                        ),
                        features=self._convert_properties_to_tensors(edges_properties[edge_type]),
                    )

        return tfgnn.GraphTensor.from_pieces(node_sets=node_sets, edge_sets=edge_sets)

    def _infer_dtype_from_value(self, value: Any) -> tf.DType:
        if isinstance(value, dict):
            raise ValueError(f"Map property type is not supported by TFGNN.")
        if isinstance(value, str):
            return tf.string
        elif isinstance(value, int):
            return tf.int64
        elif isinstance(value, float):
            return tf.float32
        elif isinstance(value, bool):
            return tf.bool
        else:
            raise ValueError(f"Unexpected type: {type(value)}.")

    def _properties_metadata(
        self, properties_list: List[Dict[str, Any]]
    ) -> Tuple[Set[str], Set[str], Dict[str, tf.DType], Set[str]]:
        all_property_names = set()
        list_properties = set()
        dtypes = {}

        for properties in properties_list:
            all_property_names.update(properties.keys())
            for key, value in properties.items():
                if isinstance(value, list):
                    list_properties.add(key)
                    if len(value):
                        value = value[0]
                    else:
                        continue

                dtypes[key] = self._infer_dtype_from_value(value)

        properties_with_missing_values = set()
        for properties in properties_list:
            for key in all_property_names:
                if key not in properties:
                    properties_with_missing_values.add(key)
        return all_property_names, list_properties, dtypes, properties_with_missing_values

    def _convert_properties_to_tensors(self, properties_list: List[Dict[str, Any]]) -> Dict[str, tf.Tensor]:
        """
        Converts list of properties to TF tensors.

        properties_list example:
        [
            {"name": "John", "age": 30},
            {"name": "Jane"}
        ]

        Returns a dictionary of TF tensors in one of the following dtypes: tf.string, tf.int64, tf.float32, tf.bool.


        example:
        {
            "name": tf.constant(["John", "Jane"], dtype=tf.string),
            "age": tf.ragged.constant([[30], []], dtype=tf.int64)
        }

        Convertion rules:

            Properties are allowed to be missing for some nodes.
                eg: one node can have property 'age' and another node can only have property 'name'

            If properties have different types, an exception will be raised.
                eg: if one node has property 'age' as Integer and another node has property 'age' as String, an exception will be raised.

            If a property have type String, Integer, Float, Boolean:
                Then if all nodes have the same property value, it is converted to a dense 1D tensor eg:  [1, 2, 3]
                Otherwise, it is converted to a ragged 2D tensor eg: [[1], [], [3]]
                    The user can fill the missing value and convert to dense tensor by `ragged_tensor.to_tensor(default_value=0)`

            If a property have type List:
                Then if all nodes have values of the same length, it is converted to a dense 2D tensor eg:  [[1, 2, 3], [3, 4, 5]]
                Otherwise, it is converted to a ragged 2D tensor eg: [[1, 2], [], [3, 4, 5]]

            If a property have type Map:
                Then exception will be raised as tfgnn.GraphTensor does not support map property type
        """
        all_property_names, list_properties, dtypes, properties_with_missing_values = self._properties_metadata(
            properties_list
        )

        features = defaultdict(list)

        for properties in properties_list:
            for key in all_property_names:
                if key not in properties:
                    # missing value
                    value = []
                else:
                    if key in properties_with_missing_values:
                        if key in list_properties:
                            value = properties[key]
                        else:
                            value = [properties[key]]
                    else:
                        value = properties[key]

                features[key].append(value)

        for key, values in features.items():
            if key not in properties_with_missing_values:
                if key not in dtypes:
                    # do not include property if all nodes have empty lists
                    continue
                if key in list_properties:
                    have_same_shape = True
                    for value in values:
                        have_same_shape = have_same_shape and len(value) == len(values[0])
                    if have_same_shape:
                        features[key] = tf.constant(values, dtype=dtypes[key])
                    else:
                        features[key] = tf.ragged.constant(values, dtype=dtypes[key])
                else:
                    features[key] = tf.constant(values, dtype=dtypes[key])
            else:
                features[key] = tf.ragged.constant(values, dtype=dtypes[key])
        return features

    def _convert_tensors_to_properties(self, features: Dict[str, tf.Tensor], idx: int) -> Dict[str, Any]:
        """Converts TF tensors to properties dictionary."""
        properties = {}
        for key, tensor in features.items():
            value = tensor[idx].numpy()
            if not isinstance(value, np.ndarray) and isinstance(value, bytes):
                value = value.decode("utf-8")
            if isinstance(value, np.ndarray) and (np.issubdtype(value.dtype, np.bytes_) or value.dtype == np.object_):
                value = value.astype(str)
            if (isinstance(value, np.ndarray) or isinstance(value, list)) and len(value) == 0:
                # skip empty values
                continue
            if isinstance(value, (np.floating, float)) and (np.isnan(value) or np.isinf(value)):
                continue
            properties[key] = value

        return properties

    def to_cypher_queries(self, graph_tensor: tfgnn.GraphTensor) -> List[str]:
        """Produce cypher queries for data saved as part of the TFGNN graph. If the graph is homogeneous, a default TFGNN's labels will be used.
        _N as a node label and _E as edge label. The method converts 1D as well as multidimensional features. If there are some isolated nodes inside TFGNN graph, they won't get transferred. Nodes and edges
        created in Memgraph DB will, for the consistency reasons, have property `dgl_id` set to the id they have as part of the TFGNN graph. Note that this method doesn't insert anything inside the database,
        it just creates cypher queries. To insert queries the following code can be used:
        >>> memgraph = Memgraph()
        graph_tensor = TFGNNTranslator(...)
        for query in TFGNNTranslator().to_cypher_queries(graph_tensor):
           memgraph.execute(query)
        """

        queries = []
        # merge potentially batched graphs to one graph with disjoined graphs
        graph_tensor = graph_tensor.merge_batch_to_components()

        for edge_type, edge_set in graph_tensor.edge_sets.items():
            # in GraphTensor, the source and target nodes are explicitly defined in edge set schema
            source_node_label = edge_set.adjacency.source_name
            dest_node_label = edge_set.adjacency.target_name

            for edge_index in range(edge_set.sizes[0]):
                start_node_id = edge_set.adjacency.source[edge_index].numpy()
                source_node_properties = self._convert_tensors_to_properties(
                    graph_tensor.node_sets[source_node_label].features, start_node_id
                )
                source_node_properties[TFGNN_ID] = start_node_id

                end_node_id = edge_set.adjacency.target[edge_index].numpy()
                dest_node_properties = self._convert_tensors_to_properties(
                    graph_tensor.node_sets[dest_node_label].features, end_node_id
                )
                dest_node_properties[TFGNN_ID] = end_node_id

                edge_properties = self._convert_tensors_to_properties(edge_set.features, edge_index)
                edge_properties[TFGNN_ID] = edge_index

                queries.append(
                    self.create_insert_query(
                        source_node_label=source_node_label,
                        source_node_properties=source_node_properties,
                        edge_type=edge_type,
                        edge_properties=edge_properties,
                        dest_node_label=dest_node_label,
                        dest_node_properties=dest_node_properties,
                    )
                )
        return queries


def to_cypher_index_queries(self, graph_tensor: tfgnn.GraphTensor) -> List[str]:
    """
    Creates cypher index queries for the graph.
    """
    queries = []
    for node_name in graph_tensor.node_sets:
        queries.append(f"CREATE INDEX ON :{node_name}({TFGNN_ID})")
    return queries
