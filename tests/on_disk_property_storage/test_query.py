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

from gqlalchemy import SQLitePropertyDatabase


@pytest.fixture
def clear_db():
    db = SQLitePropertyDatabase()
    db.drop_database()


def test_create_db():
    db = SQLitePropertyDatabase()
    assert db is not None


def test_add_relationship_property(clear_db):
    db = SQLitePropertyDatabase()
    relationship_id = 2
    property_name = "friendship_type"
    property_value = "best_friends"
    db.save_relationship_property(relationship_id, property_name, property_value)
    result = db.load_relationship_property(relationship_id, property_name)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0][0] == property_value


def test_add_node_property(clear_db):
    db = SQLitePropertyDatabase()
    node_id = 1
    property_name = "person_name"
    property_value = "John"
    db.save_node_property(node_id, property_name, property_value)
    result = db.load_node_property(node_id, property_name)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0][0] == property_value
