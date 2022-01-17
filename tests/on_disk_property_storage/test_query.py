# Copyright (c) 2016-2021 Memgraph Ltd. [https://memgraph.com]
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

from gqlalchemy import SQLitePropertyDatabase, Memgraph, Node, Field
from typing import Optional


db = SQLitePropertyDatabase("./tests/on_disk_storage.db")


@pytest.fixture
def clear_db():
    db.drop_database()


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


memgraph = Memgraph()


class User(Node):
    id: int = Field(index=True, db=memgraph)
    huge_string: Optional[str] = Field(on_disk=True, on_disk_db=db)


# class Streamer(User):
#     pass


def test_add_node_with_on_disk_property(clear_db):
    user = User(id=12, huge_string="qwertyuiopasdfghjklzxcvbnm")
    memgraph.save_node(user)
