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

import logging
import multiprocessing as mp
from typing import Any, Dict, Iterator, List, Union

import mgclient
import networkx as nx

from gqlalchemy import Memgraph
from gqlalchemy.models import MemgraphIndex
from gqlalchemy.utilities import to_cypher_labels, to_cypher_properties, to_cypher_value, NetworkXCypherConfig

__all__ = ("nx_to_cypher", "nx_graph_to_memgraph_parallel")


class NetworkXGraphConstants:
    LABELS = "labels"
    TYPE = "type"
    ID = "id"


def nx_to_cypher(graph: nx.Graph, config: NetworkXCypherConfig = None) -> Iterator[str]:
    """Generates a Cypher queries for creating graph"""

    if config is None:
        config = NetworkXCypherConfig()

    builder = NetworkXCypherBuilder(config=config)

    yield from builder.yield_queries(graph)


def nx_graph_to_memgraph_parallel(
    graph: nx.Graph,
    host: str = "127.0.0.1",
    port: int = 7687,
    username: str = "",
    password: str = "",
    encrypted: bool = False,
    config: NetworkXCypherConfig = None,
) -> None:
    """Generates a Cypher queries and inserts data into Memgraph in parallel"""
    if config is None:
        config = NetworkXCypherConfig()

    builder = NetworkXCypherBuilder(config=config)
    query_groups = builder.yield_query_groups(graph)

    if not config.create_index:
        _check_for_index_hint(
            host,
            port,
            username,
            password,
            encrypted,
        )

    for query_group in query_groups:
        _start_parallel_execution(query_group, host, port, username, password, encrypted)


def _start_parallel_execution(
    queries_gen: Iterator[str], host: str, port: int, username: str, password: str, encrypted: bool
) -> None:
    num_of_processes = mp.cpu_count() // 2
    queries = list(queries_gen)
    chunk_size = len(queries) // num_of_processes
    processes = []

    for i in range(num_of_processes):
        process_queries = queries[i * chunk_size : chunk_size * (i + 1)]
        processes.append(
            mp.Process(
                target=_insert_queries,
                args=(
                    process_queries,
                    host,
                    port,
                    username,
                    password,
                    encrypted,
                ),
            )
        )
    for p in processes:
        p.start()
    for p in processes:
        p.join()


def _check_for_index_hint(
    host: str = "127.0.0.1",
    port: int = 7687,
    username: str = "",
    password: str = "",
    encrypted: bool = False,
):
    """Check if the there are indexes, if not show warnings"""
    memgraph = Memgraph(host, port, username, password, encrypted)
    indexes = memgraph.get_indexes()
    if len(indexes) == 0:
        logging.getLogger(__file__).warning(
            "Be careful you do not have any indexes set up, the queries will take longer than expected!"
        )


def _insert_queries(queries: List[str], host: str, port: int, username: str, password: str, encrypted: bool) -> None:
    """Used by multiprocess insertion of nx into memgraph, works on a chunk of queries"""
    memgraph = Memgraph(host, port, username, password, encrypted)
    while len(queries) > 0:
        try:
            query = queries.pop()
            memgraph.execute(query)
        except mgclient.DatabaseError as e:
            queries.append(query)
            logging.getLogger(__file__).warning(f"Ignoring database error: {e}")
            continue


class NetworkXCypherBuilder:
    def __init__(self, config: NetworkXCypherConfig):
        if config is None:
            raise NoNetworkXConfigException("No NetworkX configuration provided!")

        self._config = config

    def yield_queries(self, graph: nx.Graph) -> Iterator[str]:
        """Generates a Cypher queries for creating graph"""

        if self._config.create_index:
            yield from self._nx_nodes_to_cypher_with_index(graph)
        else:
            yield from self._nx_nodes_to_cypher(graph)
        yield from self._nx_edges_to_cypher(graph)

    def yield_query_groups(self, graph: nx.Graph) -> List[Iterator[str]]:
        """Generates a Cypher queries for creating graph by query groups"""

        query_groups = []

        if self._config.create_index:
            query_groups.append(self._nx_nodes_to_cypher_with_index(graph))
        else:
            query_groups.append(self._nx_nodes_to_cypher(graph))

        query_groups.append(self._nx_edges_to_cypher(graph))

        return query_groups

    def _nx_nodes_to_cypher(self, graph: nx.Graph) -> Iterator[str]:
        """Generates a Cypher queries for creating nodes"""
        for nx_id, data in graph.nodes(data=True):
            yield self._create_node(nx_id, data)

    def _nx_nodes_to_cypher_with_index(self, graph: nx.Graph) -> Iterator[str]:
        """Generates a Cypher queries for creating nodes and indexes"""
        labels = set()
        for nx_id, data in graph.nodes(data=True):
            node_labels = data.get(NetworkXGraphConstants.LABELS, None)
            if isinstance(node_labels, (list, set)):
                labels |= set(node_labels)
            else:
                labels.add(node_labels)
            yield self._create_node(nx_id, data)
        labels.discard(None)
        for label in labels:
            yield self._create_index(label)

    def _nx_edges_to_cypher(self, graph: nx.Graph) -> Iterator[str]:
        """Generates a Cypher queries for creating edges"""
        for n1, n2, data in graph.edges(data=True):
            from_label = graph.nodes[n1].get(NetworkXGraphConstants.LABELS, "")
            to_label = graph.nodes[n2].get(NetworkXGraphConstants.LABELS, "")

            n1_id = graph.nodes[n1].get(NetworkXGraphConstants.ID, n1)
            n2_id = graph.nodes[n2].get(NetworkXGraphConstants.ID, n2)
            yield self._create_edge(n1_id, n2_id, from_label, to_label, data)

    def _create_node(self, nx_id: int, properties: Dict[str, Any]) -> str:
        """Returns Cypher query for node creation"""
        if "id" not in properties:
            properties["id"] = nx_id
        labels_str = to_cypher_labels(properties.get(NetworkXGraphConstants.LABELS, ""))
        properties_without_labels = {k: v for k, v in properties.items() if k != NetworkXGraphConstants.LABELS}
        properties_str = to_cypher_properties(properties_without_labels, self._config)

        return f"CREATE ({labels_str} {properties_str});"

    def _create_edge(
        self,
        from_id: Union[int, str],
        to_id: Union[int, str],
        from_label: Union[str, List[str]],
        to_label: Union[str, List[str]],
        properties: Dict[str, Any],
    ) -> str:
        """Returns Cypher query for edge creation."""
        edge_type = to_cypher_labels(properties.get(NetworkXGraphConstants.TYPE, "TO"))
        properties.pop(NetworkXGraphConstants.TYPE, None)
        properties_str = to_cypher_properties(properties, self._config)
        from_label_str = to_cypher_labels(from_label)
        to_label_str = to_cypher_labels(to_label)
        from_id_str = to_cypher_value(from_id)
        to_id_str = to_cypher_value(to_id)

        return f"MATCH (n{from_label_str} {{id: {from_id_str}}}), (m{to_label_str} {{id: {to_id_str}}}) CREATE (n)-[{edge_type} {properties_str}]->(m);"

    def _create_index(self, label: str, property: str = None):
        """Returns Cypher query for index creation"""
        index = MemgraphIndex(label, property)
        return f"CREATE INDEX ON {index.to_cypher()}(id);"


class NoNetworkXConfigException(Exception):
    pass
