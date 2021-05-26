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

import networkx as nx
from gqlalchemy import Memgraph
from gqlalchemy.transformations import nx_to_cypher


def test_simple_nx_to_memgraph(memgraph: Memgraph):
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3])
    graph.add_edges_from([(1, 2), (1, 3)])

    for query in nx_to_cypher(graph):
        memgraph.execute_query(query)

    actual_nodes = list(memgraph.execute_and_fetch("MATCH (n) RETURN n ORDER BY n.id"))
    assert len(actual_nodes) == 3
    for i, node in enumerate(actual_nodes):
        assert node["n"].properties["id"] == i + 1
        assert node["n"].labels == set()

    actual_edges = list(memgraph.execute_and_fetch("MATCH ()-[e]->() RETURN e"))
    assert len(actual_edges) == 2
    for i, edge in enumerate(actual_edges):
        assert edge["e"].type == "TO"


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

    for query in nx_to_cypher(graph):
        memgraph.execute_query(query)

    actual_nodes = list(memgraph.execute_and_fetch("MATCH (n) RETURN n ORDER BY n.id"))
    assert len(actual_nodes) == 3
    for i, node in enumerate(actual_nodes):
        assert node["n"].properties["id"] == expected_nodes[i][0]
        if isinstance(expected_nodes[i][1]["labels"], (list, tuple)):
            assert node["n"].labels == set(expected_nodes[i][1]["labels"])
        else:
            assert node["n"].labels == {expected_nodes[i][1]["labels"]}
        assert node["n"].properties["num"] == expected_nodes[i][1]["num"]

    actual_edges = list(memgraph.execute_and_fetch("MATCH ()-[e]->() RETURN e"))
    assert len(actual_edges) == 2
    for i, edge in enumerate(actual_edges):
        assert edge["e"].type == expected_edges[i][2]["type"]
        assert edge["e"].properties["num"] == expected_edges[i][2]["num"]
