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

from gqlalchemy import Field, MemgraphConstraintExists, MemgraphConstraintUnique, Memgraph, Node

db = Memgraph()


def test_exists_attr(memgraph_without_dropping_constraints):
    class Person(Node):
        first_name: str = Field(index=True, db=db)
        year: int = Field(exists=True, db=db)
        person_age: int = Field(unique=True, db=db)
        hair: str = Field(exists=True, db=db)
        eyes: str = Field(unique=True, db=db)
        gender: str = Field(exists=True, unique=True, db=db)
        height: int = Field(unique=True, db=db)
        weight: int = Field(unique=True, exists=True, db=db)
        nationality: str = Field(exists=True, unique=True, db=db)
        state: str = Field(exists=False, unique=False, db=db)

    exists_constraints = {
        MemgraphConstraintExists("Person", "year"),
        MemgraphConstraintExists("Person", "gender"),
        MemgraphConstraintExists("Person", "hair"),
        MemgraphConstraintExists("Person", "gender"),
        MemgraphConstraintExists("Person", "weight"),
        MemgraphConstraintExists("Person", "nationality"),
    }
    actual_exists_constraints = memgraph_without_dropping_constraints.get_exists_constraints()
    assert set(actual_exists_constraints) == exists_constraints


def test_unique_attr(memgraph_without_dropping_constraints):
    class Person(Node):
        first_name: str = Field(index=True, db=db)
        year: int = Field(exists=True, db=db)
        person_age: int = Field(unique=True, db=db)
        hair: str = Field(exists=True, db=db)
        eyes: str = Field(unique=True, db=db)
        gender: str = Field(exists=True, unique=True, db=db)
        height: int = Field(unique=True, db=db)
        weight: int = Field(unique=True, exists=True, db=db)
        nationality: str = Field(exists=True, unique=True, db=db)
        state: str = Field(exists=False, unique=False, db=db)

    unique_constraints = {
        MemgraphConstraintUnique("Person", ("person_age",)),
        MemgraphConstraintUnique("Person", ("eyes",)),
        MemgraphConstraintUnique("Person", ("gender",)),
        MemgraphConstraintUnique("Person", ("height",)),
        MemgraphConstraintUnique("Person", ("weight",)),
        MemgraphConstraintUnique("Person", ("nationality",)),
    }
    actual_unique_constraints = memgraph_without_dropping_constraints.get_unique_constraints()
    assert set(actual_unique_constraints) == unique_constraints


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
        MemgraphConstraintExists("NodeTwo", "text_"),
        MemgraphConstraintUnique(
            "NodeThree",
            (
                "attribute1",
                "attribute2",
            ),
        ),
        MemgraphConstraintUnique("NodeThree", ("attribute3",)),
    ]
    memgraph.ensure_constraints(new_constraints)
    actual_constraints_ensured = memgraph.get_constraints()

    assert set(actual_constraints_ensured) == set(new_constraints)
