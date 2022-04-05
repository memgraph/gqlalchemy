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

from pydantic import Field
from pathlib import Path

import pytest
from gqlalchemy import Memgraph
from gqlalchemy.models import Node, Relationship


def get_data_dir() -> Path:
    return Path(__file__).parents[0].joinpath("data")


@pytest.fixture
def memgraph() -> Memgraph:
    memgraph = Memgraph()
    memgraph.ensure_indexes([])
    memgraph.ensure_constraints([])
    memgraph.drop_database()

    yield memgraph

    memgraph.ensure_indexes([])
    memgraph.ensure_constraints([])


@pytest.fixture
def memgraph_without_dropping_constraints() -> Memgraph:
    memgraph = Memgraph()
    memgraph.drop_database()

    yield memgraph

    memgraph.drop_database()


@pytest.fixture
def populated_memgraph(dataset_file: str) -> Memgraph:
    memgraph = Memgraph()
    memgraph.ensure_indexes([])
    memgraph.ensure_constraints([])
    memgraph.drop_database()
    with get_data_dir().joinpath(dataset_file).open("r") as dataset:
        for query in dataset:
            memgraph.execute(query)

    yield memgraph

    memgraph.drop_database()


@pytest.fixture
def relationship_type():
    return Relationship


@pytest.fixture
def node_type():
    return Node


@pytest.fixture
def make_attributes_with_annotations():
    def _make_attributes_with_annotations(attributes):
        return {"__annotations__": attributes, **{key: None for key in attributes}}

    return _make_attributes_with_annotations


@pytest.fixture
def make_class(make_attributes_with_annotations):
    def _make_class(classname, bases, attributes, with_annotations, **kwargs):
        new_attributes = attributes if with_annotations is False else make_attributes_with_annotations(attributes)
        return type(classname, bases, new_attributes, **kwargs)

    return _make_class


@pytest.fixture
def make_relationship(make_class, relationship_type):
    def _make_relationship(classname, attributes, with_annotations, **kwargs):
        return make_class(classname, (relationship_type,), attributes, with_annotations, **kwargs)

    return _make_relationship


@pytest.fixture
def make_node(make_class, node_type):
    def _make_node(classname, attributes, with_annotations, **kwargs):
        return make_class(classname, (node_type,), attributes, with_annotations, **kwargs)

    return _make_node


@pytest.fixture
def make_memgraph_relationship(make_relationship):
    def _make_memgraph_relationship(classname, **kwargs):
        return make_relationship(classname, {}, False, **kwargs)

    return _make_memgraph_relationship


@pytest.fixture
def make_memgraph_node_attributes(memgraph):
    return {"name": Field(default=str(), index=True, unique=True, db=memgraph)}


@pytest.fixture
def make_memgraph_node(make_node, make_memgraph_node_attributes):
    def _memgraph_node(classname, **kwargs):
        return make_node(classname, make_memgraph_node_attributes, False, **kwargs)

    return _memgraph_node


@pytest.fixture
def make_user_class(make_memgraph_node):
    return make_memgraph_node("User")


@pytest.fixture
def make_follows_test_class(make_memgraph_relationship):
    return make_memgraph_relationship("Follows_test", type="FOLLOWS")


@pytest.fixture
def make_simple_user(make_user_class):
    def _make_simple_user(**kwargs):
        return make_user_class(**kwargs)

    return _make_simple_user


@pytest.fixture
def make_simple_follows(make_follows_test_class):
    def _make_simple_follows(**kwargs):
        return make_follows_test_class(**kwargs)

    return _make_simple_follows
