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

from typing import Optional
from gqlalchemy import Memgraph, Node, Relationship, Field
import pytest

db = Memgraph()


class SimpleNode(Node):
    id: Optional[int] = Field()
    name: Optional[str] = Field()


class NodeWithKey(Node):
    id: int = Field(exists=True, unique=True, index=True, db=db)
    name: Optional[str] = Field()


class SimpleRelationship(Relationship, type="SIMPLE_RELATIONSHIP"):
    pass


@pytest.fixture
def clear_db():
    db = Memgraph()
    db.drop_database()


def test_save_node(clear_db):
    node1 = SimpleNode(id=1, name="First Simple Node")
    assert node1._id is None
    node1.save(db)
    assert node1._id is not None
    node2 = SimpleNode(id=1)
    node2.save(db)
    assert node1._id != node2._id


def test_save_node2(memgraph, clear_db):
    node1 = NodeWithKey(id=1, name="First NodeWithKey")
    assert node1._id is None
    node1.save(db)
    assert node1._id is not None
    node2 = NodeWithKey(id=1)
    node2.save(db)
    assert node1._id == node2._id
    assert node1.name == node2.name


def test_save_relationship(memgraph, clear_db):
    node1 = NodeWithKey(id=1, name="First NodeWithKey").save(memgraph)
    node2 = NodeWithKey(id=2, name="Second NodeWithKey").save(memgraph)
    relationship = SimpleRelationship(
        _start_node_id=node1._id,
        _end_node_id=node2._id,
    )
    assert SimpleRelationship.type == relationship._type
    assert SimpleRelationship._type is not None
    relationship.save(memgraph)
    assert relationship._id is not None


def test_save_relationship2(memgraph, clear_db):
    node1 = NodeWithKey(id=1, name="First NodeWithKey").save(memgraph)
    node2 = NodeWithKey(id=2, name="Second NodeWithKey").save(memgraph)
    relationship = SimpleRelationship(
        _start_node_id=node1._id,
        _end_node_id=node2._id,
    )
    assert SimpleRelationship.type == relationship._type
    assert SimpleRelationship.type is not None
    relationship.save(memgraph)
    assert relationship._id is not None
    relationship2 = db.load_relationship(relationship)
    assert relationship2._id == relationship._id
