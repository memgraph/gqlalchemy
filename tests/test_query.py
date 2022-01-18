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

from typing import Any, Dict, Iterator

import pytest

from gqlalchemy import Memgraph, Node


def query(command: str) -> Iterator[Dict[str, Any]]:
    """Queries Memgraph database and returns iterator of results"""
    db = Memgraph()
    yield from db.execute_and_fetch(command)


@pytest.fixture
def clear_db():
    db = Memgraph()
    db.drop_database()


@pytest.mark.parametrize(
    "command, results",
    [("MATCH (n) RETURN n", []), ("MATCH ()-[e]-() RETURN e", []), ("MATCH (n) RETURN count(n) as cnt", [{"cnt": 0}])],
)
def test_query_on_empty_database(command, results, clear_db):
    actual_results = list(query(command))
    assert actual_results == results


def test_query_create_count(clear_db):
    create_command = """
    CREATE
        (n: Hello {message: "Hello"}),
        (m: World {message: "World"})
    RETURN n, m;
    """
    actual_results = list(query(create_command))
    assert len(actual_results) == 1
    assert set(actual_results[0].keys()) == {"n", "m"}
    for result in actual_results[0].values():
        assert isinstance(result, Node)

    count_command = "MATCH (n) RETURN count(n) as cnt"
    assert list(query(count_command)) == [{"cnt": 2}]
