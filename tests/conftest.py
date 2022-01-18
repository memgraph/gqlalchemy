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

from pathlib import Path

import pytest
from gqlalchemy import Memgraph


def get_data_dir() -> Path:
    return Path(__file__).parents[0].joinpath("data")


@pytest.fixture
def memgraph() -> Memgraph:
    memgraph = Memgraph()
    memgraph.ensure_indexes([])
    memgraph.ensure_constraints([])
    memgraph.drop_database()
    return memgraph


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
