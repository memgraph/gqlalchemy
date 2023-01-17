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

from gqlalchemy import Memgraph
from gqlalchemy.transformations.importing.importer import Importer
from gqlalchemy.transformations.translators.dgl_translator import DGLTranslator
from gqlalchemy.transformations.translators.nx_translator import NxTranslator
from gqlalchemy.transformations.translators.pyg_translator import PyGTranslator
from gqlalchemy.memgraph_constants import MG_HOST, MG_PORT, MG_USERNAME, MG_PASSWORD, MG_ENCRYPTED, MG_CLIENT_NAME, MG_LAZY

class GraphImporter(Importer):
    """Imports dgl, pyg or networkx graph representations to Memgraph.
    The following code will suffice for importing queries.
    >>> importer = GraphImporter("dgl")
    graph = DGLGraph(...)
    importer.translate(graph)  # queries are inserted in this step
    Args:
        graph_type: The type of the graph.
    """

    def __init__(self, graph_type: str,
        default_node_label = "NODE",
        default_edge_type = "RELATIONSHIP",
        host: str = MG_HOST,
        port: int = MG_PORT,
        username: str = MG_USERNAME,
        password: str = MG_PASSWORD,
        encrypted: bool = MG_ENCRYPTED,
        client_name: str = MG_CLIENT_NAME,
        lazy: bool = MG_LAZY,) -> None:
        super().__init__()
        self.graph_type = graph_type.lower()
        if self.graph_type == "dgl":
            self.translator = DGLTranslator(default_node_label, default_edge_type, host, port, username, password, encrypted, client_name, lazy)
        elif self.graph_type == "pyg":
            self.translator = PyGTranslator(default_node_label, default_edge_type, host, port, username, password, encrypted, client_name, lazy)
        elif self.graph_type == "nx":
            self.translator = NxTranslator(default_node_label, default_edge_type, host, port, username, password, encrypted, client_name, lazy)
        else:
            raise ValueError("Unknown import option. Currently supported are DGL, PyG and Networkx.")

    def translate(self, graph):
        """Gets cypher queries using the underlying translator and then inserts all queries to Memgraph DB.
        Args:
            graph: dgl, pytorch geometric or nx graph instance.
        """
        memgraph = Memgraph()
        for query in self.translator.to_cypher_queries(graph):
            memgraph.execute(query)
