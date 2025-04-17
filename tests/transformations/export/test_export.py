import pytest

from gqlalchemy.transformations.export.graph_transporter import GraphTransporter


@pytest.mark.extras
@pytest.mark.dgl
def test_export_dgl():
    DGLTranslator = pytest.importorskip("gqlalchemy.transformations.translators.dgl_translator.DGLTranslator")

    transporter = GraphTransporter(graph_type="DGL")
    assert isinstance(transporter.translator, DGLTranslator)
    transporter.export()  # even with empty graph we should check that something doesn't fail


@pytest.mark.extras
@pytest.mark.pyg
def test_export_pyg():
    PyGTranslator = pytest.importorskip("gqlalchemy.transformations.translators.pyg_translator.PyGTranslator")

    transporter = GraphTransporter(graph_type="pyG")
    assert isinstance(transporter.translator, PyGTranslator)
    transporter.export()  # even with empty graph we should check that something doesn't fail


def test_export_nx():
    from gqlalchemy.transformations.translators.nx_translator import NxTranslator

    transporter = GraphTransporter(graph_type="Nx")
    assert isinstance(transporter.translator, NxTranslator)
    transporter.export()  # even with empty graph we should check that something doesn't fail
