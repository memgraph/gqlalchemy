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

from gqlalchemy.transformations.export.transporter import Transporter
from gqlalchemy.transformations.translators.dgl_translator import DGLTranslator
from gqlalchemy.transformations.translators.nx_translator import NxTranslator
from gqlalchemy.transformations.translators.pyg_translator import PyGTranslator

class GraphTransporter(Transporter):
    """Here is a possible example for using this module:
    >>> transporter = GraphTransported("dgl")
    graph = transporter.export()
    """

    def __init__(self, graph_type: str) -> None:
        """Initializes GraphTransporter. It is used for converting Memgraph graph to the specific graph type offered by some Python package (PyG, DGL, NX...)
        Here is a possible example for using this module:
        >>> transporter = GraphTransported("dgl")
        graph = transporter.export()
        Args:
            graph_type: dgl, pyg or nx
        """
        super().__init__()
        self.graph_type = graph_type.lower()
        if self.graph_type == "dgl":
            self.translator = DGLTranslator()
        elif self.graph_type == "pyg":
            self.translator = PyGTranslator()
        elif self.graph_type == "nx":
            self.translator = NxTranslator()
        else:
            raise ValueError("Unknown export option. Currently supported are DGL, PyG and Networkx.")

    def export(self):
        """Creates graph instance for the wanted export option.
        """
        return self.translator.get_instance()
