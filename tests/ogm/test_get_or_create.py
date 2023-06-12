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

from gqlalchemy import Node, Field, Relationship, GQLAlchemyError, Match


def count_streamer_nodes() -> int:
    """Return a count of all streamer nodes"""
    return list(
        Match()
        .node("Streamer", variable="s")
        .return_({"count(s)": "frequency"})
        .execute()
    )[0]["frequency"]


def count_follows_relationships() -> int:
    """Return a count of all FOLLOWS relationships between Streamers."""
    return list(
        Match()
        .node("Streamer", variable="s")
        .to(edge_label="FOLLOWS", variable="r")
        .node("Streamer", variable="t")
        .return_({"count(r)": "frequency"})
        .execute()
    )[0]["frequency"]


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

    start_count = count_streamer_nodes()
    streamer, created = non_existent_streamer.get_or_create(database)
    assert created is True, "Node.get_or_create should create this node since it doesn't yet exist."
    assert streamer.name == "Mislav"
    assert streamer.id == "7"
    assert streamer.followers == 777
    assert streamer.totalViewCount == 7777
    assert streamer._labels == {"Streamer", "User"}

    after_create_count = count_streamer_nodes()
    assert after_create_count == start_count + 1, "Since the node was created, the count should be incremented by 1."

    streamer, created = non_existent_streamer.get_or_create(database)
    assert created is False, "Node.get_or_create should not create this node but load it instead."
    assert streamer.name == "Mislav"
    assert streamer.id == "7"
    assert streamer.followers == 777
    assert streamer.totalViewCount == 7777
    assert streamer._labels == {"Streamer", "User"}

    after_load_count = count_streamer_nodes()
    assert after_create_count == after_load_count, "A loaded node should not increase the count."


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_get_or_create_relationship(database):
    class User(Node):
        name: str = Field(unique=True, db=database)
        id: str = Field(index=True, db=database)

    class Follows(Relationship):
        _type = "FOLLOWS"

    node_from, created = User(id=1, name="foo").get_or_create(database)
    assert created is True
    assert node_from.id == "1"
    assert node_from.name == "foo"

    node_to, created = User(id=2, name="bar").get_or_create(database)
    assert created is True
    assert node_to.id == "2"
    assert node_to.name == "bar"

    start_count = count_follows_relationships()
    # Assert that loading a relationship that doesn't yet exist raises GQLAlchemyError.
    non_existent_relationship = Follows(_start_node_id=1, _end_node_id=2)
    with pytest.raises(GQLAlchemyError):
        database.load_relationship(non_existent_relationship)

    relationship, created = non_existent_relationship.get_or_create(database)
    assert created is True, "Relationship.get_or_create should create this relationship since it doesn't yet exist."
    assert relationship.id is not None
    created_id = relationship.id

    after_create_count = count_follows_relationships()
    assert (
        after_create_count == start_count + 1
    ), "Since the relationship was created, the count should be incremented by 1."

    relationship, created = non_existent_relationship.get_or_create(database)
    assert created is False, "Relationship.get_or_create should not create this relationship but load it instead."
    assert relationship.id == created_id

    after_load_count = count_follows_relationships()
    assert after_create_count == after_load_count, "A loaded relationship should not increase the count."
