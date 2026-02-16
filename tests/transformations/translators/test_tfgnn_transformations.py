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


import pytest
import tensorflow as tf
import tensorflow_gnn as tfgnn
import numpy as np

from gqlalchemy import Memgraph
from gqlalchemy.transformations.translators.tfgnn_translator import TFGNNTranslator
from gqlalchemy.transformations.constants import DEFAULT_NODE_LABEL


def test_export_homogeneous_graph(memgraph: Memgraph):
    """
    Test exporting homogeneous graph (nodes without labels)
    """
    memgraph.execute(
        """
        CREATE (m {name: 'Alice'}), (n {name: 'Bob'}), (m)-[:FRIEND]->(n)
    """
    )
    graph_tensor = TFGNNTranslator().get_instance()

    assert graph_tensor.node_sets[DEFAULT_NODE_LABEL].sizes[0] == 2
    assert graph_tensor.node_sets[DEFAULT_NODE_LABEL].features["name"].numpy().tolist() == [b"Alice", b"Bob"]
    assert graph_tensor.edge_sets["FRIEND"].sizes[0] == 1
    assert len(graph_tensor.edge_sets["FRIEND"].features) == 0


def test_export_heterogeneous_graph(memgraph: Memgraph):
    """
    Test exporting heterogeneous graph (nodes with one label)
    """
    memgraph.execute(
        """
        CREATE (m:Person {name: 'Alice'}), (n:Person {name: 'Bob'}), (m)-[:FRIEND]->(n)
    """
    )
    graph_tensor = TFGNNTranslator().get_instance()
    assert graph_tensor.node_sets["Person"].sizes[0] == 2
    assert graph_tensor.edge_sets["FRIEND"].sizes[0] == 1


def test_export_heterogeneous_multi_label_graph(memgraph: Memgraph):
    """
    Test exporting heterogeneous graph and nodes with more than one label
    GraphTensor will create a node for every label and edge type for each combination of source / target labels
    """
    memgraph.execute(
        """
        CREATE (m:A:B {name: 'Alice'}), (n:C {name: 'Bob'}), (m)-[:FRIEND]->(n)
    """
    )

    graph_tensor = TFGNNTranslator().get_instance()
    assert graph_tensor.node_sets["A"].sizes[0] == 1
    assert graph_tensor.node_sets["B"].sizes[0] == 1
    assert graph_tensor.node_sets["C"].sizes[0] == 1

    assert graph_tensor.edge_sets["A_FRIEND_C"].sizes[0] == 1
    assert graph_tensor.edge_sets["B_FRIEND_C"].sizes[0] == 1


def test_export_missing_properties(memgraph: Memgraph):
    """
    Test exporting graph with missing properties
    """
    memgraph.execute(
        """
        CREATE (:Person {name: 'Alice'}), (:Person {name: 'Bob', age: 30}), (:Person {name: 'Charlie', height: 6.1})
    """
    )
    graph_tensor = TFGNNTranslator().get_instance()
    assert graph_tensor.node_sets["Person"].sizes[0] == 3
    assert graph_tensor.node_sets["Person"].features["name"].numpy().tolist() == [b"Alice", b"Bob", b"Charlie"]
    assert graph_tensor.node_sets["Person"].features["age"].to_tensor(default_value=0).numpy().flatten().tolist() == [
        0,
        30,
        0,
    ]
    assert np.allclose(
        graph_tensor.node_sets["Person"].features["height"].to_tensor(default_value=0).numpy().flatten(),
        [0.0, 0.0, 6.1],
    )


def test_export_list_properties_same_dimensionality(memgraph: Memgraph):
    """
    Test exporting graph with list properties of same dimensionality
    """
    memgraph.execute(
        """
        CREATE (:Person {name: 'Alice', hobbies: ['reading', 'hiking']}),
                (:Person {name: 'Bob', hobbies: ['reading', 'gaming']}),
                (:Person {name: 'Charlie', hobbies: ['reading', 'cooking']})
    """
    )
    graph_tensor = TFGNNTranslator().get_instance()
    assert graph_tensor.node_sets["Person"].sizes[0] == 3
    assert graph_tensor.node_sets["Person"].features["name"].numpy().tolist() == [b"Alice", b"Bob", b"Charlie"]
    assert graph_tensor.node_sets["Person"].features["hobbies"].numpy().tolist() == [
        [b"reading", b"hiking"],
        [b"reading", b"gaming"],
        [b"reading", b"cooking"],
    ]


def test_export_list_properties_various_dimensionality(memgraph: Memgraph):
    """
    Test exporting graph with list properties of various dimensionality
    """
    memgraph.execute(
        """
        CREATE (:Person {name: 'Alice', hobbies: ['hiking']}),
                (:Person {name: 'Bob', hobbies: ['reading', 'gaming']}),
                (:Person)
    """
    )
    graph_tensor = TFGNNTranslator().get_instance()
    assert graph_tensor.node_sets["Person"].sizes[0] == 3
    assert graph_tensor.node_sets["Person"].features["name"].to_tensor(default_value=b"N/A").numpy().tolist() == [
        [b"Alice"],
        [b"Bob"],
        [b"N/A"],
    ]
    assert graph_tensor.node_sets["Person"].features["hobbies"].to_tensor(
        default_value=b"reading"
    ).numpy().tolist() == [[b"hiking", b"reading"], [b"reading", b"gaming"], [b"reading", b"reading"]]


def test_export_map_properties(memgraph: Memgraph):
    memgraph.execute(
        """
        CREATE (:Person {hobbies: {reading: 1, hiking: 2}})
    """
    )
    with pytest.raises(ValueError, match="Map property type is not supported by TFGNN."):
        TFGNNTranslator().get_instance()


def test_create_simple_graph(memgraph: Memgraph):
    graph_tensor = tfgnn.GraphTensor.from_pieces(
        node_sets={
            "Person": tfgnn.NodeSet.from_fields(sizes=[2], features={"name": [b"Alice", b"Bob"]}),
            "Dog": tfgnn.NodeSet.from_fields(sizes=[1], features={"name": [b"Rex"]}),
        },
        edge_sets={
            "FRIEND": tfgnn.EdgeSet.from_fields(
                sizes=[1],
                adjacency=tfgnn.Adjacency.from_indices(
                    source=("Person", tf.constant([0])), target=("Person", tf.constant([1]))
                ),
            ),
            "PETS": tfgnn.EdgeSet.from_fields(
                sizes=[1],
                features={"bread": [b"Golden Retriever"]},
                adjacency=tfgnn.Adjacency.from_indices(
                    source=("Person", tf.constant([1])), target=("Dog", tf.constant([0]))
                ),
            ),
        },
    )
    for query in TFGNNTranslator().to_cypher_queries(graph_tensor):
        memgraph.execute(query)

    properties = []
    for node in memgraph.execute_and_fetch("MATCH (n: Person) RETURN properties(n)"):
        properties.append(node["properties(n)"])
    assert properties == [{"name": "Alice", "tfgnn_id": 0}, {"name": "Bob", "tfgnn_id": 1}]

    # ingest again to check that all nodes are merged and graph is not changed
    for query in TFGNNTranslator().to_cypher_queries(graph_tensor):
        memgraph.execute(query)

    new_properties = []
    for node in memgraph.execute_and_fetch("MATCH (n: Person) RETURN properties(n)"):
        new_properties.append(node["properties(n)"])
    assert new_properties == properties

    properties = []
    for node in memgraph.execute_and_fetch("MATCH (n: Dog) RETURN properties(n)"):
        properties.append(node["properties(n)"])
    assert properties == [{"name": "Rex", "tfgnn_id": 0}]

    properties_s = []
    properties_t = []
    for edge in memgraph.execute_and_fetch("MATCH (s)-[r:FRIEND]->(t) RETURN properties(s), properties(t)"):
        properties_s.append(edge["properties(s)"])
        properties_t.append(edge["properties(t)"])
    assert properties_s == [{"name": "Alice", "tfgnn_id": 0}]
    assert properties_t == [{"name": "Bob", "tfgnn_id": 1}]

    properties_s = []
    properties_r = []
    properties_t = []
    for edge in memgraph.execute_and_fetch(
        "MATCH (s)-[r:PETS]->(t) RETURN properties(s), properties(r), properties(t)"
    ):
        properties_s.append(edge["properties(s)"])
        properties_r.append(edge["properties(r)"])
        properties_t.append(edge["properties(t)"])
    assert properties_s == [{"name": "Bob", "tfgnn_id": 1}]
    assert properties_r == [{"bread": "Golden Retriever", "tfgnn_id": 0}]
    assert properties_t == [{"name": "Rex", "tfgnn_id": 0}]


def test_create_missing_properties(memgraph: Memgraph):
    graph_tensor = tfgnn.GraphTensor.from_pieces(
        node_sets={
            "Person": tfgnn.NodeSet.from_fields(
                sizes=[2],
                features={
                    "hobbies": tf.ragged.constant([[], [b"reading", b"gaming"]]),
                    "age": tf.ragged.constant([[25], []]),
                },
            )
        },
        edge_sets={
            "FRIEND": tfgnn.EdgeSet.from_fields(
                sizes=[1],
                adjacency=tfgnn.Adjacency.from_indices(
                    source=("Person", tf.constant([0])), target=("Person", tf.constant([1]))
                ),
            )
        },
    )
    for query in TFGNNTranslator().to_cypher_queries(graph_tensor):
        memgraph.execute(query)

    properties = []
    for node in memgraph.execute_and_fetch("MATCH (n) RETURN properties(n)"):
        properties.append(node["properties(n)"])

    assert properties == [{"age": [25], "tfgnn_id": 0}, {"hobbies": ["reading", "gaming"], "tfgnn_id": 1}]


def test_create_disjoined_nodes(memgraph: Memgraph):
    graph_tensor = tfgnn.GraphTensor.from_pieces(
        node_sets={"Person": tfgnn.NodeSet.from_fields(sizes=[2], features={"age": tf.ragged.constant([25, 45])})}
    )
    for query in TFGNNTranslator().to_cypher_queries(graph_tensor):
        memgraph.execute(query)

    result = memgraph.execute_and_fetch("MATCH (n) RETURN n")
    assert len(list(result)) == 0
