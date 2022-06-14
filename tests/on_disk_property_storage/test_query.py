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
from typing import Optional

from gqlalchemy import Field, Memgraph, Node, Relationship, SQLitePropertyDatabase


memgraph = Memgraph()
db = SQLitePropertyDatabase("./tests/on_disk_storage.db", memgraph)


def drop_data_and_constraints():
    memgraph.drop_database()
    db.drop_database()
    memgraph.ensure_indexes([])
    memgraph.ensure_constraints([])


@pytest.fixture(scope="module")
def clear_db():
    drop_data_and_constraints()
    yield
    drop_data_and_constraints()


def test_add_relationship_property(clear_db):
    relationship_id = 2
    property_name = "friendship_type"
    property_value = "best_friends"
    db.save_relationship_property(relationship_id, property_name, property_value)
    result_value = db.load_relationship_property(relationship_id, property_name)
    assert result_value == property_value


def test_add_node_property(clear_db):
    node_id = 1
    property_name = "person_name"
    property_value = "John"
    db.save_node_property(node_id, property_name, property_value)
    result_value = db.load_node_property(node_id, property_name)
    assert result_value == property_value


def test_delete_node_property(clear_db):
    node_id = 1
    property_name = "person_name"
    property_value = "John"
    db.save_node_property(node_id, property_name, property_value)
    db.delete_node_property(node_id, property_name)
    result_value = db.load_node_property(node_id, property_name)
    assert result_value is None


def test_delete_relationship_property(clear_db):
    relationship_id = 2
    property_name = "friendship_type"
    property_value = "best_friends"
    db.save_relationship_property(relationship_id, property_name, property_value)
    db.delete_relationship_property(relationship_id, property_name)
    result_value = db.load_relationship_property(relationship_id, property_name)
    assert result_value is None


def test_add_node_with_an_on_disk_property():
    class User(Node):
        id: int = Field(unique=True, index=True, db=memgraph)
        huge_string: Optional[str] = Field(on_disk=True)

    secret = "qwertyuiopasdfghjklzxcvbnm"
    user = User(id=12, huge_string=secret)
    memgraph.save_node(user)
    user_2 = User(id=12).load(memgraph)
    assert user_2.huge_string == secret


def test_add_relationship_with_an_on_disk_property():
    class User(Node):
        id: int = Field(unique=True, index=True, db=memgraph)
        huge_string: Optional[str] = Field(on_disk=True)

    class FriendTo(Relationship, type="FRIEND_TO"):
        huge_string: Optional[str] = Field(on_disk=True)

    secret = "qwertyuiopasdfghjklzxcvbnm"
    user_1 = User(id=12).save(memgraph)
    user_2 = User(id=11).save(memgraph)
    friend = FriendTo(
        _start_node_id=user_1._id,
        _end_node_id=user_2._id,
        huge_string=secret,
    ).save(memgraph)
    friend_2 = FriendTo(
        _start_node_id=user_1._id,
        _end_node_id=user_2._id,
    ).load(memgraph)
    assert friend.huge_string == secret
    assert friend.huge_string == friend_2.huge_string
