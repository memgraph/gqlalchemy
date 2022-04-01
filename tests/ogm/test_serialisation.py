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
from gqlalchemy import Node, Relationship, Field


def test_save_node(memgraph):
    class SimpleNode(Node):
        id: Optional[int] = Field()
        name: Optional[str] = Field()

    node1 = SimpleNode(id=1, name="First Simple Node")
    assert node1._id is None
    node1.save(memgraph)
    assert node1._id is not None
    node2 = SimpleNode(id=1)
    node2.save(memgraph)
    assert node1._id != node2._id


def test_save_node2(memgraph):
    class NodeWithKey(Node):
        id: int = Field(exists=True, unique=True, index=True, db=memgraph)
        name: Optional[str] = Field()

    node1 = NodeWithKey(id=1, name="First NodeWithKey")
    assert node1._id is None
    node1.save(memgraph)
    assert node1._id is not None
    node2 = NodeWithKey(id=1)
    node2.save(memgraph)
    assert node1._id == node2._id
    assert node1.name == node2.name


def test_save_nodes(memgraph):
    class SimpleNode(Node):
        id: Optional[int] = Field()
        name: Optional[str] = Field()

    node1 = SimpleNode(id=1, name="First Simple Node")
    node2 = SimpleNode(id=2, name="Second Simple Node")
    node3 = SimpleNode(id=3, name="Third Simple Node")

    assert node1._id is None
    assert node2._id is None
    assert node3._id is None

    memgraph.save_nodes([node1, node2, node3])

    assert node1._id is not None
    assert node2._id is not None
    assert node3._id is not None

    node1.name = "1st Simple Node"
    node2.name = "2nd Simple Node"
    node3.name = "3rd Simple Node"

    memgraph.save_nodes([node1, node2, node3])

    assert node1.name == "1st Simple Node"
    assert node2.name == "2nd Simple Node"
    assert node3.name == "3rd Simple Node"


def test_save_relationship(memgraph):
    class NodeWithKey(Node):
        id: int = Field(exists=True, unique=True, index=True, db=memgraph)
        name: Optional[str] = Field()

    class SimpleRelationship(Relationship, type="SIMPLE_RELATIONSHIP"):
        pass

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


def test_save_relationship2(memgraph):
    class NodeWithKey(Node):
        id: int = Field(exists=True, unique=True, index=True, db=memgraph)
        name: Optional[str] = Field()

    class SimpleRelationship(Relationship, type="SIMPLE_RELATIONSHIP"):
        pass

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
    relationship2 = memgraph.load_relationship(relationship)
    assert relationship2._id == relationship._id


def test_save_relationships(memgraph):
    class User(Node):
        id: int = Field(exists=True, unique=True, index=True, db=memgraph)
        name: Optional[str] = Field()

    class Follows(Relationship, type="FOLLOWS"):
        pass

    node1 = User(id=1, name="Marin")
    node2 = User(id=2, name="Marko")

    memgraph.save_nodes([node1, node2])
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

    memgraph.save_relationships([relationship1, relationship2])
    assert relationship1._id is not None
    assert relationship2._id is not None
