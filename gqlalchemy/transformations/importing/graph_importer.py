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

try:
    from gqlalchemy.transformations.translators.dgl_translator import DGLTranslator
except ModuleNotFoundError:
    DGLTranslator = None

from gqlalchemy.transformations.translators.nx_translator import NxTranslator

try:
    from gqlalchemy.transformations.translators.pyg_translator import PyGTranslator
except ModuleNotFoundError:
    PyGTranslator = None


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
