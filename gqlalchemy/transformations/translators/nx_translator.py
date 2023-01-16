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

from typing import Iterator, List, Dict, Any, Union
import logging
import multiprocessing as mp

import networkx as nx
import mgclient


from gqlalchemy import Memgraph
from gqlalchemy.transformations.constants import LABEL, EDGE_TYPE
from gqlalchemy.transformations.translators.translator import Translator
from gqlalchemy import Match
from gqlalchemy.models import Node, Relationship, MemgraphIndex
from gqlalchemy.utilities import NetworkXCypherConfig, to_cypher_labels, to_cypher_properties, to_cypher_value


class NetworkXGraphConstants:
    LABELS = "labels"
    TYPE = "type"
    ID = "id"


class NetworkXCypherBuilder:
    def __init__(self, config: NetworkXCypherConfig):
        if config is None:
            raise NoNetworkXConfigException("No NetworkX configuration provided!")

        self._config = config

    def yield_queries(self, graph: nx.Graph) -> Iterator[str]:
        """Generates Cypher queries for creating a graph."""

        if self._config.create_index:
            yield from self._nx_nodes_to_cypher_with_index(graph)
        else:
            yield from self._nx_nodes_to_cypher(graph)
        yield from self._nx_edges_to_cypher(graph)

    def yield_query_groups(self, graph: nx.Graph) -> List[Iterator[str]]:
        """Generates Cypher queries for creating a graph by query groups."""

        query_groups = []

        if self._config.create_index:
            query_groups.append(self._nx_nodes_to_cypher_with_index(graph))
        else:
            query_groups.append(self._nx_nodes_to_cypher(graph))

        query_groups.append(self._nx_edges_to_cypher(graph))

        return query_groups

    def _nx_nodes_to_cypher(self, graph: nx.Graph) -> Iterator[str]:
        """Generates Cypher queries for creating nodes."""
        for nx_id, data in graph.nodes(data=True):
            yield self._create_node(nx_id, data)

    def _nx_nodes_to_cypher_with_index(self, graph: nx.Graph) -> Iterator[str]:
        """Generates Cypher queries for creating nodes and indexes."""
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
        """Generates Cypher queries for creating edges."""
        for n1, n2, data in graph.edges(data=True):
            from_label = graph.nodes[n1].get(NetworkXGraphConstants.LABELS, "")
            to_label = graph.nodes[n2].get(NetworkXGraphConstants.LABELS, "")

            n1_id = graph.nodes[n1].get(NetworkXGraphConstants.ID, n1)
            n2_id = graph.nodes[n2].get(NetworkXGraphConstants.ID, n2)
            yield self._create_edge(n1_id, n2_id, from_label, to_label, data)

    def _create_node(self, nx_id: int, properties: Dict[str, Any]) -> str:
        """Returns Cypher query for node creation."""
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
        """Returns Cypher query for index creation."""
        index = MemgraphIndex(label, property)
        return f"CREATE INDEX ON {index.to_cypher()}(id);"


class NoNetworkXConfigException(Exception):
    pass


class NxTranslator(Translator):
    """Uses original ids from Memgraph. Labels are encoded as properties. Since Networkx allows
    that nodes have properties of different dimensionality, this modules makes use of it and stores properties
    as dictionary entries. All properties are saved to Networkx data structure.
    """

    # TODO: maybe we would like to have specific `weight` property for out users
    def __init__(self, default_node_label="NODE", default_edge_type="RELATIONSHIP") -> None:
        super().__init__(default_node_label, default_edge_type)
        self.__all__ = ("nx_to_cypher", "nx_graph_to_memgraph_parallel")

    def to_cypher_queries(self, graph: nx.Graph, config: NetworkXCypherConfig = None) -> Iterator[str]:
        """Generates a Cypher query for creating a graph."""

        if config is None:
            config = NetworkXCypherConfig()

        builder = NetworkXCypherBuilder(config=config)

        yield from builder.yield_queries(graph)

    def nx_graph_to_memgraph_parallel(
        self,
        graph: nx.Graph,
        host: str = "127.0.0.1",
        port: int = 7687,
        username: str = "",
        password: str = "",
        encrypted: bool = False,
        config: NetworkXCypherConfig = None,
    ) -> None:
        """Generates Cypher queries and inserts data into Memgraph in parallel."""
        if config is None:
            config = NetworkXCypherConfig()

        builder = NetworkXCypherBuilder(config=config)
        query_groups = builder.yield_query_groups(graph)

        if not config.create_index:
            self._check_for_index_hint(
                host,
                port,
                username,
                password,
                encrypted,
            )

        for query_group in query_groups:
            self._start_parallel_execution(query_group, host, port, username, password, encrypted)

    def _start_parallel_execution(
        self, queries_gen: Iterator[str], host: str, port: int, username: str, password: str, encrypted: bool
    ) -> None:
        num_of_processes = mp.cpu_count() // 2
        queries = list(queries_gen)
        chunk_size = len(queries) // num_of_processes
        processes = []

        for i in range(num_of_processes):
            process_queries = queries[i * chunk_size : chunk_size * (i + 1)]
            processes.append(
                mp.Process(
                    target=self._insert_queries,
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

    def _insert_queries(
        self, queries: List[str], host: str, port: int, username: str, password: str, encrypted: bool
    ) -> None:
        """Used by multiprocess insertion of nx into memgraph, works on a chunk of queries."""
        memgraph = Memgraph(host, port, username, password, encrypted)
        while len(queries) > 0:
            try:
                query = queries.pop()
                memgraph.execute(query)
            except mgclient.DatabaseError as e:
                queries.append(query)
                logging.getLogger(__file__).warning(f"Ignoring database error: {e}")
                continue

    def _check_for_index_hint(
        self,
        host: str = "127.0.0.1",
        port: int = 7687,
        username: str = "",
        password: str = "",
        encrypted: bool = False,
    ):
        """Check if the there are indexes, if not show warnings."""
        memgraph = Memgraph(host, port, username, password, encrypted)
        indexes = memgraph.get_indexes()
        if len(indexes) == 0:
            logging.getLogger(__file__).warning(
                "Be careful you do not have any indexes set up, the queries will take longer than expected!"
            )

    def get_instance(self):
        """Creates Networx instance of the graph from the data residing inside Memgraph. Since Networkx doesn't support labels in a way Memgraph does, labels
        are encoded as a node and edge properties.
        """
        # Get all nodes and edges from the database
        query_results = Match().node(variable="n").to(variable="r").node(variable="m").return_().execute()

        # Data structures
        graph_data = []  # List[Tuple[source_node_id, dest_node_id]]
        node_info = dict()  # Dict[id, Dict[prop: value]]
        edge_info = dict()  # Dict[(source_node_id, dest_node_id), Dict[prop: value]]

        # Parse each row from query results
        for row in query_results:
            row_values = row.values()
            for entity in row_values:
                entity_properties = entity._properties
                if isinstance(entity, Node) and entity._id not in node_info:
                    entity_properties[LABEL] = Translator.merge_labels(entity._labels, self.default_node_label)
                    node_info[entity._id] = entity_properties
                elif isinstance(entity, Relationship):
                    entity_properties[EDGE_TYPE] = entity._type if entity._type else self.default_edge_type
                    edge_info[(entity._start_node_id, entity._end_node_id)] = entity_properties
                    graph_data.append((entity._start_node_id, entity._end_node_id))

        # Create Nx graph
        graph = nx.DiGraph(graph_data)
        nx.set_node_attributes(graph, node_info)
        nx.set_edge_attributes(graph, edge_info)
        return graph
