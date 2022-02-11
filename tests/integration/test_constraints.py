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

from gqlalchemy import MemgraphConstraintExists, MemgraphConstraintUnique


def test_create_constraint_exist(memgraph):
    memgraph_constraint = MemgraphConstraintExists("TestLabel", "name")

    memgraph.create_constraint(memgraph_constraint)
    actual_constraints = memgraph.get_constraints()

    assert actual_constraints == [memgraph_constraint]


def test_create_constraint_unique(memgraph):
    memgraph_constraint = MemgraphConstraintUnique("TestLabel", ("name",))

    memgraph.create_constraint(memgraph_constraint)
    actual_constraints = memgraph.get_constraints()

    assert actual_constraints == [memgraph_constraint]


def test_drop_constraint_exist(memgraph):
    memgraph_constraint = MemgraphConstraintExists("TestLabel", "name")

    memgraph.create_constraint(memgraph_constraint)
    memgraph.drop_constraint(memgraph_constraint)
    actual_constraints = memgraph.get_constraints()

    assert actual_constraints == []


def test_drop_constraint_unique(memgraph):
    memgraph_constraint = MemgraphConstraintUnique("TestLabel", ("name",))

    memgraph.create_constraint(memgraph_constraint)
    memgraph.drop_constraint(memgraph_constraint)
    actual_constraints = memgraph.get_constraints()

    assert actual_constraints == []


def test_create_duplicate_constraint(memgraph):
    memgraph_constraint_exist = MemgraphConstraintExists("TestLabel", "name")

    memgraph.create_constraint(memgraph_constraint_exist)
    memgraph.create_constraint(memgraph_constraint_exist)
    actual_constraints = memgraph.get_constraints()

    assert set(actual_constraints) == {memgraph_constraint_exist}


def test_ensure_constraints_remove_all(memgraph):
    old_constraints = [
        MemgraphConstraintExists("NodeOne", "name"),
        MemgraphConstraintExists("NodeTwo", "age"),
        MemgraphConstraintUnique(
            "NodeThree",
            (
                "name",
                "age",
            ),
        ),
        MemgraphConstraintUnique("NodeThree", ("code",)),
    ]
    for old_constraint in old_constraints:
        memgraph.create_constraint(old_constraint)
    actual_constraints = memgraph.get_constraints()

    assert set(actual_constraints) == set(old_constraints)

    new_constraints = []
    memgraph.ensure_constraints(new_constraints)
    actual_constraints_ensured = memgraph.get_constraints()

    assert set(actual_constraints_ensured) == set(new_constraints)


def test_ensure_constraints(memgraph):
    old_constraints = [
        MemgraphConstraintExists("NodeOne", "name"),
        MemgraphConstraintExists("NodeTwo", "age"),
        MemgraphConstraintUnique(
            "NodeThree",
            (
                "name",
                "age",
            ),
        ),
        MemgraphConstraintUnique("NodeThree", ("code",)),
    ]
    for old_constraint in old_constraints:
        memgraph.create_constraint(old_constraint)
    actual_constraints = memgraph.get_constraints()

    assert set(actual_constraints) == set(old_constraints)

    new_constraints = [
        MemgraphConstraintExists("NodeOne", "code"),
        MemgraphConstraintExists("NodeTwo", "text"),
        MemgraphConstraintUnique(
            "NodeThree",
            (
                "attribtue1",
                "attribtue2",
            ),
        ),
        MemgraphConstraintUnique("NodeThree", ("attribtue3",)),
    ]
    memgraph.ensure_constraints(new_constraints)
    actual_constraints_ensured = memgraph.get_constraints()

    assert set(actual_constraints_ensured) == set(new_constraints)
