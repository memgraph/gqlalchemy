import pytest
from gqlalchemy import Memgraph
from gqlalchemy.exceptions import GQLAlchemyFileNotFoundError


@pytest.mark.parametrize(
    "file_path, module_name",
    [
        ("gqlalchemy/query_modules/push_streams/kafka.py", 'kafka'),
    ],
)
def test_add_query_module_valid(file_path, module_name):
    memgraph_db = Memgraph()

    procedures_before = list(memgraph_db.execute_and_fetch("CALL mg.procedures() YIELD name"))

    memgraph_db = memgraph_db._add_query_module(file_path=file_path, module_name=module_name)

    procedures_after = list(memgraph_db.execute_and_fetch("CALL mg.procedures() YIELD name"))

    assert len(procedures_after) == len(procedures_before) + 3


@pytest.mark.parametrize(
    "file_path, module_name",
    [
        ("path_doesnt_exists", "fake"),
    ],
)
def test_add_query_module_invalid(file_path, module_name):
    with pytest.raises(GQLAlchemyFileNotFoundError):
        Memgraph()._add_query_module(file_path=file_path, module_name=module_name)
