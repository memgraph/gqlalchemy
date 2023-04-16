import pytest

GraphTransporter = pytest.importorskip("gqlalchemy.transformations.export.graph_transporter.GraphTransporter")
DGLTranslator = pytest.importorskip("gqlalchemy.transformations.translators.dgl_translator.DGLTranslator")
NxTranslator = pytest.importorskip("gqlalchemy.transformations.translators.nx_translator.NxTranslator")
PyGTranslator = pytest.importorskip("gqlalchemy.transformations.translators.pyg_translator.PyGTranslator")


@pytest.mark.extras
@pytest.mark.parametrize(
    "graph_type, translator_type", [("DGL", DGLTranslator), ("pyG", PyGTranslator), ("Nx", NxTranslator)]
)
def test_export_selection_strategy(graph_type, translator_type):
    transporter = GraphTransporter(graph_type)
    assert isinstance(transporter.translator, translator_type)
    transporter.export()  # even with empty graph we should check that something doesn't fail
