# Copyright (c) 2016-2022 Memgraph Ltd. [https://memgraph.com]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from pathlib import Path
from typing import Tuple

from gqlalchemy import Memgraph, models, Neo4j, QueryBuilder, Neo4jQueryBuilder
from gqlalchemy.instance_runner import MemgraphInstanceDocker


def get_data_dir() -> Path:
    return Path(__file__).parents[0].joinpath("data")


@pytest.fixture
def database(request):
    return request.getfixturevalue(request.param)


@pytest.fixture
def vendor(request):
    return request.getfixturevalue(request.param)


@pytest.fixture
def memgraph() -> Memgraph:
    memgraph = Memgraph()
    memgraph.ensure_indexes([])
    memgraph.ensure_constraints([])
    memgraph.drop_database()
    memgraph.set_storage_mode("IN_MEMORY_TRANSACTIONAL")

    yield memgraph

    memgraph.ensure_indexes([])
    memgraph.ensure_constraints([])
    memgraph.set_storage_mode("IN_MEMORY_TRANSACTIONAL")


@pytest.fixture
def neo4j() -> Neo4j:
    neo4j = Neo4j(port="7688")
    neo4j.ensure_constraints([])
    neo4j.ensure_indexes([])
    neo4j.drop_database()

    yield neo4j

    neo4j.ensure_constraints([])
    neo4j.ensure_indexes([])


@pytest.fixture
def memgraph_query_builder() -> Tuple[Memgraph, QueryBuilder]:
    memgraph = Memgraph()
    memgraph.ensure_indexes([])
    memgraph.ensure_constraints([])
    memgraph.drop_database()

    yield (memgraph, QueryBuilder(memgraph))

    memgraph.ensure_indexes([])
    memgraph.ensure_constraints([])


@pytest.fixture
def neo4j_query_builder() -> Tuple[Neo4j, Neo4jQueryBuilder]:
    neo4j = Neo4j(port="7688")
    neo4j.ensure_indexes([])
    neo4j.ensure_constraints([])
    neo4j.drop_database()

    yield (neo4j, Neo4jQueryBuilder(neo4j))

    neo4j.ensure_indexes([])
    neo4j.ensure_constraints([])


@pytest.fixture
def memgraph_without_dropping_constraints() -> Memgraph:
    memgraph = Memgraph()
    memgraph.drop_database()

    yield memgraph

    memgraph.drop_database()


@pytest.fixture
def populated_memgraph(dataset_file: str) -> Memgraph:
    memgraph = Memgraph()
    memgraph.ensure_indexes([])
    memgraph.ensure_constraints([])
    memgraph.drop_database()
    with get_data_dir().joinpath(dataset_file).open("r") as dataset:
        for query in dataset:
            memgraph.execute(query)

    yield memgraph

    memgraph.drop_database()


@pytest.fixture
def remove_module_memgraph(module_remove_name: str) -> Memgraph:
    memgraph = Memgraph()
    memgraph.ensure_indexes([])
    memgraph.ensure_constraints([])
    memgraph.drop_database()

    yield memgraph

    module_paths = list(memgraph.execute_and_fetch("CALL mg.get_module_files() YIELD path"))
    module_path = [path["path"] for path in module_paths if module_remove_name in path["path"]][0]
    list(memgraph.execute_and_fetch(f"CALL mg.delete_module_file('{module_path}') YIELD *"))
    memgraph.drop_database()


@pytest.fixture(scope="session", autouse=True)
def init():
    models.IGNORE_SUBCLASSNOTFOUNDWARNING = True


@pytest.fixture
def configuration():
    return {"--log-level": "TRACE"}


@pytest.mark.extras
@pytest.mark.docker
@pytest.fixture
def memgraph_instance_docker():
    def _memgraph_instance_docker(config):
        return MemgraphInstanceDocker(port=7690, config=config)

    return _memgraph_instance_docker


@pytest.mark.extras
@pytest.mark.docker
@pytest.fixture
def memgraph_instance_docker_with_config(memgraph_instance_docker, configuration):
    instance = memgraph_instance_docker(config=configuration)
    yield instance

    instance.stop()


@pytest.mark.extras
@pytest.mark.docker
@pytest.fixture
def memgraph_instance_docker_without_config(memgraph_instance_docker):
    instance = memgraph_instance_docker(config={})
    yield instance

    instance.stop()
