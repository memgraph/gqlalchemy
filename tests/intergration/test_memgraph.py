# Copyright (c) 2016-2021 Memgraph Ltd. [https://memgraph.com]
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
from typing import List

import pytest
from gqlalchemy import Memgraph, Node, Relationship


def compare_nodes(actual: List[Node], expected: List[Node]):
    actual.sort(key=lambda x: x.properties["id"])
    expected.sort(key=lambda x: x.properties["id"])

    for index, actual_object in enumerate(actual):
        assert actual_object.properties == expected[index].properties


def compare_edges(actual: List[Relationship], expected: List[Relationship]):
    actual.sort(key=lambda x: x.properties["id"])
    expected.sort(key=lambda x: x.properties["id"])

    for index, actual_object in enumerate(actual):
        assert actual_object.properties == expected[index].properties
        assert actual_object.start_node is not None
        assert actual_object.end_node is not None
        # assert actual_object.end_node.properties["id"] == expected[index].end_node.properties["id"]


@pytest.mark.parametrize("dataset_file", ["nodes_and_edges.cyp"])
def test_nodes_mapping(populated_memgraph: Memgraph):
    query = "MATCH (n) RETURN n"
    expected_nodes = [
        Node(0, ["Node"], {"id": 0, "name": "name1"}),
        Node(1, ["Node"], {"id": 1, "data": [1, 2, 3]}),
        Node(2, ["Node"], {"id": 2, "data": {"a": 1, "b": "abc"}}),
    ]

    actual_nodes = [r["n"] for r in populated_memgraph.execute_and_fetch(query)]

    compare_nodes(actual_nodes, expected_nodes)


@pytest.mark.parametrize("dataset_file", ["nodes_and_edges.cyp"])
def test_edges_mapping(populated_memgraph: Memgraph):
    query = "MATCH ()-[e]->() RETURN e"
    expected_edges = [
        Relationship(0, "Relation", 0, 1, {"id": 0, "name": "name1"}),
        Relationship(1, "Relation", 1, 2, {"id": 1, "num": 100}),
        Relationship(2, "Relation", 2, 0, {"id": 2, "data": [1, 2, 3]}),
    ]

    actual_edges = [r["e"] for r in populated_memgraph.execute_and_fetch(query)]
    print(actual_edges)

    compare_edges(actual_edges, expected_edges)


@pytest.mark.parametrize("dataset_file", ["path.cyp"])
def test_path_mapping(populated_memgraph: Memgraph):
    query = "MATCH p = ({id: 0})-[*]->({id: 3}) RETURN p"
    expected_nodes = [
        Node(0, ["Node"], {"id": 0}),
        Node(1, ["Node"], {"id": 1}),
        Node(2, ["Node"], {"id": 2}),
        Node(2, ["Node"], {"id": 3}),
    ]
    expected_relationships = [
        Relationship(0, "Relation", 0, 1, {"id": 0}),
        Relationship(1, "Relation", 1, 2, {"id": 1}),
        Relationship(2, "Relation", 2, 3, {"id": 2}),
    ]

    actual_paths = [r["p"] for r in populated_memgraph.execute_and_fetch(query)]
    assert len(actual_paths) == 1
    actual_path = actual_paths[0]

    compare_nodes(actual_path.nodes, expected_nodes)
    compare_edges(actual_path.relationships, expected_relationships)
