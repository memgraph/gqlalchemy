# Copyright (c) 2016-2023 Memgraph Ltd. [https://memgraph.com]
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

from gqlalchemy import Memgraph
from gqlalchemy.transformations.graph_type import GraphType
from gqlalchemy.transformations.importing.importer import Importer

from gqlalchemy.exceptions import raise_if_not_imported
import gqlalchemy.memgraph_constants as mg_consts
import networkx as nx
import json
import re
from collections import defaultdict
from typing import Any, Dict

try:
    from gqlalchemy.transformations.translators.dgl_translator import DGLTranslator
except ModuleNotFoundError:
    DGLTranslator = None

from gqlalchemy.transformations.translators.nx_translator import NxTranslator

try:
    from gqlalchemy.transformations.translators.pyg_translator import PyGTranslator
except ModuleNotFoundError:
    PyGTranslator = None

try:
    import pydot
except ModuleNotFoundError:
    pydot = None


class GraphImporter(Importer):
    """Imports dgl, pyg or networkx graph representations to Memgraph.
    The following code will suffice for importing queries.
    >>> importer = GraphImporter("dgl")
    graph = DGLGraph(...)
    importer.translate(graph)  # queries are inserted in this step
    Args:
        graph_type: The type of the graph.
    """

    def __init__(
        self,
        graph_type: str,
        host: str = mg_consts.MG_HOST,
        port: int = mg_consts.MG_PORT,
        username: str = mg_consts.MG_USERNAME,
        password: str = mg_consts.MG_PASSWORD,
        encrypted: bool = mg_consts.MG_ENCRYPTED,
        client_name: str = mg_consts.MG_CLIENT_NAME,
        lazy: bool = mg_consts.MG_LAZY,
    ) -> None:
        super().__init__()
        self.graph_type = graph_type.upper()
        if self.graph_type == GraphType.DGL.name:
            raise_if_not_imported(dependency=DGLTranslator, dependency_name="dgl")
            self.translator = DGLTranslator(host, port, username, password, encrypted, client_name, lazy)
        elif self.graph_type == GraphType.PYG.name:
            raise_if_not_imported(dependency=PyGTranslator, dependency_name="torch_geometric")
            self.translator = PyGTranslator(host, port, username, password, encrypted, client_name, lazy)
        elif self.graph_type == GraphType.NX.name:
            self.translator = NxTranslator(host, port, username, password, encrypted, client_name, lazy)
        else:
            raise ValueError("Unknown import option. Currently supported options are: DGL, PyG and NetworkX.")

    def translate(self, graph) -> None:
        """Gets cypher queries using the underlying translator and then inserts all queries to Memgraph DB.
        Args:
            graph: dgl, pytorch geometric or nx graph instance.
        """
        memgraph = Memgraph()
        for query in self.translator.to_cypher_queries(graph):
            memgraph.execute(query)

    def translate_dot_file(self, path: str) -> None:
        """Parses a DOT file to a NetworkX graph and imports it to Memgraph."""
        self._raise_if_not_nx_importer()
        raise_if_not_imported(dependency=pydot, dependency_name="pydot")

        pydot_graphs = pydot.graph_from_dot_file(path)
        if not pydot_graphs:
            raise ValueError("Unable to parse DOT file.")

        graph = self._normalize_dot_graph(self._graph_from_pydot(pydot_graphs[0]))
        self.translate(graph)

    def translate_dot_data(self, dot_data: str) -> None:
        """Parses DOT content to a NetworkX graph and imports it to Memgraph."""
        self._raise_if_not_nx_importer()
        raise_if_not_imported(dependency=pydot, dependency_name="pydot")

        pydot_graphs = pydot.graph_from_dot_data(dot_data)
        if not pydot_graphs:
            raise ValueError("Unable to parse DOT data.")

        graph = self._normalize_dot_graph(self._graph_from_pydot(pydot_graphs[0]))
        self.translate(graph)

    def _raise_if_not_nx_importer(self) -> None:
        if self.graph_type != GraphType.NX.name:
            raise ValueError("DOT import is supported only for NetworkX graph importer.")

    def _normalize_dot_graph(self, graph: nx.Graph) -> nx.Graph:
        """Enriches raw DOT graphs with stable, Cypher-friendly metadata."""
        normalized_graph = graph.__class__()
        edge_ids = defaultdict(int)
        sequence = 0

        for node_id, data in graph.nodes(data=True):
            node_properties = self._normalize_dot_properties(data)
            node_properties["dot_type"] = "node"
            node_properties["display_name"] = node_properties.get("attributes_label", str(node_id))
            node_properties["source_graph"] = "dot"
            node_properties["sequence"] = sequence
            sequence += 1
            if "id" not in node_properties:
                node_properties["id"] = self._normalize_dot_value(node_id)
            normalized_graph.add_node(node_id, **node_properties)

        if graph.is_multigraph():
            edge_iter = graph.edges(data=True, keys=True)
            for source, dest, _edge_key, data in edge_iter:
                edge_properties = self._normalize_dot_properties(data)
                edge_properties["dot_type"] = "edge"
                edge_properties["type"] = "DOT_EDGE"
                edge_key = f"{source}->{dest}"
                edge_index = edge_ids[edge_key]
                edge_ids[edge_key] += 1
                edge_id = edge_key if edge_index == 0 else f"{edge_key}#{edge_index}"
                edge_properties["id"] = self._normalize_dot_value(edge_id)
                edge_properties["points"] = [self._normalize_dot_value(source), self._normalize_dot_value(dest)]
                edge_properties["sequence"] = sequence
                sequence += 1
                normalized_graph.add_edge(source, dest, **edge_properties)
        else:
            edge_iter = graph.edges(data=True)
            for source, dest, data in edge_iter:
                edge_properties = self._normalize_dot_properties(data)
                edge_properties["dot_type"] = "edge"
                edge_properties["type"] = "DOT_EDGE"
                edge_key = f"{source}->{dest}"
                edge_index = edge_ids[edge_key]
                edge_ids[edge_key] += 1
                edge_id = edge_key if edge_index == 0 else f"{edge_key}#{edge_index}"
                edge_properties["id"] = self._normalize_dot_value(edge_id)
                edge_properties["points"] = [self._normalize_dot_value(source), self._normalize_dot_value(dest)]
                edge_properties["sequence"] = sequence
                sequence += 1
                normalized_graph.add_edge(source, dest, **edge_properties)

        return normalized_graph

    def _graph_from_pydot(self, dot_graph) -> nx.MultiDiGraph:
        """Builds a MultiDiGraph from a pydot graph without using nx.nx_pydot."""
        graph = nx.MultiDiGraph()

        def _walk(current_graph) -> None:
            for node in current_graph.get_nodes():
                node_id = self._normalize_dot_value(node.get_name())
                # Ignore pydot/graphviz pseudo-nodes used for defaults.
                if node_id in {"", "node", "edge", "graph"}:
                    continue

                properties = {
                    self._sanitize_property_key(key): self._normalize_dot_value(value)
                    for key, value in (node.get_attributes() or {}).items()
                }
                if node_id in graph.nodes:
                    graph.nodes[node_id].update(properties)
                else:
                    graph.add_node(node_id, **properties)

            for edge in current_graph.get_edges():
                source = self._normalize_dot_value(edge.get_source())
                dest = self._normalize_dot_value(edge.get_destination())
                if not source or not dest:
                    continue

                properties = {
                    self._sanitize_property_key(key): self._normalize_dot_value(value)
                    for key, value in (edge.get_attributes() or {}).items()
                }
                graph.add_edge(source, dest, **properties)

            for subgraph in current_graph.get_subgraphs():
                _walk(subgraph)

        _walk(dot_graph)

        return graph

    def _normalize_dot_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        normalized_attributes = {
            self._sanitize_property_key(key): self._normalize_dot_value(value) for key, value in properties.items()
        }
        normalized_properties: Dict[str, Any] = dict(normalized_attributes)
        normalized_properties["attributes_json"] = json.dumps(normalized_attributes, sort_keys=True)

        for key, value in normalized_attributes.items():
            normalized_properties[f"attributes_{key}"] = value

        return normalized_properties

    @staticmethod
    def _normalize_dot_value(value: Any) -> Any:
        if isinstance(value, str):
            return value.strip().strip('"')
        return value

    @staticmethod
    def _sanitize_property_key(key: str) -> str:
        return re.sub(r"[^0-9A-Za-z_]", "_", key)
