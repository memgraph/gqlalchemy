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
from typing import List

from gqlalchemy import Memgraph, Node, Relationship


def compare_nodes(actual: List[Node], expected: List[Node]):
    actual.sort(key=lambda x: x.id)
    expected.sort(key=lambda x: x.id)

    for index, actual_object in enumerate(actual):
        assert actual_object._properties == expected[index]._properties


def compare_edges(actual: List[Relationship], expected: List[Relationship]):
    actual.sort(key=lambda x: x.id)
    expected.sort(key=lambda x: x.id)

    for index, actual_object in enumerate(actual):
        assert actual_object._properties == expected[index]._properties
        assert actual_object._start_node_id is not None
        assert actual_object._end_node_id is not None
        # assert actual_object.end_node.properties["id"] == expected[index].end_node.properties["id"]


@pytest.mark.parametrize("dataset_file", ["nodes_and_edges.cyp"])
def test_nodes_mapping(populated_memgraph: Memgraph):
    query = "MATCH (n) RETURN n"
    expected_nodes = [
        Node(
            _id=0,
            _node_labels={"Node"},
            id=0,
            name="name1",
        ),
        Node(
            _id=1,
            _node_labels={"Node"},
            id=1,
            data=[1, 2, 3],
        ),
        Node(
            _id=2,
            _node_labels={"Node"},
            id=2,
            data={"a": 1, "b": "abc"},
        ),
    ]

    actual_nodes = [r["n"] for r in populated_memgraph.execute_and_fetch(query)]

    compare_nodes(actual_nodes, expected_nodes)


@pytest.mark.parametrize("dataset_file", ["nodes_and_edges.cyp"])
def test_edges_mapping(populated_memgraph: Memgraph):
    query = "MATCH ()-[e]->() RETURN e"
    expected_edges = [
        Relationship(
            _id=0,
            _type="Relation",
            _start_node_id=0,
            _end_node_id=1,
            id=0,
            name="name1",
        ),
        Relationship(
            _id=1,
            _type="Relation",
            _start_node_id=1,
            _end_node_id=2,
            id=1,
            num=100,
        ),
        Relationship(
            _id=2,
            _type="Relation",
            _start_node_id=2,
            _end_node_id=0,
            id=2,
            data=[1, 2, 3],
        ),
    ]

    actual_edges = [r["e"] for r in populated_memgraph.execute_and_fetch(query)]

    compare_edges(actual_edges, expected_edges)


@pytest.mark.parametrize("dataset_file", ["path.cyp"])
def test_path_mapping(populated_memgraph: Memgraph):
    query = "MATCH p = ({id: 0})-[*]->({id: 3}) RETURN p"
    expected_nodes = [
        Node(_id=0, _node_labels={"Node"}, id=0),
        Node(_id=1, _node_labels={"Node"}, id=1),
        Node(_id=2, _node_labels={"Node"}, id=2),
        Node(_id=2, _node_labels={"Node"}, id=3),
    ]
    expected_relationships = [
        Relationship(
            _id=0,
            _type="Relation",
            _start_node_id=0,
            _end_node_id=1,
            id=0,
        ),
        Relationship(
            _id=1,
            _type="Relation",
            _start_node_id=1,
            _end_node_id=2,
            id=1,
        ),
        Relationship(
            _id=2,
            _type="Relation",
            _start_node_id=2,
            _end_node_id=3,
            id=2,
        ),
    ]

    actual_paths = [r["p"] for r in populated_memgraph.execute_and_fetch(query)]
    assert len(actual_paths) == 1
    actual_path = actual_paths[0]

    compare_nodes(actual_path._nodes, expected_nodes)
    compare_edges(actual_path._relationships, expected_relationships)
