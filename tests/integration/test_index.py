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

import pytest

from gqlalchemy import Field, Node
from gqlalchemy.models import MemgraphIndex
from gqlalchemy.exceptions import GQLAlchemyDatabaseMissingInNodeClassError


def test_index_label(memgraph):
    class Animal(Node, index=True, db=memgraph):
        name: str

    actual_index = memgraph.get_indexes()

    assert set(actual_index) == {MemgraphIndex("Animal")}


def test_index_property(memgraph):
    class Human(Node):
        id: str = Field(index=True, db=memgraph)

    actual_index = memgraph.get_indexes()

    assert set(actual_index) == {MemgraphIndex("Human", "id")}


def test_missing_db_in_node_class(memgraph):
    with pytest.raises(GQLAlchemyDatabaseMissingInNodeClassError):

        class User(Node, index=True):
            id: str


def test_db_in_node_class(memgraph):
    class User(Node, db=memgraph):
        id: str = Field(index=True)

    actual_index = memgraph.get_indexes()
    assert set(actual_index) == {MemgraphIndex("User", "id")}


def test_db_in_node_and_property(memgraph):
    class User(Node, db=memgraph):
        id: str = Field(index=True, db=memgraph)

    actual_index = memgraph.get_indexes()
    assert set(actual_index) == {MemgraphIndex("User", "id")}


def test_index_on_label_and_property(memgraph):
    class User(Node, index=True, db=memgraph):
        id: str = Field(index=True, db=memgraph)

    actual_index = memgraph.get_indexes()
    assert set(actual_index) == {MemgraphIndex("User", "id"), MemgraphIndex("User")}


def test_false_index_in_node_class(memgraph):
    class User(Node, index=False, db=memgraph):
        id: str

    actual_index = memgraph.get_indexes()
    assert set(actual_index) == set()


def test_false_index_no_db_in_node_class(memgraph):
    class User(Node, index=False):
        id: str

    actual_index = memgraph.get_indexes()
    assert set(actual_index) == set()


def test_false_index_with_db_in_node_class(memgraph):
    class User(Node, index=False, db=memgraph):
        id: str

    actual_index = memgraph.get_indexes()
    assert set(actual_index) == set()


def test_index_attr(memgraph):
    class Example(Node):
        first_name: str = Field(index=True, db=memgraph)
        last_name: str = Field(index=False, db=memgraph)

    actual_index = memgraph.get_indexes()

    assert set(actual_index) == {MemgraphIndex("Example", "first_name")}


def test_no_index(memgraph):
    assert memgraph.get_indexes() == []


def test_create_index(memgraph):
    index1 = MemgraphIndex("NodeOne")
    index2 = MemgraphIndex("NodeOne", "name")

    memgraph.create_index(index1)
    memgraph.create_index(index2)

    assert set(memgraph.get_indexes()) == {index1, index2}


def test_create_duplicate_index(memgraph):
    index = MemgraphIndex("NodeOne")

    memgraph.create_index(index)
    memgraph.create_index(index)

    assert set(memgraph.get_indexes()) == {index}


def test_drop_index(memgraph):
    index1 = MemgraphIndex("NodeOne")
    index2 = MemgraphIndex("NodeOne", "name")

    memgraph.create_index(index1)
    memgraph.create_index(index2)

    memgraph.drop_index(index1)
    assert set(memgraph.get_indexes()) == {index2}

    memgraph.drop_index(index2)
    assert set(memgraph.get_indexes()) == set()


def test_drop_duplicate_index(memgraph):
    index = MemgraphIndex("NodeOne")

    memgraph.create_index(index)
    memgraph.drop_index(index)
    assert set(memgraph.get_indexes()) == set()

    memgraph.drop_index(index)
    assert set(memgraph.get_indexes()) == set()


def test_ensure_index(memgraph):
    old_indexes = [
        MemgraphIndex("NodeOne"),
        MemgraphIndex("NodeOne", "name"),
        MemgraphIndex("NodeTwo"),
        MemgraphIndex("NodeTwo", "age"),
    ]
    for old_index in old_indexes:
        memgraph.create_index(old_index)

    assert set(memgraph.get_indexes()) == set(old_indexes)

    new_indexes = [
        MemgraphIndex("NodeOne", "name"),
        MemgraphIndex("NodeTwo"),
        MemgraphIndex("NodeThree"),
        MemgraphIndex("NodeFour", "created_at"),
    ]
    memgraph.ensure_indexes(new_indexes)

    assert set(memgraph.get_indexes()) == set(new_indexes)


def test_create_and_get_label_index(memgraph):
    new_index = MemgraphIndex("Person")
    memgraph.create_index(new_index)

    indexes = memgraph.get_indexes()

    assert set(indexes) == {new_index}


def test_create_and_get_label_index_with_type(memgraph):
    new_index = MemgraphIndex("Person", None, index_type="LABEL_INDEX_TYPE")
    memgraph.create_index(new_index)

    indexes = memgraph.get_indexes()

    assert set(indexes) == {new_index}


def test_create_and_get_label_property_index(memgraph):
    new_index = MemgraphIndex("Person", "name")
    memgraph.create_index(new_index)

    indexes = memgraph.get_indexes()

    assert set(indexes) == {new_index}


def test_create_and_get_label_property_index_with_type(memgraph):
    new_index = MemgraphIndex("Person", "name", index_type="LABEL_INDEX_TYPE")
    memgraph.create_index(new_index)

    indexes = memgraph.get_indexes()

    assert set(indexes) == {new_index}


def test_create_and_get_composite_index(memgraph):
    new_index = MemgraphIndex("Person", ("name", "age"))
    memgraph.create_index(new_index)

    indexes = memgraph.get_indexes()

    assert set(indexes) == {new_index}


def test_create_and_get_composite_index_with_type(memgraph):
    new_index = MemgraphIndex("Person", ("name", "age"), index_type="LABEL_INDEX_TYPE")
    memgraph.create_index(new_index)

    indexes = memgraph.get_indexes()

    assert set(indexes) == {new_index}


def test_create_and_get_multiple_label_indexes(memgraph):
    label_index = MemgraphIndex("Person")
    label_prop_index = MemgraphIndex("Person", "name")
    label_composite_index = MemgraphIndex("Person", ("name", "age"))

    memgraph.create_index(label_index)
    memgraph.create_index(label_prop_index)
    memgraph.create_index(label_composite_index)

    indexes = memgraph.get_indexes()

    assert set(indexes) == {label_index, label_prop_index, label_composite_index}


def test_create_list_prop_index(memgraph):
    label_prop_index = MemgraphIndex("Person", ["name"])
    memgraph.create_index(label_prop_index)

    indexes = memgraph.get_indexes()

    assert set(indexes) == {label_prop_index}


def test_create_list_prop_composite_index(memgraph):
    label_prop_index = MemgraphIndex("Person", ["name", "age"])
    memgraph.create_index(label_prop_index)

    indexes = memgraph.get_indexes()

    assert set(indexes) == {label_prop_index}


def test_create_edge_type_index(memgraph):
    edge_type_index = MemgraphIndex("REL", None, index_type="EDGE_INDEX_TYPE")
    memgraph.create_index(edge_type_index)

    indexes = memgraph.get_indexes()

    assert set(indexes) == {edge_type_index}


def test_create_edge_type_property_index(memgraph):
    edge_type_property_index = MemgraphIndex("REL", "name", index_type="EDGE_INDEX_TYPE")
    memgraph.create_index(edge_type_property_index)

    indexes = memgraph.get_indexes()

    assert set(indexes) == {edge_type_property_index}


def test_create_global_edge_index(memgraph):
    global_edge_index = MemgraphIndex(None, "name", index_type="EDGE_GLOBAL_INDEX_TYPE")
    memgraph.create_index(global_edge_index)

    indexes = memgraph.get_indexes()

    assert set(indexes) == {global_edge_index}


def test_create_point_index(memgraph):
    point_index = MemgraphIndex("Person", "year", index_type="POINT_INDEX_TYPE")
    memgraph.create_index(point_index)

    indexes = memgraph.get_indexes()
    assert set(indexes) == {point_index}


def test_drop_index_all(memgraph):
    label_index = MemgraphIndex("Person")
    label_prop_index = MemgraphIndex("Person", "name")
    label_composite_index = MemgraphIndex("Person", ("name", "age"))
    edge_type_index = MemgraphIndex("REL", None, index_type="EDGE_INDEX_TYPE")
    edge_type_property_index = MemgraphIndex("REL", "name", index_type="EDGE_INDEX_TYPE")
    global_edge_index = MemgraphIndex(None, "name", index_type="EDGE_GLOBAL_INDEX_TYPE")
    point_index = MemgraphIndex("Person", "year", index_type="POINT_INDEX_TYPE")

    memgraph.create_index(label_index)
    memgraph.create_index(label_prop_index)
    memgraph.create_index(label_composite_index)
    memgraph.create_index(edge_type_index)
    memgraph.create_index(edge_type_property_index)
    memgraph.create_index(global_edge_index)
    memgraph.create_index(point_index)

    memgraph.drop_indexes()

    indexes = memgraph.get_indexes()

    assert set(indexes) == set()


def test_ensure_index_all(memgraph):
    label_index = MemgraphIndex("Person")
    label_prop_index = MemgraphIndex("Person", "name")
    label_composite_index = MemgraphIndex("Person", ("name", "age"))
    edge_type_index = MemgraphIndex("REL", None, index_type="EDGE_INDEX_TYPE")
    edge_type_property_index = MemgraphIndex("REL", "name", index_type="EDGE_INDEX_TYPE")
    global_edge_index = MemgraphIndex(None, "name", index_type="EDGE_GLOBAL_INDEX_TYPE")
    point_index = MemgraphIndex("Person", "year", index_type="POINT_INDEX_TYPE")

    memgraph.ensure_indexes(
        [
            label_index,
            label_prop_index,
            label_composite_index,
            edge_type_index,
            edge_type_property_index,
            global_edge_index,
            point_index,
        ]
    )

    indexes = memgraph.get_indexes()

    assert set(indexes) == {
        label_index,
        label_prop_index,
        label_composite_index,
        edge_type_index,
        edge_type_property_index,
        global_edge_index,
        point_index,
    }


def test_different_composite_index(memgraph):
    label_composite_index_1 = MemgraphIndex("Person", ("name", "age"))
    label_composite_index_2 = MemgraphIndex("Person", ("age", "name"))

    memgraph.create_index(label_composite_index_1)
    memgraph.create_index(label_composite_index_2)

    indexes = memgraph.get_indexes()

    assert set(indexes) == {label_composite_index_1, label_composite_index_2}
    assert indexes[0] != indexes[1]

    memgraph.drop_indexes()

    indexes = memgraph.get_indexes()

    assert set(indexes) == set()


def test_create_and_get_nested_label_property_index(memgraph):
    new_index = MemgraphIndex("Person", "specifications.dimensions.width")
    memgraph.create_index(new_index)

    indexes = memgraph.get_indexes()

    assert set(indexes) == {new_index}


def test_create_and_get_nested_label_property_index_with_type(memgraph):
    new_index = MemgraphIndex("Person", "specifications.dimensions.width", index_type="LABEL_INDEX_TYPE")
    memgraph.create_index(new_index)

    indexes = memgraph.get_indexes()

    assert set(indexes) == {new_index}
