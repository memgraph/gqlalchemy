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

from typing import Any, Dict, Iterator

import networkx as nx

from gqlalchemy.utilities import to_cypher_labels, to_cypher_properties

__all__ = (
    "nx_to_cypher",
    "nx_edges_to_cypher",
    "nx_nodes_to_cypher",
)


def nx_nodes_to_cypher(graph: nx.Graph) -> Iterator[str]:
    """Generates a Cypher queries for creating nodes"""
    for nx_id, data in graph.nodes(data=True):
        yield _create_node(nx_id, data)


def nx_edges_to_cypher(graph: nx.Graph) -> Iterator[str]:
    """Generates a Cypher queries for creating edges"""
    for n1, n2, data in graph.edges(data=True):
        yield _create_edge(n1, n2, data)


def nx_to_cypher(graph: nx.Graph) -> Iterator[str]:
    """Generates a Cypher queries for creating graph"""

    yield from nx_nodes_to_cypher(graph)
    yield from nx_edges_to_cypher(graph)


def _create_node(nx_id: int, properties: Dict[str, Any]) -> str:
    """Returns Cypher query for node creation"""
    if "id" not in properties:
        properties["id"] = nx_id
    labels_str = to_cypher_labels(properties.pop("labels", ""))
    properties_str = to_cypher_properties(properties)

    return f"CREATE ({labels_str} {properties_str});"


def _create_edge(from_id: int, to_id: int, properties: Dict[str, Any]) -> str:
    """Returns Cypher query for edge creation."""
    edge_type = to_cypher_labels(properties.get("type", "TO"))
    properties.pop("type", None)
    properties_str = to_cypher_properties(properties)

    return f"MATCH (n {{id: {from_id}}}), (m {{id: {to_id}}}) CREATE (n)-[{edge_type} {properties_str}]->(m);"
