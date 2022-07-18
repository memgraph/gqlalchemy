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

from gqlalchemy import Node


def test_properties(memgraph):
    class User(Node):
        id: int
        last_name: str
        _name: str
        _age: int

    user = User(id=1, last_name="Smith", _name="Jane").save(memgraph)
    User(id=2, last_name="Scott").save(memgraph)
    loaded_user = memgraph.load_node(user)
    loaded_user._age = 24
    loaded_user2 = memgraph.load_node(User(id=2, last_name="Scott"))

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
