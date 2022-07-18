# Copyright (c) 2016-2022 Memgraph Ltd. [https://memgraph.com]
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

import networkx as nx
from gqlalchemy.transformations import nx_to_cypher, NoNetworkXConfigException, NetworkXCypherBuilder
from gqlalchemy.utilities import NetworkXCypherConfig


def test_nx_create_nodes():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2])
    expected_cypher_queries = [
        "CREATE ( {id: 1});",
        "CREATE ( {id: 2});",
    ]

    actual_cypher_queries = list(nx_to_cypher(graph))

    assert actual_cypher_queries == expected_cypher_queries


def test_nx_create_nodes_with_string():
    graph = nx.Graph()
    graph.add_nodes_from(
        [
            (1, {"id": "id1"}),
            (2, {"id": "id2"}),
        ]
    )
    expected_cypher_queries = [
        "CREATE ( {id: 'id1'});",
        "CREATE ( {id: 'id2'});",
    ]

    actual_cypher_queries = list(nx_to_cypher(graph))

    assert actual_cypher_queries == expected_cypher_queries


def test_nx_create_nodes_with_properties():
    graph = nx.Graph()
    graph.add_nodes_from(
        [
            (1, {"color": "blue", "labels": "L1"}),
            (2, {"age": 32}),
            (3, {"data": [1, 2, 3], "labels": ["L1", "L2", "L3"]}),
        ]
    )
    expected_cypher_queries = [
        "CREATE (:L1 {color: 'blue', id: 1});",
        "CREATE ( {age: 32, id: 2});",
        "CREATE (:L1:L2:L3 {data: [1, 2, 3], id: 3});",
    ]

    actual_cypher_queries = list(nx_to_cypher(graph))

    assert actual_cypher_queries == expected_cypher_queries


def test_nx_create_edges():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3])
    graph.add_edges_from([(1, 2), (2, 3)])
    expected_cypher_queries = [
        "CREATE ( {id: 1});",
        "CREATE ( {id: 2});",
        "CREATE ( {id: 3});",
        "MATCH (n {id: 1}), (m {id: 2}) CREATE (n)-[:TO ]->(m);",
        "MATCH (n {id: 2}), (m {id: 3}) CREATE (n)-[:TO ]->(m);",
    ]

    actual_cypher_queries = list(nx_to_cypher(graph))

    assert actual_cypher_queries == expected_cypher_queries


def test_nx_create_edges_with_string_ids():
    graph = nx.Graph()
    graph.add_nodes_from(
        [
            (1, {"id": "id1"}),
            (2, {"id": "id2"}),
            (3, {"id": "id3"}),
        ]
    )
    graph.add_edges_from([(1, 2), (2, 3)])
    expected_cypher_queries = [
        "CREATE ( {id: 'id1'});",
        "CREATE ( {id: 'id2'});",
        "CREATE ( {id: 'id3'});",
        "MATCH (n {id: 'id1'}), (m {id: 'id2'}) CREATE (n)-[:TO ]->(m);",
        "MATCH (n {id: 'id2'}), (m {id: 'id3'}) CREATE (n)-[:TO ]->(m);",
    ]

    actual_cypher_queries = list(nx_to_cypher(graph))

    assert actual_cypher_queries == expected_cypher_queries


def test_nx_create_edges_with_properties():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3])
    graph.add_edges_from([(1, 2, {"type": "TYPE1"}), (2, 3, {"type": "TYPE2", "data": "abc"})])
    expected_cypher_queries = [
        "CREATE ( {id: 1});",
        "CREATE ( {id: 2});",
        "CREATE ( {id: 3});",
        "MATCH (n {id: 1}), (m {id: 2}) CREATE (n)-[:TYPE1 ]->(m);",
        "MATCH (n {id: 2}), (m {id: 3}) CREATE (n)-[:TYPE2 {data: 'abc'}]->(m);",
    ]

    actual_cypher_queries = list(nx_to_cypher(graph))

    assert actual_cypher_queries == expected_cypher_queries


def test_nx_create_edge_and_node_with_properties():
    graph = nx.Graph()
    graph.add_nodes_from(
        [(1, {"labels": "Label1"}), (2, {"labels": ["Label1", "Label2"], "name": "name1"}), (3, {"labels": "Label1"})]
    )
    graph.add_edges_from([(1, 2, {"type": "TYPE1"}), (2, 3, {"type": "TYPE2", "data": "abc"})])
    expected_cypher_queries = [
        "CREATE (:Label1 {id: 1});",
        "CREATE (:Label1:Label2 {name: 'name1', id: 2});",
        "CREATE (:Label1 {id: 3});",
        "MATCH (n:Label1 {id: 1}), (m:Label1:Label2 {id: 2}) CREATE (n)-[:TYPE1 ]->(m);",
        "MATCH (n:Label1:Label2 {id: 2}), (m:Label1 {id: 3}) CREATE (n)-[:TYPE2 {data: 'abc'}]->(m);",
    ]

    actual_cypher_queries = list(nx_to_cypher(graph))

    assert actual_cypher_queries == expected_cypher_queries


def test_nx_create_edge_and_node_with_index():
    graph = nx.Graph()
    graph.add_nodes_from(
        [(1, {"labels": "Label1"}), (2, {"labels": ["Label1", "Label2"], "name": "name1"}), (3, {"labels": "Label1"})]
    )
    graph.add_edges_from([(1, 2, {"type": "TYPE1"}), (2, 3, {"type": "TYPE2", "data": "abc"})])
    expected_cypher_queries = [
        "CREATE (:Label1 {id: 1});",
        "CREATE (:Label1:Label2 {name: 'name1', id: 2});",
        "CREATE (:Label1 {id: 3});",
        "CREATE INDEX ON :Label2(id);",
        "CREATE INDEX ON :Label1(id);",
        "MATCH (n:Label1 {id: 1}), (m:Label1:Label2 {id: 2}) CREATE (n)-[:TYPE1 ]->(m);",
        "MATCH (n:Label1:Label2 {id: 2}), (m:Label1 {id: 3}) CREATE (n)-[:TYPE2 {data: 'abc'}]->(m);",
    ]

    actual_cypher_queries = list(nx_to_cypher(graph, NetworkXCypherConfig(create_index=True)))

    assert actual_cypher_queries[0:3] == expected_cypher_queries[0:3]
    assert set(actual_cypher_queries[3:5]) == set(expected_cypher_queries[3:5])
    assert actual_cypher_queries[5:7] == expected_cypher_queries[5:7]


def test_creating_builder_with_no_config_throws_exception():
    with pytest.raises(NoNetworkXConfigException):
        NetworkXCypherBuilder(None)
