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

import json

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


def test_import_nx_normalize_dot_properties_json_key_collision():
    importer = GraphImporter(graph_type="Nx")
    normalized_properties = importer._normalize_dot_properties({"json": "raw-value", "label": "A"})

    assert json.loads(normalized_properties["attributes_json"]) == {"json": "raw-value", "label": "A"}
    assert normalized_properties["attributes_json_attribute"] == "raw-value"
    assert normalized_properties["attributes_label"] == "A"


def test_import_nx_from_dot_data(monkeypatch):
    pytest.importorskip("pydot")

    importer = GraphImporter(graph_type="Nx")
    captured = {}

    def _capture_translate(graph):
        captured["graph"] = graph

    monkeypatch.setattr(importer, "translate", _capture_translate)

    importer.translate_dot_data(
        'digraph G { "A" [label="A", shape="ellipse", color="blue"]; "B"; "A" -> "B" [fontsize="10", style="dashed"]; "A" -> "B" [fontsize="10", style="dashed"]; }'
    )

    assert "graph" in captured
    assert captured["graph"].is_multigraph()
    assert captured["graph"].number_of_nodes() == 2
    assert captured["graph"].number_of_edges() == 2

    node_data = captured["graph"].nodes["A"]
    assert node_data["dot_type"] == "node"
    assert node_data["source_graph"] == "dot"
    assert node_data["display_name"] == "A"
    assert node_data["attributes_label"] == "A"
    assert node_data["attributes_shape"] == "ellipse"
    assert node_data["attributes_color"] == "blue"
    assert json.loads(node_data["attributes_json"]) == {"color": "blue", "label": "A", "shape": "ellipse"}

    node_b_data = captured["graph"].nodes["B"]
    assert node_b_data["dot_type"] == "node"
    assert node_b_data["display_name"] == "B"
    assert json.loads(node_b_data["attributes_json"]) == {}

    edge_data_list = [edge_data for *_, edge_data in captured["graph"].edges(data=True)]
    assert sorted(edge_data["id"] for edge_data in edge_data_list) == ["A->B", "A->B#1"]
    for edge_data in edge_data_list:
        assert edge_data["type"] == "DOT_EDGE"
        assert edge_data["dot_type"] == "edge"
        assert edge_data["points"] == ["A", "B"]
        assert edge_data["attributes_fontsize"] == "10"
        assert edge_data["attributes_style"] == "dashed"
        assert json.loads(edge_data["attributes_json"]) == {"fontsize": "10", "style": "dashed"}

    sequences = [data["sequence"] for _, data in captured["graph"].nodes(data=True)] + [
        data["sequence"] for *_, data in captured["graph"].edges(data=True)
    ]
    assert sorted(sequences) == [0, 1, 2, 3]


def test_import_nx_from_dot_file(tmp_path, monkeypatch):
    pytest.importorskip("pydot")

    importer = GraphImporter(graph_type="Nx")
    captured = {}
    dot_file = tmp_path / "graph.dot"
    dot_file.write_text(
        'digraph G { "S" [label="S", shape="ellipse"]; "T"; "S" -> "T" [fontsize="10"]; "S" -> "T" [fontsize="10"]; }'
    )

    def _capture_translate(graph):
        captured["graph"] = graph

    monkeypatch.setattr(importer, "translate", _capture_translate)

    importer.translate_dot_file(str(dot_file))

    assert "graph" in captured
    assert captured["graph"].is_multigraph()
    assert captured["graph"].number_of_nodes() == 2
    assert captured["graph"].number_of_edges() == 2
    edge_ids = sorted([edge_data["id"] for *_, edge_data in captured["graph"].edges(data=True)])
    assert edge_ids == ["S->T", "S->T#1"]
    assert captured["graph"].nodes["S"]["source_graph"] == "dot"
