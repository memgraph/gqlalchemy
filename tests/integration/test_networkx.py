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
from random import randint

import networkx as nx

from gqlalchemy import Memgraph
from gqlalchemy.models import MemgraphIndex
from gqlalchemy.transformations.translators.nx_translator import NxTranslator
from gqlalchemy.utilities import NetworkXCypherConfig


@pytest.fixture
def random_nx_graph(number_of_nodes=100000, number_of_edges=150000) -> nx.Graph:
    graph = nx.Graph()
    for i in range(number_of_nodes):
        graph.add_node(i, labels="Label")
    for _ in range(number_of_edges):
        graph.add_edge(randint(0, number_of_nodes), randint(0, number_of_nodes))

    return graph


@pytest.fixture
def big_random_nx_graph(number_of_nodes=200000, number_of_edges=1000000) -> nx.Graph:
    graph = nx.Graph()
    for i in range(number_of_nodes):
        graph.add_node(i, labels="Label")
    for _ in range(number_of_edges):
        graph.add_edge(randint(0, number_of_nodes), randint(0, number_of_nodes))

    return graph


def test_simple_nx_to_memgraph(memgraph: Memgraph):
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3])
    graph.add_edges_from([(1, 2), (1, 3)])

    translator = NxTranslator()
    for query in translator.to_cypher_queries(graph):
        memgraph.execute(query)

    actual_nodes = list(memgraph.execute_and_fetch("MATCH (n) RETURN n ORDER BY n.id"))
    assert len(actual_nodes) == 3
    for i, node in enumerate(actual_nodes):
        assert node["n"]._properties["id"] == i + 1
        assert node["n"]._labels == set()

    actual_edges = list(memgraph.execute_and_fetch("MATCH ()-[e]->() RETURN e"))
    assert len(actual_edges) == 2
    for i, edge in enumerate(actual_edges):
        assert edge["e"]._type == "TO"


def test_simple_index_nx_to_memgraph(memgraph: Memgraph):
    graph = nx.Graph()
    graph.add_nodes_from(
        [
            (1, {"labels": "L1", "num": 123}),
            (2, {"labels": "L1", "num": 123}),
            (3, {"labels": ["L1", "L2", "L3"], "num": 123}),
        ]
    )
    graph.add_edges_from([(1, 2), (1, 3)])
    expected_indexes = {
        MemgraphIndex("L1", "id"),
        MemgraphIndex("L2", "id"),
        MemgraphIndex("L3", "id"),
    }

    translator = NxTranslator()
    for query in translator.to_cypher_queries(graph, NetworkXCypherConfig(create_index=True)):
        memgraph.execute(query)
    actual_indexes = set(memgraph.get_indexes())

    assert actual_indexes == expected_indexes


def test_nx_to_memgraph(memgraph: Memgraph):
    graph = nx.Graph()
    expected_nodes = [
        (1, {"labels": "L1", "num": 123}),
        (2, {"labels": "L1", "num": 123}),
        (3, {"labels": ["L1", "L2", "L3"], "num": 123}),
    ]
    expected_edges = [(1, 2, {"type": "E1", "num": 3.14}), (1, 3, {"type": "E2", "num": 123})]
    graph.add_nodes_from(expected_nodes)
    graph.add_edges_from(expected_edges)

    translator = NxTranslator()
    for query in translator.to_cypher_queries(graph):
        memgraph.execute(query)

    actual_nodes = list(memgraph.execute_and_fetch("MATCH (n) RETURN n ORDER BY n.id"))
    assert len(actual_nodes) == 3
    for i, node in enumerate(actual_nodes):
        assert node["n"]._properties["id"] == expected_nodes[i][0]
        if isinstance(expected_nodes[i][1]["labels"], (list, tuple)):
            assert node["n"]._labels == set(expected_nodes[i][1]["labels"])
        else:
            assert node["n"]._labels == {expected_nodes[i][1]["labels"]}
        assert node["n"]._properties["num"] == expected_nodes[i][1]["num"]

    actual_edges = list(memgraph.execute_and_fetch("MATCH ()-[e]->() RETURN e"))
    assert len(actual_edges) == 2
    for i, edge in enumerate(actual_edges):
        assert edge["e"]._type == expected_edges[i][2]["type"]
        assert edge["e"]._properties["num"] == expected_edges[i][2]["num"]


@pytest.mark.timeout(60)
@pytest.mark.slow
def test_big_nx_to_memgraph_with_manual_index(memgraph: Memgraph, random_nx_graph: nx.Graph):
    memgraph.create_index(MemgraphIndex("Label", "id"))

    translator = NxTranslator()
    for query in translator.to_cypher_queries(random_nx_graph):
        memgraph.execute(query)


@pytest.mark.timeout(60)
@pytest.mark.slow
def test_big_nx_to_memgraph(memgraph: Memgraph, random_nx_graph: nx.Graph):
    translator = NxTranslator()
    for query in translator.to_cypher_queries(random_nx_graph, NetworkXCypherConfig(create_index=True)):
        memgraph.execute(query)


@pytest.mark.timeout(240)
@pytest.mark.slow
def test_huge_nx_to_memgraph_parallel_with_index(memgraph: Memgraph, big_random_nx_graph: nx.Graph):
    memgraph.create_index(MemgraphIndex("Label", "id"))
    translator = NxTranslator()
    translator.nx_graph_to_memgraph_parallel(big_random_nx_graph)
