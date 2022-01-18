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

from typing import Optional
from gqlalchemy import Memgraph, Node, Relationship, Path
from gqlalchemy.models import GraphObject


class Person(Node):
    id: Optional[int]
    name: Optional[str]


class Alice(Node):
    id: Optional[int]
    name: Optional[str]


class Friends(Relationship, _type="FRIENDS"):
    pass


def test_simple_json_deserialisation():
    person_json = '{"_type":"Person", "id": 9, "name": "person"}'
    person = GraphObject.parse_raw(person_json)
    assert person == Person(id=9, name="person")


def test_json_deserialisation():
    person_json = '{"_type":"Person", "id": 9, "name": "person", "_node_labels": ["Person"], "_id": 1, "_node_id": 1}'
    person_1 = GraphObject.parse_raw(person_json)
    person_2 = Person(id=9, name="person")
    person_2._id = 1
    person_2._node_id = 1
    person_2._node_labels = ["Person"]
    assert person_1 == person_2


def test_dictionary_deserialisation():
    pass


def test_automatic_deserialisation_from_database():
    db = Memgraph()

    db.execute("create (:Person {id: 1, name: 'person'});")
    db.execute("create (:Alice {id: 8, name: 'alice'});")
    db.execute("match (a:Alice) match(b:Person) create (a)-[:FRIENDS]->(b);")

    result = list(db.execute_and_fetch("match (a)-[r]->(b) return a, r, b"))
    for node in result:
        a = node["a"]
        assert isinstance(a, Alice)
        assert a.id == 8
        assert a.name == "alice"
        assert a._node_labels == {"Alice"}
        assert isinstance(a._node_id, int)
        assert a._properties == {"id": 8, "name": "alice"}
        assert isinstance(a._id, int)

        r = node["r"]
        assert isinstance(r, Friends)
        assert r._type == "FRIENDS"
        assert isinstance(r._relationship_id, int)
        assert isinstance(r._start_node_id, int)
        assert isinstance(r._end_node_id, int)
        assert r._properties == {}
        assert isinstance(r._id, int)

        b = node["b"]
        assert isinstance(b, Person)
        assert b.id == 1
        assert b.name == "person"
        assert b._node_labels == {"Person"}
        assert isinstance(b._node_id, int)
        assert b._properties == {"id": 1, "name": "person"}
        assert isinstance(b._id, int)

    db.drop_database()


def test_path_deserialisation():
    db = Memgraph()
    db.execute("create (:Person {id: 1, name: 'person'});")
    db.execute("create (:Alice {id: 8, name: 'alice'});")
    db.execute("match (a:Alice) match(b:Person) create (a)-[:FRIENDS]->(b);")
    result = list(db.execute_and_fetch("MATCH p = ()-[*1]-() RETURN p"))
    path = result[0]["p"]
    assert isinstance(path, Path)
    assert len(path._nodes) == 2
    assert len(path._relationships) == 1
    db.drop_database()
