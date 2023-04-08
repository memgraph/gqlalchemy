import pytest

from gqlalchemy.transformations.export.graph_transporter import GraphTransporter
from gqlalchemy.transformations.translators.dgl_translator import DGLTranslator
from gqlalchemy.transformations.translators.pyg_translator import PyGTranslator
from gqlalchemy.transformations.translators.nx_translator import NxTranslator


@pytest.mark.parametrize(
    "graph_type, translator_type", [("DGL", DGLTranslator), ("pyG", PyGTranslator), ("Nx", NxTranslator)]
)
def test_export_selection_strategy(graph_type, translator_type):
    transporter = GraphTransporter(graph_type)
    assert isinstance(transporter.translator, translator_type)
    transporter.export()  # even with empty graph we should check that something doesn't fail
