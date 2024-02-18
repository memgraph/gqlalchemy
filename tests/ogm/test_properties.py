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

from gqlalchemy import Node


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_properties(database):
    class User(Node):
        id: int
        last_name: str
        _name: str
        _age: int

    user = User(id=1, last_name="Smith", _name="Jane").save(database)
    User(id=2, last_name="Scott").save(database)
    loaded_user = database.load_node(user)
    loaded_user._age = 24
    loaded_user2 = database.load_node(User(id=2, last_name="Scott"))

    assert type(loaded_user) is User
    assert type(loaded_user2) is User
    assert hasattr(loaded_user, "_name") is False
    assert hasattr(loaded_user, "_age") is True
    assert hasattr(loaded_user2, "_name") is False
    assert hasattr(loaded_user2, "_age") is False
    assert "id" in User.__fields__
    assert "last_name" in User.__fields__
    assert "_name" not in User.__fields__
    assert "_age" not in User.__fields__
    assert loaded_user.id == 1
    assert loaded_user.last_name == "Smith"
    assert loaded_user._label == "User"
    assert loaded_user2.id == 2
    assert loaded_user2.last_name == "Scott"
    assert loaded_user2._label == "User"
    assert user._name == "Jane"
    assert loaded_user._age == 24


def test_unicode_support(memgraph):
    class Test(Node):
        name: str
        last_name: str

    user1 = Test(name="\x13", last_name="\u0013").save(memgraph)
    user2 = Test(name="\u0013", last_name="\\x13").save(memgraph)
    user3 = Test(name="this is an example\u0013some text here", last_name="smith").save(memgraph)
    user4 = Test(name="jane", last_name="doe").save(memgraph)
    user5 = Test(name="jack", last_name="\u0013").save(memgraph)

    loaded_user1 = memgraph.load_node(user1)
    loaded_user2 = memgraph.load_node(user2)
    loaded_user3 = memgraph.load_node(user3)
    loaded_user4 = memgraph.load_node(user4)
    loaded_user5 = memgraph.load_node(user5)

    assert loaded_user1.name == "\u0013"
    assert loaded_user1.last_name == "\u0013"
    assert loaded_user2.name == "\u0013"
    assert loaded_user2.last_name == "\\x13"
    assert loaded_user3.name == "this is an example\u0013some text here"
    assert loaded_user4.name == "jane"
    assert loaded_user4.last_name == "doe"
    assert loaded_user5.name == "jack"
    assert loaded_user5.last_name == "\u0013"


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_list_property(database):
    class User(Node):
        my_list: list

    user = User(my_list=[1, 2, 3]).save(database)

    loaded_user = database.load_node(user)

    assert type(loaded_user) is User
    assert "my_list" in User.__fields__
    assert loaded_user.my_list == [1, 2, 3]


@pytest.mark.parametrize("database", ["memgraph"], indirect=True)
def test_dict_property(database):
    class User(Node):
        my_dict: dict

    expected_dict = dict(x=1, y=-2, z=3.1, d=20, testPoint=True, label="testPoint")
    user = User(my_dict=expected_dict).save(database)

    loaded_user = database.load_node(user)

    assert type(loaded_user) is User
    assert "my_dict" in User.__fields__
    assert loaded_user.my_dict == expected_dict
