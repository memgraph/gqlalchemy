import pytest
from gqlalchemy.exceptions import GQLAlchemyDatabaseError
from gqlalchemy import create


def test_switch_to_on_disk(memgraph):
    create().node(labels="Person", name="Leslie").execute()

    with pytest.raises(GQLAlchemyDatabaseError):
        memgraph.set_storage_mode("ON_DISK_TRANSACTIONAL")
