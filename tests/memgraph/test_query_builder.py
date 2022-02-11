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
from gqlalchemy import InvalidMatchChainException, QueryBuilder, match, call, unwind, with_, Node, Relationship, Field
from gqlalchemy.memgraph import Memgraph
from typing import Optional
from unittest.mock import patch


def test_invalid_match_chain_throws_exception():
    with pytest.raises(InvalidMatchChainException):
        QueryBuilder().node(":Label", "n").node(":Label", "m").return_()


def test_simple_create(memgraph):
    query_builder = QueryBuilder().create().node("L1", variable="n").to("TO").node("L2").return_()
    expected_query = " CREATE (n:L1)-[:TO]->(:L2) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_simple_match(memgraph):
    query_builder = QueryBuilder().match().node("L1", variable="n").to("TO").node("L2").return_()
    expected_query = " MATCH (n:L1)-[:TO]->(:L2) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_simple_merge(memgraph):
    query_builder = QueryBuilder().merge().node("L1", variable="n").to("TO").node("L2").return_()
    expected_query = " MERGE (n:L1)-[:TO]->(:L2) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_simple_create_with_variables(memgraph):
    query_builder = (
        QueryBuilder().create().node("L1", variable="n").to("TO", variable="e").node("L2", variable="m").return_()
    )
    expected_query = " CREATE (n:L1)-[e:TO]->(m:L2) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_simple_match_with_variables(memgraph):
    query_builder = (
        QueryBuilder().match().node("L1", variable="n").to("TO", variable="e").node("L2", variable="m").return_()
    )
    expected_query = " MATCH (n:L1)-[e:TO]->(m:L2) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_simple_merge_with_variables(memgraph):
    query_builder = (
        QueryBuilder().merge().node("L1", variable="n").to("TO", variable="e").node("L2", variable="m").return_()
    )
    expected_query = " MERGE (n:L1)-[e:TO]->(m:L2) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_simple_with_multiple_labels(memgraph):
    query_builder = (
        QueryBuilder().match().node(["L1", "L2", "L3"], variable="n").to("TO").node("L2", variable="m").return_()
    )
    expected_query = " MATCH (n:L1:L2:L3)-[:TO]->(m:L2) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_multiple_matches(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node("L1", variable="n")
        .to("TO")
        .node("L2", variable="m")
        .match(True)
        .node(variable="n")
        .to("TO")
        .node("L3")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) OPTIONAL MATCH (n)-[:TO]->(:L3) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_multiple_merges(memgraph):
    query_builder = (
        QueryBuilder()
        .merge()
        .node("L1", variable="n")
        .to("TO")
        .node("L2", variable="m")
        .merge()
        .node(variable="n")
        .to("TO")
        .node("L3")
        .return_()
    )
    expected_query = " MERGE (n:L1)-[:TO]->(m:L2) MERGE (n)-[:TO]->(:L3) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_where(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node("L1", variable="n")
        .to("TO")
        .node("L2", variable="m")
        .where("n.name", "=", "best_name")
        .or_where("m.id", "<", 4)
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = 'best_name' OR m.id < 4 RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_get_single(memgraph):
    query_builder = QueryBuilder().match().node("L1", variable="n").to("TO").node("L2", variable="m").return_({"n": ""})
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN n "

    with patch.object(Memgraph, "execute_and_fetch", return_value=iter([{"n": None}])) as mock:
        query_builder.get_single(retrieve="n")

    mock.assert_called_with(expected_query)


def test_return_empty(memgraph):
    query_builder = QueryBuilder().match().node("L1", variable="n").to("TO").node("L2", variable="m").return_()
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_return_alias(memgraph):
    query_builder = (
        QueryBuilder().match().node("L1", variable="n").to("TO").node("L2", variable="m").return_({"L1": "first"})
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 AS first "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_return_alias_same_as_variable(memgraph):
    query_builder = (
        QueryBuilder().match().node("L1", variable="n").to("TO").node("L2", variable="m").return_({"L1": "L1"})
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_return_alias_empty(memgraph):
    query_builder = (
        QueryBuilder().match().node("L1", variable="n").to("TO").node("L2", variable="m").return_({"L1": ""})
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_call_procedure_pagerank(memgraph):
    query_builder = (
        QueryBuilder()
        .call(procedure="pagerank.get")
        .yield_({"node": "", "rank": ""})
        .return_({"node": "node", "rank": "rank"})
    )
    expected_query = " CALL pagerank.get() YIELD node, rank RETURN node, rank "
    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_call_procedure_node2vec(memgraph):
    query_builder = QueryBuilder().call(procedure="node2vec_online.get_embeddings", arguments="False, 2.0, 0.5")
    expected_query = " CALL node2vec_online.get_embeddings(False, 2.0, 0.5) "
    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_call_procedure_nxalg_betweenness_centrality(memgraph):
    query_builder = (
        QueryBuilder()
        .call(procedure="nxalg.betweenness_centrality", arguments="20, True")
        .yield_()
        .return_({"node": "", "betweenness": ""})
    )
    expected_query = " CALL nxalg.betweenness_centrality(20, True) YIELD * RETURN node, betweenness "
    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_unwind(memgraph):
    query_builder = (
        QueryBuilder().unwind(list_expression="[1, 2, 3, null]", variable="x").return_({"x": "", "'val'": "y"})
    )
    expected_query = " UNWIND [1, 2, 3, null] AS x RETURN x, 'val' AS y "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_with_empty(memgraph):
    query_builder = QueryBuilder().match().node("L1", variable="n").to("TO").node("L2", variable="m").with_()
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WITH * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_with(memgraph):
    query_builder = QueryBuilder().match().node(variable="n").with_({"n": ""})
    expected_query = " MATCH (n) WITH n "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_union(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(variable="n1", labels="Node1")
        .return_({"n1": ""})
        .union(include_duplicates=False)
        .match()
        .node(variable="n2", labels="Node2")
        .return_({"n2": ""})
    )
    expected_query = " MATCH (n1:Node1) RETURN n1 UNION MATCH (n2:Node2) RETURN n2 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_union_all(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(variable="n1", labels="Node1")
        .return_({"n1": ""})
        .union()
        .match()
        .node(variable="n2", labels="Node2")
        .return_({"n2": ""})
    )
    expected_query = " MATCH (n1:Node1) RETURN n1 UNION ALL MATCH (n2:Node2) RETURN n2 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_delete(memgraph):
    query_builder = QueryBuilder().match().node(variable="n1", labels="Node1").delete({"n1"})
    expected_query = " MATCH (n1:Node1) DELETE n1 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_delete_detach(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(variable="n1", labels="Node1")
        .to(edge_label="EDGE")
        .node(variable="n2", labels="Node2")
        .delete(["n1", "n2"], True)
    )
    expected_query = " MATCH (n1:Node1)-[:EDGE]->(n2:Node2) DETACH DELETE n1, n2 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_remove_property(memgraph):
    query_builder = QueryBuilder().match().node(variable="n", labels="Node").remove({"n.name"})
    expected_query = " MATCH (n:Node) REMOVE n.name "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_remove_label(memgraph):
    query_builder = QueryBuilder().match().node(variable="n", labels=["Node1", "Node2"]).remove({"n:Node2"})
    expected_query = " MATCH (n:Node1:Node2) REMOVE n:Node2 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_remove_property_and_label(memgraph):
    query_builder = QueryBuilder().match().node(variable="n", labels=["Node1", "Node2"]).remove(["n:Node2", "n.name"])
    expected_query = " MATCH (n:Node1:Node2) REMOVE n:Node2, n.name "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_orderby(memgraph):
    query_builder = QueryBuilder().match().node(variable="n").order_by("n.id")
    expected_query = " MATCH (n) ORDER BY n.id "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_orderby_desc(memgraph):
    query_builder = QueryBuilder().match().node(variable="n").order_by("n.id DESC")
    expected_query = " MATCH (n) ORDER BY n.id DESC "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_limit(memgraph):
    query_builder = QueryBuilder().match().node(variable="n").limit("3")
    expected_query = " MATCH (n) LIMIT 3 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_skip(memgraph):
    query_builder = QueryBuilder().match().node(variable="n").return_({"n": ""}).skip("1")
    expected_query = " MATCH (n) RETURN n SKIP 1 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_base_class_match(memgraph):
    query_builder = match().node(variable="n").return_({"n": ""})
    expected_query = " MATCH (n) RETURN n "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_base_class_call(memgraph):
    query_builder = call("pagerank.get").yield_().return_()
    expected_query = " CALL pagerank.get() YIELD * RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_base_class_unwind(memgraph):
    query_builder = unwind("[1, 2, 3]", "x").return_({"x": "x"})
    expected_query = " UNWIND [1, 2, 3] AS x RETURN x "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_base_class_with(memgraph):
    query_builder = with_({"10": "n"}).return_({"n": ""})
    expected_query = " WITH 10 AS n RETURN n "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_from(memgraph):
    query_builder = match().node("L1", variable="n").from_("TO", variable="e").node("L2", variable="m").return_()
    expected_query = " MATCH (n:L1)<-[e:TO]-(m:L2) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_add_string_partial(memgraph):
    query_builder = match().node("Node1", variable="n").to("TO", variable="e").add_custom_cypher("(m:L2) ").return_()
    expected_query = " MATCH (n:Node1)-[e:TO]->(m:L2) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_add_string_complete(memgraph):
    query_builder = QueryBuilder().add_custom_cypher("MATCH (n) RETURN n")
    expected_query = "MATCH (n) RETURN n"

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


class User(Node):
    name: Optional[str] = Field(index=True, unique=True, db=Memgraph())


class Follows_test(Relationship, type="FOLLOWS"):
    pass


@pytest.fixture
def cleanup_class():
    yield
    global User
    del User  # noqa F821


@pytest.mark.usefixtures("cleanup_class")
def test_node_object(memgraph):
    user_1 = User(name="Ron")
    user_2 = User(name="Leslie")
    follows = Follows_test()
    query_builder = (
        QueryBuilder()
        .match()
        .node(node=user_1, variable="user_1")
        .to(relationship=follows)
        .node(node=user_2, variable="user_2")
        .return_()
    )
    expected_query = " MATCH (user_1:User {name: 'Ron'})-[:FOLLOWS]->(user_2:User {name: 'Leslie'}) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)
