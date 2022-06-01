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

from gqlalchemy import Node, Path, Relationship
from gqlalchemy.models import GraphObject


def test_simple_json_deserialisation():
    class Person(Node):
        id: Optional[int]
        name: Optional[str]

    person_json = '{"labels":"Person", "id": 9, "name": "person"}'
    person = Person.parse_raw(person_json)
    assert str(person) == str(Person(id=9, name="person"))


def test_json_deserialisation():
    class Person(Node):
        id: Optional[int]
        name: Optional[str]

    person_json = '{"id": 9, "name": "person", "_labels": ["Person"], "_id": 1, "_id": 1}'
    person_1 = GraphObject.parse_raw(person_json)
    person_2 = Person(id=9, name="person")
    person_2._id = 1
    person_2._id = 1
    person_2._labels = ["Person"]
    assert str(person_1) == str(person_2)


def test_dictionary_deserialisation():
    pass


def test_automatic_deserialisation_from_database(memgraph):
    class Person(Node):
        id: Optional[int]
        name: Optional[str]

    class Alice(Node):
        id: Optional[int]
        name: Optional[str]

    class Friends(Relationship, type="FRIENDS"):
        pass

    memgraph.execute("create (:Person {id: 1, name: 'person'});")
    memgraph.execute("create (:Alice {id: 8, name: 'alice'});")
    memgraph.execute("match (a:Alice) match(b:Person) create (a)-[:FRIENDS]->(b);")

    result = list(memgraph.execute_and_fetch("match (a)-[r]->(b) return a, r, b"))
    for node in result:
        a = node["a"]
        assert isinstance(a, Alice)
        assert a.id == 8
        assert a.name == "alice"
        assert a._labels == {"Alice"}
        assert isinstance(a._id, int)
        assert a._properties == {"id": 8, "name": "alice"}
        assert isinstance(a._id, int)

        r = node["r"]
        assert isinstance(r, Friends)
        assert r._type == "FRIENDS"
        assert isinstance(r._id, int)
        assert isinstance(r._start_node_id, int)
        assert isinstance(r._end_node_id, int)
        assert r._properties == {}
        assert isinstance(r._id, int)

        b = node["b"]
        assert isinstance(b, Person)
        assert b.id == 1
        assert b.name == "person"
        assert b._labels == {"Person"}
        assert isinstance(b._id, int)
        assert b._properties == {"id": 1, "name": "person"}
        assert isinstance(b._id, int)


def test_path_deserialisation(memgraph):
    memgraph.execute("create (:Person {id: 1, name: 'person'});")
    memgraph.execute("create (:Alice {id: 8, name: 'alice'});")
    memgraph.execute("match (a:Alice) match(b:Person) create (a)-[:FRIENDS]->(b);")
    result = list(memgraph.execute_and_fetch("MATCH p = ()-[*1]-() RETURN p"))
    path = result[0]["p"]
    assert isinstance(path, Path)
    assert len(path._nodes) == 2
    assert len(path._relationships) == 1
