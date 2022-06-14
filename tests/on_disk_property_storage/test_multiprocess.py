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

import multiprocessing as mp
import pytest
import random
import traceback
from typing import Optional

import mgclient

from gqlalchemy import Field, GQLAlchemyError, Memgraph, Node, SQLitePropertyDatabase


db = Memgraph()
SQLitePropertyDatabase("./tests/on_disk_storage.db", db)


@pytest.fixture
def clear_db():
    db = Memgraph()
    db.drop_database()
    on_disk_db = SQLitePropertyDatabase("./tests/on_disk_storage.db")
    on_disk_db.drop_database()


@pytest.mark.slow
def test_run_1000_queries(clear_db):
    _run_n_queries(1000)


@pytest.mark.slow
def test_run_10000_queries(clear_db):
    _run_n_queries(10000)


@pytest.mark.slow
def test_run_100000_queries(clear_db):
    _run_n_queries(100000)


def _run_n_queries(n: int):
    number_of_processes = mp.cpu_count() // 2 + 1
    chunk_size = n // number_of_processes
    with mp.Pool(processes=number_of_processes) as pool:
        pool.map(_create_n_user_objects, [chunk_size] * number_of_processes)


def _create_n_user_objects(n: int) -> None:
    class User(Node):
        id: Optional[str] = Field(unique=True, index=True, db=db)
        huge_string: Optional[str] = Field(on_disk=True)

    db = Memgraph()
    SQLitePropertyDatabase("./tests/on_disk_storage.db", db)
    huge_string = "I LOVE MEMGRAPH" * 1000
    for _ in range(n):
        id_ = random.randint(1, 2 * n)
        try:
            user1 = User(id=id_, huge_string=huge_string).save(db)
            assert user1.huge_string == huge_string
        except mgclient.DatabaseError:  # Memgraph collision happened
            continue
        except GQLAlchemyError as e:
            print("Error when saving a node.")
            print(traceback.format_exc())
            print(list(db.execute_and_fetch("match (a) return a;")))
            print(list(db.execute_and_fetch("show constraint info;")))
            raise e
        try:
            user2 = User(id=id_).load(db)
            assert user2.huge_string == huge_string
        except mgclient.DatabaseError:  # Memgraph collision happened
            continue
        except GQLAlchemyError as e:
            print("Error in loading a node.")
            print(traceback.format_exc())
            print(list(db.execute_and_fetch("match (a) return a;")))
            print(list(db.execute_and_fetch("show constraint info;")))
            raise e
