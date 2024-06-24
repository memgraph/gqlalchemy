def test_get_storage_mode(memgraph):
    assert memgraph.get_storage_mode() == "IN_MEMORY_TRANSACTIONAL"


def test_set_storage_mode(memgraph):
    memgraph.set_storage_mode("IN_MEMORY_ANALYTICAL")
    assert memgraph.get_storage_mode() == "IN_MEMORY_ANALYTICAL"
