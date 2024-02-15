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

from gqlalchemy.exceptions import raise_if_not_imported
import gqlalchemy.memgraph_constants as mg_consts
from gqlalchemy.transformations.export.transporter import Transporter
from gqlalchemy.transformations.graph_type import GraphType

try:
    from gqlalchemy.transformations.translators.dgl_translator import DGLTranslator
except ModuleNotFoundError:
    DGLTranslator = None

from gqlalchemy.transformations.translators.nx_translator import NxTranslator

try:
    from gqlalchemy.transformations.translators.pyg_translator import PyGTranslator
except ModuleNotFoundError:
    PyGTranslator = None


class GraphTransporter(Transporter):
    """Here is a possible example for using this module:
    >>> transporter = GraphTransporter("dgl")
    graph = transporter.export()
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
        """Initializes GraphTransporter. It is used for converting Memgraph graph to the specific graph type offered by some Python package (PyG, DGL, NX...)
        Here is a possible example for using this module:
        >>> transporter = GraphTransporter("dgl")
        graph = transporter.export()
        Args:
            graph_type: dgl, pyg or nx
        """
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
            raise ValueError("Unknown export option. Currently supported are DGL, PyG and NetworkX.")

    def export(self):
        """Creates graph instance for the wanted export option."""
        return self.translator.get_instance()
