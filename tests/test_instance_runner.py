from gqlalchemy import MemgraphInstanceBinary, MemgraphInstanceDocker


def test_start_memgraph_docker():
    memgraph_instance = MemgraphInstanceDocker(port=7688)
    memgraph = memgraph_instance.start()
    assert list(memgraph.execute_and_fetch("RETURN 100 AS result"))[0]["result"] == 100
    memgraph_instance.stop()


def test_start_memgraph_binary():
    memgraph_instance = MemgraphInstanceBinary(
        port=7689, config={"--data-directory": "data"}, binary_path="/usr/lib/memgraph/memgraph", user="memgraph"
    )
    memgraph = memgraph_instance.start()
    assert list(memgraph.execute_and_fetch("RETURN 100 AS result"))[0]["result"] == 100
    memgraph_instance.stop()
