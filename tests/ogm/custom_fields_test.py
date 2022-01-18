# Copyright (c) 2016-2022 Memgraph Ltd. [https://memgraph.com]
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

from gqlalchemy import (
    Memgraph,
    MemgraphConstraintExists,
    MemgraphConstraintUnique,
    MemgraphIndex,
    Node,
)
from pydantic import Field

db = Memgraph()


class Node1(Node):
    id: int = Field(exists=True, db=db)


class Node2(Node):
    id: int = Field(unique=True, db=db)


class Node3(Node):
    id: int = Field(index=True, db=db)


def test_create_constraint_exist(memgraph):
    memgraph_constraint = MemgraphConstraintExists("Node1", "id")

    memgraph.create_constraint(memgraph_constraint)
    actual_constraints = memgraph.get_constraints()

    assert actual_constraints == [memgraph_constraint]


def test_create_constraint_unique(memgraph):
    memgraph_constraint = MemgraphConstraintUnique("Node2", ("id",))

    memgraph.create_constraint(memgraph_constraint)
    actual_constraints = memgraph.get_constraints()

    assert actual_constraints == [memgraph_constraint]


def test_create_index(memgraph):
    memgraph_index = MemgraphIndex("Node2", "id")

    memgraph.create_index(memgraph_index)
    actual_constraints = memgraph.get_indexes()

    assert actual_constraints == [memgraph_index]
