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

import pytest

from gqlalchemy import Node, Field, Relationship, GQLAlchemyError


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_get_or_create_node(database):
    class User(Node):
        name: str = Field(unique=True, db=database)

    class Streamer(User):
        name: str = Field(unique=True, db=database)
        id: str = Field(index=True, db=database)
        followers: int = Field()
        totalViewCount: int = Field()

    # Assert that loading a node that doesn't yet exist raises GQLAlchemyError.
    non_existent_streamer = Streamer(name="Mislav", id="7", followers=777, totalViewCount=7777)
    with pytest.raises(GQLAlchemyError):
        database.load_node(non_existent_streamer)

    streamer, created = non_existent_streamer.get_or_create(database)
    assert created is True, "Node.get_or_create should create this node since it doesn't yet exist."
    assert streamer.name == "Mislav"
    assert streamer.id == "7"
    assert streamer.followers == 777
    assert streamer.totalViewCount == 7777
    assert streamer._labels == {"Streamer", "User"}

    streamer, created = non_existent_streamer.get_or_create(database)
    assert created is False, "Node.get_or_create should not create this node but load it instead."
    assert streamer.name == "Mislav"
    assert streamer.id == "7"
    assert streamer.followers == 777
    assert streamer.totalViewCount == 7777
    assert streamer._labels == {"Streamer", "User"}


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_get_or_create_relationship(database):
    class User(Node):
        name: str = Field(unique=True, db=database)
        id: str = Field(index=True, db=database)

    class Follows(Relationship):
        _type = "FOLLOWS"

    node_from, created = User(id=1).get_or_create(database)
    assert created is True
    assert node_from.id == 1

    node_to, created = User(id=2).get_or_create(database)
    assert created is True
    assert node_to.id == 1

    # Assert that loading a relationship that doesn't yet exist raises GQLAlchemyError.
    non_existent_relationship = Follows(_start_node_id=1, _end_node_id=2)
    with pytest.raises(GQLAlchemyError):
        database.load_relationship(non_existent_relationship)

    relationship, created = non_existent_relationship.get_or_create(database)
    assert created is True, "Relationship.get_or_create should create this relationship since it doesn't yet exist."
    assert relationship.id is not None
    created_id = relationship.id

    relationship, created = non_existent_relationship.get_or_create(database)
    assert created is False, "Relationship.get_or_create should not create this relationship but load it instead."
    assert relationship.id == created_id
