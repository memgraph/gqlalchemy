# Copyright (c) 2016-2021 Memgraph Ltd. [https://memgraph.com]
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

from typing import Optional
from gqlalchemy import (
    Memgraph,
    Node,
)
from pydantic import Field
import pytest

db = Memgraph()


class Node(Node):
    # id: int = Field(exists=True, unique=True, index=True, db=db)
    id: Optional[int] = Field()
    name: Optional[str] = Field()


@pytest.fixture
def clear_db():
    db = Memgraph()
    db.drop_database()


def test_save_node(memgraph, clear_db):
    node1 = Node(id=1, name="First Node")
    assert node1._id is None
    node1.save_node(db)
    assert node1._id is not None
    node2 = Node(id=1)
    node2.load_node(db)
    assert node1._id == node2._id
    assert node1.name == node2.name
