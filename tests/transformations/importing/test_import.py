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


@pytest.mark.extras
@pytest.mark.dgl
def test_import_dgl():
    DGLTranslator = pytest.importorskip("gqlalchemy.transformations.translators.dgl_translator.DGLTranslator")

    importer = GraphImporter(graph_type="DGL")
    assert isinstance(importer.translator, DGLTranslator)
    importer.translate(None)  # it should fail safely no matter what


@pytest.mark.extras
@pytest.mark.pyg
def test_import_pyg():
    PyGTranslator = pytest.importorskip("gqlalchemy.transformations.translators.pyg_translator.PyGTranslator")

    importer = GraphImporter(graph_type="pyG")
    assert isinstance(importer.translator, PyGTranslator)
    importer.translate(None)  # it should fail safely no matter what


def test_import_nx():
    from gqlalchemy.transformations.translators.nx_translator import NxTranslator

    importer = GraphImporter(graph_type="Nx")
    assert isinstance(importer.translator, NxTranslator)
    importer.translate(None)  # it should fail safely no matter what
