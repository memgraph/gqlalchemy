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

from unittest.mock import patch

from gqlalchemy import call, create, match, merge
from gqlalchemy.vendors.memgraph import Memgraph
from gqlalchemy.query_builders.declarative_base import CallPartialQuery, Operator


def test_call_procedure_arguments_string():
    call_procedure = CallPartialQuery("dummy.procedure", "'a', 'b'").construct_query()
    assert call_procedure == " CALL dummy.procedure('a', 'b') "


def test_call_procedure_arguments_tuple():
    call_procedure = CallPartialQuery("dummy.procedure", ("a", "b")).construct_query()
    assert call_procedure == ' CALL dummy.procedure("a", "b") '


def test_call_procedure_arguments_tuple_string_int():
    call_procedure = CallPartialQuery("dummy.procedure", ("a", 1)).construct_query()
    assert call_procedure == ' CALL dummy.procedure("a", 1) '


def test_call_procedures_1(memgraph):
    query_builder = call("pagerank.get").yield_().return_()
    expected_query = " CALL pagerank.get() YIELD * RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_call_procedures_2(memgraph):
    query_builder = (
        call("json_util.load_from_url", "https://some-url.com")
        .yield_({"objects": "objects"})
        .return_({"objects": "objects"})
    )

    expected_query = " CALL json_util.load_from_url(https://some-url.com) YIELD objects RETURN objects "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_create_nodes_relationships_1(memgraph):
    query_builder = create().node(labels="Person", name="Ron")

    expected_query = ' CREATE (:Person {name: "Ron"})'

    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_create_nodes_relationships_2(memgraph):
    query_builder = merge().node(labels="Person", name="Leslie")

    expected_query = ' MERGE (:Person {name: "Leslie"})'

    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_create_nodes_relationships_3(memgraph):
    query_builder = (
        create()
        .node(labels="Person", name="Leslie")
        .to(relationship_type="FRIENDS_WITH")
        .node(labels="Person", name="Ron")
    )

    expected_query = ' CREATE (:Person {name: "Leslie"})-[:FRIENDS_WITH]->(:Person {name: "Ron"})'

    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_delete_remove_objects_1(memgraph):
    query_builder = match().node("Person", variable="p").delete(["p"])

    expected_query = " MATCH (p:Person) DELETE p "

    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_delete_remove_objects_2(memgraph):
    query_builder = match().node("Person").to("FRIENDS_WITH", variable="f").node("Person").delete(["f"])

    expected_query = " MATCH (:Person)-[f:FRIENDS_WITH]->(:Person) DELETE f "

    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_delete_remove_objects_3(memgraph):
    query_builder = match().node("Person", variable="p").remove(["p.name"])

    expected_query = " MATCH (p:Person) REMOVE p.name "

    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_filter_data_1(memgraph):
    query_builder = (
        match()
        .node("Person", variable="p1")
        .to("FRIENDS_WITH")
        .node("Person", variable="p2")
        .where(item="n.name", operator=Operator.EQUAL, literal="Ron")
        .or_where(item="m.id", operator=Operator.EQUAL, literal=0)
        .return_()
    )

    expected_query = ' MATCH (p1:Person)-[:FRIENDS_WITH]->(p2:Person) WHERE n.name = "Ron" OR m.id = 0 RETURN * '

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_return_results_1(memgraph):
    query_builder = match().node(labels="Person", variable="p").return_()

    expected_query = " MATCH (p:Person) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_return_results_2(memgraph):
    query_builder = (
        match().node(labels="Person", variable="p1").to().node(labels="Person", variable="p2").return_({"p1": "p1"})
    )

    expected_query = " MATCH (p1:Person)-[]->(p2:Person) RETURN p1 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_return_results_2_new(memgraph):
    query_builder = (
        match()
        .node(labels="Person", variable="p1")
        .to()
        .node(labels="Person", variable="p2")
        .return_([("p1", "first"), "p2"])
    )

    expected_query = " MATCH (p1:Person)-[]->(p2:Person) RETURN p1 AS first, p2 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_return_results_3(memgraph):
    query_builder = match().node(labels="Person", variable="p").return_().limit(10)

    expected_query = " MATCH (p:Person) RETURN * LIMIT 10 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_return_results_4(memgraph):
    query_builder = match().node(labels="Person", variable="p").return_({"p": "p"}).order_by("p.name DESC")

    expected_query = " MATCH (p:Person) RETURN p ORDER BY p.name DESC "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)
