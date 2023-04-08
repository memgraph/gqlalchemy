import pytest

from gqlalchemy import Memgraph


@pytest.fixture
def memgraph() -> Memgraph:
    memgraph = Memgraph()
    memgraph.drop_database()
    yield memgraph
    memgraph.drop_database()


def execute_queries(memgraph, queries):
    for query in queries:
        memgraph.execute(query)
