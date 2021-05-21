import pytest

from memgraph import Memgraph


@pytest.fixture
def db():
    db = Memgraph()
    db.ensure_indexes([])
    db.ensure_constraints([])
    return db
