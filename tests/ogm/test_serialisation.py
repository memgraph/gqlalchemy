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

from datetime import datetime
from typing import Optional

from gqlalchemy import Field, Node, Relationship


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_save_node(database):
    class SimpleNode(Node):
        id: Optional[int] = Field()
        name: Optional[str] = Field()

    node1 = SimpleNode(id=1, name="First Simple Node")
    assert node1._id is None
    node1.save(database)
    assert node1._id is not None
    node2 = SimpleNode(id=1)
    node2.save(database)
    assert node1._id != node2._id


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_save_node2(database):
    class NodeWithKey(Node):
        id: int = Field(unique=True, db=database)
        name: Optional[str] = Field()

    node1 = NodeWithKey(id=1, name="First NodeWithKey")
    assert node1._id is None
    node1.save(database)
    assert node1._id is not None
    node2 = NodeWithKey(id=1)
    node2.save(database)
    assert node1._id == node2._id
    assert node1.name == node2.name


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_save_nodes(database):
    class SimpleNode(Node):
        id: Optional[int] = Field()
        name: Optional[str] = Field()

    node1 = SimpleNode(id=1, name="First Simple Node")
    node2 = SimpleNode(id=2, name="Second Simple Node")
    node3 = SimpleNode(id=3, name="Third Simple Node")

    assert node1._id is None
    assert node2._id is None
    assert node3._id is None

    database.save_nodes([node1, node2, node3])

    assert node1._id is not None
    assert node2._id is not None
    assert node3._id is not None

    node1.name = "1st Simple Node"
    node2.name = "2nd Simple Node"
    node3.name = "3rd Simple Node"

    database.save_nodes([node1, node2, node3])

    assert node1.name == "1st Simple Node"
    assert node2.name == "2nd Simple Node"
    assert node3.name == "3rd Simple Node"


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_save_relationship(database):
    class NodeWithKey(Node):
        id: int = Field(unique=True, db=database)
        name: Optional[str] = Field()

    class SimpleRelationship(Relationship, type="SIMPLE_RELATIONSHIP"):
        pass

    node1 = NodeWithKey(id=1, name="First NodeWithKey").save(database)
    node2 = NodeWithKey(id=2, name="Second NodeWithKey").save(database)
    relationship = SimpleRelationship(
        _start_node_id=node1._id,
        _end_node_id=node2._id,
    )
    assert SimpleRelationship.type == relationship._type
    assert SimpleRelationship._type is not None
    relationship.save(database)
    assert relationship._id is not None


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_save_relationship2(database):
    class NodeWithKey(Node):
        id: int = Field(unique=True, db=database)
        name: Optional[str] = Field()

    class SimpleRelationship(Relationship, type="SIMPLE_RELATIONSHIP"):
        pass

    node1 = NodeWithKey(id=1, name="First NodeWithKey").save(database)
    node2 = NodeWithKey(id=2, name="Second NodeWithKey").save(database)
    relationship = SimpleRelationship(
        _start_node_id=node1._id,
        _end_node_id=node2._id,
    )
    assert SimpleRelationship.type == relationship._type
    assert SimpleRelationship.type is not None
    relationship.save(database)
    assert relationship._id is not None
    relationship2 = database.load_relationship(relationship)
    assert relationship2._id == relationship._id


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_save_relationships(database):
    class User(Node):
        id: int = Field(unique=True, db=database)
        name: Optional[str] = Field()

    class Follows(Relationship, type="FOLLOWS"):
        pass

    node1 = User(id=1, name="Marin")
    node2 = User(id=2, name="Marko")

    database.save_nodes([node1, node2])
    assert node1._id is not None
    assert node2._id is not None

    relationship1 = Follows(
        _start_node_id=node1._id,
        _end_node_id=node2._id,
    )
    relationship2 = Follows(
        _start_node_id=node2._id,
        _end_node_id=node1._id,
    )

    assert Follows.type == relationship1._type
    assert Follows._type is not None

    database.save_relationships([relationship1, relationship2])
    assert relationship1._id is not None
    assert relationship2._id is not None


def test_save_node_with_datetime_property(memgraph):
    class User(Node):
        id: str = Field(index=True, db=memgraph)
        name: str = Field()
        timestamp: datetime = Field()

    user = User(id="1", name="myUser", timestamp=datetime.now()).save(memgraph)
    assert user._id is not None
