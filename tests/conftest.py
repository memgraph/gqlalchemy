import pytest
from project_name.database import Memgraph


@pytest.fixture
def db():
    db = Memgraph()
    db.ensure_indexes([])
    db.ensure_constraints([])
    return db
