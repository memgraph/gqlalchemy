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
from pydantic import ValidationError


def test_partial_loading(memgraph):
    class User(Node):
        id: int
        name: str = None

    User(id=1, name="Jane").save(memgraph)

    with pytest.raises(ValidationError):
        memgraph.load_node(User(name="Jane"))

    user_by_id = memgraph.load_node(User(id=1))

    assert user_by_id.id == 1
    assert user_by_id.name == "Jane"
    assert user_by_id._label == "User"


def test_node_loading(memgraph):
    class User(Node):
        id: int
        name: str

    User(id=1, name="Jane").save(memgraph)
    user_by_name = memgraph.load_node(User(id=1, name="Jane"))

    assert user_by_name.id == 1
    assert user_by_name.name == "Jane"
    assert user_by_name._label == "User"
