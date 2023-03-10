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

from gqlalchemy.transformations.importing.graph_importer import GraphImporter
from gqlalchemy.transformations.translators.dgl_translator import DGLTranslator
from gqlalchemy.transformations.translators.pyg_translator import PyGTranslator
from gqlalchemy.transformations.translators.nx_translator import NxTranslator


@pytest.mark.parametrize(
    "graph_type, translator_type", [("DGL", DGLTranslator), ("pyG", PyGTranslator), ("Nx", NxTranslator)]
)
def test_import_selection_strategy(graph_type, translator_type):
    importer = GraphImporter(graph_type)
    assert isinstance(importer.translator, translator_type)
    importer.translate(None)  # it should fail safely no matter what
