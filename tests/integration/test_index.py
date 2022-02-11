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

from gqlalchemy.models import MemgraphIndex


def test_no_index(memgraph):
    assert memgraph.get_indexes() == []


def test_create_index(memgraph):
    index1 = MemgraphIndex("NodeOne")
    index2 = MemgraphIndex("NodeOne", "name")

    memgraph.create_index(index1)
    memgraph.create_index(index2)

    assert set(memgraph.get_indexes()) == {index1, index2}


def test_create_duplicate_index(memgraph):
    index = MemgraphIndex("NodeOne")

    memgraph.create_index(index)
    memgraph.create_index(index)

    assert set(memgraph.get_indexes()) == {index}


def test_drop_index(memgraph):
    index1 = MemgraphIndex("NodeOne")
    index2 = MemgraphIndex("NodeOne", "name")

    memgraph.create_index(index1)
    memgraph.create_index(index2)

    memgraph.drop_index(index1)
    assert set(memgraph.get_indexes()) == {index2}

    memgraph.drop_index(index2)
    assert set(memgraph.get_indexes()) == set()


def test_drop_duplicate_index(memgraph):
    index = MemgraphIndex("NodeOne")

    memgraph.create_index(index)
    memgraph.drop_index(index)
    assert set(memgraph.get_indexes()) == set()

    memgraph.drop_index(index)
    assert set(memgraph.get_indexes()) == set()


def test_ensure_index(memgraph):
    old_indexes = [
        MemgraphIndex("NodeOne"),
        MemgraphIndex("NodeOne", "name"),
        MemgraphIndex("NodeTwo"),
        MemgraphIndex("NodeTwo", "age"),
    ]
    for old_index in old_indexes:
        memgraph.create_index(old_index)

    assert set(memgraph.get_indexes()) == set(old_indexes)

    new_indexes = [
        MemgraphIndex("NodeOne", "name"),
        MemgraphIndex("NodeTwo"),
        MemgraphIndex("NodeThree"),
        MemgraphIndex("NodeFour", "created_at"),
    ]
    memgraph.ensure_indexes(new_indexes)

    assert set(memgraph.get_indexes()) == set(new_indexes)
