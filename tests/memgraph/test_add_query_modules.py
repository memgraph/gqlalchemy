import pytest

from gqlalchemy import Memgraph
from gqlalchemy.exceptions import GQLAlchemyFileNotFoundError


@pytest.mark.parametrize(
    "file_path, module_name, module_remove_name",
    [
        ("gqlalchemy/query_modules/push_streams/kafka.py", "kafka.py", "kafka.py"),
    ],
)
def test_add_query_module_valid(file_path, module_name, remove_module_memgraph):
    memgraph = remove_module_memgraph.add_query_module(file_path=file_path, module_name=module_name)

    module_paths = list(memgraph.execute_and_fetch("CALL mg.get_module_files() YIELD path"))

    assert any("kafka" in path["path"] for path in module_paths)


@pytest.mark.parametrize(
    "file_path, module_name",
    [
        ("path_doesnt_exists", "fake"),
    ],
)
def test_add_query_module_invalid(file_path, module_name):
    with pytest.raises(GQLAlchemyFileNotFoundError):
        Memgraph().add_query_module(file_path=file_path, module_name=module_name)
