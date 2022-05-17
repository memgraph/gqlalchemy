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

from gqlalchemy.exceptions import (
    GQLAlchemyLiteralAndExpressionMissingInWhere,
    GQLAlchemyExtraKeywordArgumentsInWhere,
)
import pytest
from gqlalchemy import (
    InvalidMatchChainException,
    QueryBuilder,
    match,
    call,
    create,
    load_csv,
    unwind,
    with_,
    merge,
    return_,
    Node,
    Relationship,
    Field,
)
from gqlalchemy.memgraph import Memgraph
from typing import Optional
from unittest.mock import patch
from gqlalchemy.exceptions import GQLAlchemyMissingOrder, GQLAlchemyOrderByTypeError
from gqlalchemy.query_builder import Order


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


def test_with_empty(memgraph):
    query_builder = QueryBuilder().match().node("L1", variable="n").to("TO").node("L2", variable="m").with_()
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WITH * "

    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_with(memgraph):
    query_builder = QueryBuilder().match().node(variable="n").with_({"n": ""})
    expected_query = " MATCH (n) WITH n "

    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_union(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(variable="n1", labels="Node1")
        .return_("n1")
        .union(include_duplicates=False)
        .match()
        .node(variable="n2", labels="Node2")
        .return_("n2")
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
        .return_("n1")
        .union()
        .match()
        .node(variable="n2", labels="Node2")
        .return_("n2")
    )
    expected_query = " MATCH (n1:Node1) RETURN n1 UNION ALL MATCH (n2:Node2) RETURN n2 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_delete(memgraph):
    query_builder = QueryBuilder().match().node(variable="n1", labels="Node1").delete({"n1"})
    expected_query = " MATCH (n1:Node1) DELETE n1 "

    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()
        mock.assert_called_with(expected_query)


def test_simple_merge(memgraph):
    query_builder = merge().node("L1", variable="n").to("TO").node("L2")
    expected_query = " MERGE (n:L1)-[:TO]->(:L2)"

    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_base_merge(memgraph):
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
    query_builder = merge().node("L1", variable="n").to("TO", variable="e").node("L2", variable="m").return_()
    expected_query = " MERGE (n:L1)-[e:TO]->(m:L2) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_base_merge_with_variables(memgraph):
    query_builder = (
        QueryBuilder().merge().node("L1", variable="n").to("TO", variable="e").node("L2", variable="m").return_()
    )
    expected_query = " MERGE (n:L1)-[e:TO]->(m:L2) RETURN * "
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

    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_remove_property(memgraph):
    query_builder = QueryBuilder().match().node(variable="n", labels="Node").remove({"n.name"})
    expected_query = " MATCH (n:Node) REMOVE n.name "

    with patch.object(Memgraph, "execute", return_value=None) as mock:
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


def test_load_csv_with_header(memgraph):
    query_builder = QueryBuilder().load_csv("path/to/my/file.csv", True, "row").return_()
    expected_query = " LOAD CSV FROM 'path/to/my/file.csv' WITH HEADER AS row RETURN * "
    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()
    mock.assert_called_with(expected_query)


def test_load_csv_no_header(memgraph):
    query_builder = QueryBuilder().load_csv("path/to/my/file.csv", False, "row").return_()
    expected_query = " LOAD CSV FROM 'path/to/my/file.csv' NO HEADER AS row RETURN * "
    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()
    mock.assert_called_with(expected_query)


def test_where_literal(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node("L1", variable="n")
        .to("TO")
        .node("L2", variable="m")
        .where(item="n.name", operator="=", literal="best_name")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = 'best_name' RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_where_property(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator="=", expression="m.name")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = m.name RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_where_not_property(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where_not(item="n.name", operator="=", expression="m.name")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE NOT n.name = m.name RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_where_label(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n", operator=":", expression="Node")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_where_not_label(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where_not(item="n", operator=":", expression="Node")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE NOT n:Node RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_where_literal_and_expression_missing(memgraph):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissingInWhere):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(edge_label="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator="=")
            .return_()
        )


def test_where_not_literal_and_expression_missing(memgraph):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissingInWhere):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(edge_label="TO")
            .node(labels="L2", variable="m")
            .where_not(item="n.name", operator="=")
            .return_()
        )


def test_where_extra_values(memgraph):
    with pytest.raises(GQLAlchemyExtraKeywordArgumentsInWhere):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(edge_label="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator="=", literal="best_name", expression="Node")
            .return_()
        )


def test_where_not_extra_values(memgraph):
    with pytest.raises(GQLAlchemyExtraKeywordArgumentsInWhere):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(edge_label="TO")
            .node(labels="L2", variable="m")
            .where_not(item="n.name", operator="=", literal="best_name", expression="Node")
            .return_()
        )


def test_or_where_literal(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator="=", literal="best_name")
        .or_where(item="m.id", operator="<", literal=4)
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = 'best_name' OR m.id < 4 RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_or_not_where_literal(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator="=", literal="best_name")
        .or_not_where(item="m.id", operator="<", literal=4)
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = 'best_name' OR NOT m.id < 4 RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_or_where_property(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator="=", expression="m.name")
        .or_where(item="m.name", operator="=", expression="n.last_name")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = m.name OR m.name = n.last_name RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_or_not_where_property(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator="=", expression="m.name")
        .or_not_where(item="m.name", operator="=", expression="n.last_name")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = m.name OR NOT m.name = n.last_name RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_or_where_label(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n", operator=":", expression="Node")
        .or_where(item="m", operator=":", expression="User")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node OR m:User RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_or_not_where_label(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n", operator=":", expression="Node")
        .or_not_where(item="m", operator=":", expression="User")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node OR NOT m:User RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_or_where_literal_and_expression_missing(memgraph):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissingInWhere):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(edge_label="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator="=", literal="my_name")
            .or_where(item="m.name", operator="=")
            .return_()
        )


def test_or_not_where_literal_and_expression_missing(memgraph):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissingInWhere):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(edge_label="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator="=", literal="my_name")
            .or_not_where(item="m.name", operator="=")
            .return_()
        )


def test_or_where_extra_values(memgraph):
    with pytest.raises(GQLAlchemyExtraKeywordArgumentsInWhere):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(edge_label="TO")
            .node(labels="L2", variable="m")
            .where(item="m.name", operator="=", literal="best_name")
            .or_where(item="n.name", operator="=", literal="best_name", expression="Node")
            .return_()
        )


def test_or_not_where_extra_values(memgraph):
    with pytest.raises(GQLAlchemyExtraKeywordArgumentsInWhere):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(edge_label="TO")
            .node(labels="L2", variable="m")
            .where(item="m.name", operator="=", literal="best_name")
            .or_not_where(item="n.name", operator="=", literal="best_name", expression="Node")
            .return_()
        )


def test_and_where_literal(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator="=", literal="best_name")
        .and_where(item="m.id", operator="<", literal=4)
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = 'best_name' AND m.id < 4 RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_and_not_where_literal(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator="=", literal="best_name")
        .and_not_where(item="m.id", operator="<", literal=4)
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = 'best_name' AND NOT m.id < 4 RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_and_where_property(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator="=", expression="m.name")
        .and_where(item="m.name", operator="=", expression="n.last_name")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = m.name AND m.name = n.last_name RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_and_not_where_property(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator="=", expression="m.name")
        .and_not_where(item="m.name", operator="=", expression="n.last_name")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = m.name AND NOT m.name = n.last_name RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_and_where_label(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n", operator=":", expression="Node")
        .and_where(item="m", operator=":", expression="User")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node AND m:User RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_and_not_where_label(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node("L2", variable="m")
        .where(item="n", operator=":", expression="Node")
        .and_not_where(item="m", operator=":", expression="User")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node AND NOT m:User RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_and_where_literal_and_expression_missing(memgraph):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissingInWhere):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(edge_label="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator="=", literal="my_name")
            .and_where(item="m.name", operator="=")
            .return_()
        )


def test_and_not_where_literal_and_expression_missing(memgraph):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissingInWhere):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(edge_label="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator="=", literal="my_name")
            .and_not_where(item="m.name", operator="=")
            .return_()
        )


def test_and_where_extra_values(memgraph):
    with pytest.raises(GQLAlchemyExtraKeywordArgumentsInWhere):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(edge_label="TO")
            .node(labels="L2", variable="m")
            .where(item="m.name", operator="=", literal="best_name")
            .and_where(item="n.name", operator="=", literal="best_name", expression="Node")
            .return_()
        )


def test_and_not_where_extra_values(memgraph):
    with pytest.raises(GQLAlchemyExtraKeywordArgumentsInWhere):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(edge_label="TO")
            .node(labels="L2", variable="m")
            .where(item="m.name", operator="=", literal="best_name")
            .and_not_where(item="n.name", operator="=", literal="best_name", expression="Node")
            .return_()
        )


def test_xor_where_literal(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator="=", literal="best_name")
        .xor_where(item="m.id", operator="<", literal=4)
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = 'best_name' XOR m.id < 4 RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_xor_not_where_literal(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator="=", literal="best_name")
        .xor_not_where(item="m.id", operator="<", literal=4)
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = 'best_name' XOR NOT m.id < 4 RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_xor_where_property(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator="=", expression="m.name")
        .xor_where(item="m.name", operator="=", expression="n.last_name")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = m.name XOR m.name = n.last_name RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_xor_not_where_property(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator="=", expression="m.name")
        .xor_not_where(item="m.name", operator="=", expression="n.last_name")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = m.name XOR NOT m.name = n.last_name RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_xor_where_label(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n", operator=":", expression="Node")
        .xor_where(item="m", operator=":", expression="User")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node XOR m:User RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_xor_not_where_label(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n", operator=":", expression="Node")
        .xor_not_where(item="m", operator=":", expression="User")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node XOR NOT m:User RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_xor_where_literal_and_expression_missing(memgraph):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissingInWhere):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(edge_label="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator="=", literal="my_name")
            .xor_where(item="m.name", operator="=")
            .return_()
        )


def test_xor_not_where_literal_and_expression_missing(memgraph):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissingInWhere):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(edge_label="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator="=", literal="my_name")
            .xor_not_where(item="m.name", operator="=")
            .return_()
        )


def test_xor_and_where_extra_values(memgraph):
    with pytest.raises(GQLAlchemyExtraKeywordArgumentsInWhere):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(edge_label="TO")
            .node(labels="L2", variable="m")
            .where(item="m.name", operator="=", literal="best_name")
            .xor_where(item="n.name", operator="=", literal="best_name", expression="Node")
            .return_()
        )


def test_xor_not_and_where_extra_values(memgraph):
    with pytest.raises(GQLAlchemyExtraKeywordArgumentsInWhere):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(edge_label="TO")
            .node(labels="L2", variable="m")
            .where(item="m.name", operator="=", literal="best_name")
            .xor_not_where(item="n.name", operator="=", literal="best_name", expression="Node")
            .return_()
        )


def test_and_or_xor_not_where(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(edge_label="TO")
        .node(labels="L2", variable="m")
        .where(item="n", operator=":", expression="Node")
        .and_where(item="n.age", operator=">", literal=5)
        .or_where(item="n", operator=":", expression="Node2")
        .xor_where(item="n.name", operator="=", expression="m.name")
        .xor_not_where(item="m", operator=":", expression="User")
        .or_not_where(item="m", operator=":", expression="Node")
        .and_not_where(item="m.name", operator="=", literal="John")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node AND n.age > 5 OR n:Node2 XOR n.name = m.name XOR NOT m:User OR NOT m:Node AND NOT m.name = 'John' RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_get_single(memgraph):
    query_builder = QueryBuilder().match().node("L1", variable="n").to("TO").node("L2", variable="m").return_("n")
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
        QueryBuilder().match().node("L1", variable="n").to("TO").node("L2", variable="m").return_(("L1", "first"))
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 AS first "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_return_alias_dict(memgraph):
    query_builder = (
        QueryBuilder().match().node("L1", variable="n").to("TO").node("L2", variable="m").return_({"L1": "first"})
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 AS first "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_return_multiple_alias(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node("L1", variable="n")
        .to("TO")
        .node("L2", variable="m")
        .return_([("L1", "first"), "L2", ("L3", "third")])
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 AS first, L2, L3 AS third "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_return_multiple_alias_dict(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node("L1", variable="n")
        .to("TO")
        .node("L2", variable="m")
        .return_({"L1": "first", "L2": "", "L3": "third"})
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 AS first, L2, L3 AS third "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_return_alias_same_as_variable(memgraph):
    query_builder = (
        QueryBuilder().match().node("L1", variable="n").to("TO").node("L2", variable="m").return_(("L1", "L1"))
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_return_alias_same_as_variable_dict(memgraph):
    query_builder = (
        QueryBuilder().match().node("L1", variable="n").to("TO").node("L2", variable="m").return_({"L1": "L1"})
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_return_alias_empty(memgraph):
    query_builder = QueryBuilder().match().node("L1", variable="n").to("TO").node("L2", variable="m").return_("L1")
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_return_alias_empty_dict(memgraph):
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
        .return_([("node", "node"), ("rank", "rank")])
    )
    expected_query = " CALL pagerank.get() YIELD node, rank RETURN node, rank "
    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_call_procedure_node2vec(memgraph):
    query_builder = QueryBuilder().call(procedure="node2vec_online.get_embeddings", arguments="False, 2.0, 0.5")
    expected_query = " CALL node2vec_online.get_embeddings(False, 2.0, 0.5) "
    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_call_procedure_nxalg_betweenness_centrality(memgraph):
    query_builder = (
        QueryBuilder()
        .call(procedure="nxalg.betweenness_centrality", arguments="20, True")
        .yield_()
        .return_(["node", "betweenness"])
    )
    expected_query = " CALL nxalg.betweenness_centrality(20, True) YIELD * RETURN node, betweenness "
    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_yield_multiple_alias(memgraph):
    query_builder = (
        QueryBuilder()
        .call(procedure="nxalg.betweenness_centrality", arguments="20, True")
        .yield_([("node", "n"), "betweenness"])
        .return_(["n", "betweenness"])
    )
    expected_query = " CALL nxalg.betweenness_centrality(20, True) YIELD node AS n, betweenness RETURN n, betweenness "
    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_unwind(memgraph):
    query_builder = (
        QueryBuilder().unwind(list_expression="[1, 2, 3, null]", variable="x").return_([("x", ""), ("'val'", "y")])
    )
    expected_query = " UNWIND [1, 2, 3, null] AS x RETURN x, 'val' AS y "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_remove_label(memgraph):
    query_builder = QueryBuilder().match().node(variable="n", labels=["Node1", "Node2"]).remove({"n:Node2"})
    expected_query = " MATCH (n:Node1:Node2) REMOVE n:Node2 "

    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_remove_property_and_label(memgraph):
    query_builder = QueryBuilder().match().node(variable="n", labels=["Node1", "Node2"]).remove(["n:Node2", "n.name"])
    expected_query = " MATCH (n:Node1:Node2) REMOVE n:Node2, n.name "

    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_order_by(memgraph):
    query_builder = QueryBuilder().match().node(variable="n").return_().order_by(properties="n.id")
    expected_query = " MATCH (n) RETURN * ORDER BY n.id "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_order_by_desc(memgraph):
    query_builder = QueryBuilder().match().node(variable="n").return_().order_by(properties=("n.id", Order.DESC))
    expected_query = " MATCH (n) RETURN * ORDER BY n.id DESC "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_order_by_asc(memgraph):
    query_builder = QueryBuilder().match().node(variable="n").return_().order_by(properties=("n.id", Order.ASC))
    expected_query = " MATCH (n) RETURN * ORDER BY n.id ASC "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_order_by_wrong_ordering(memgraph):
    with pytest.raises(GQLAlchemyMissingOrder):
        QueryBuilder().match().node(variable="n").return_().order_by(properties=("n.id", "DESCE"))


def test_order_by_wrong_type(memgraph):
    with pytest.raises(GQLAlchemyOrderByTypeError):
        QueryBuilder().match().node(variable="n").return_().order_by(properties=1)


def test_order_by_properties(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(variable="n")
        .return_()
        .order_by(properties=[("n.id", Order.DESC), "n.name", ("n.last_name", Order.DESC)])
    )
    expected_query = " MATCH (n) RETURN * ORDER BY n.id DESC, n.name, n.last_name DESC "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_order_by_asc_desc(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(variable="n")
        .return_()
        .order_by(
            properties=[
                ("n.id", Order.ASC),
                "n.name",
                ("n.last_name", Order.DESC),
                ("n.age", Order.ASCENDING),
                ("n.middle_name", Order.DESCENDING),
            ]
        )
    )
    expected_query = (
        " MATCH (n) RETURN * ORDER BY n.id ASC, n.name, n.last_name DESC, n.age ASCENDING, n.middle_name DESCENDING "
    )

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_limit(memgraph):
    query_builder = QueryBuilder().match().node(variable="n").return_().limit("3")
    expected_query = " MATCH (n) RETURN * LIMIT 3 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_skip(memgraph):
    query_builder = QueryBuilder().match().node(variable="n").return_(("n", "")).skip("1")
    expected_query = " MATCH (n) RETURN n SKIP 1 "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_base_class_match(memgraph):
    query_builder = match().node(variable="n").return_("n")
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


def test_base_class_create(memgraph):
    query_builder = create().node(variable="n", labels="TEST", prop="test").return_(results=("n", "n"))
    expected_query = " CREATE (n:TEST {prop: 'test'}) RETURN n "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_base_class_unwind(memgraph):
    query_builder = unwind("[1, 2, 3]", "x").return_(("x", "x"))
    expected_query = " UNWIND [1, 2, 3] AS x RETURN x "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_base_class_with_dict(memgraph):
    query_builder = with_({"10": "n"}).return_({"n": ""})
    expected_query = " WITH 10 AS n RETURN n "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_base_class_with_tuple(memgraph):
    query_builder = with_(("10", "n")).return_(("n", ""))
    expected_query = " WITH 10 AS n RETURN n "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_base_class_load_csv(memgraph):
    query_builder = load_csv("path/to/my/file.csv", True, "row").return_()
    expected_query = " LOAD CSV FROM 'path/to/my/file.csv' WITH HEADER AS row RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_base_class_return(memgraph):
    query_builder = return_(("n", "n"))
    expected_query = " RETURN n "

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


def test_node_instance(memgraph):
    class User(Node):
        name: Optional[str] = Field(index=True, unique=True, db=memgraph)

    user = User(name="Ron").save(memgraph)
    query_builder = QueryBuilder().match().node(node=user, variable="u").return_()
    expected_query = " MATCH (u:User {name: 'Ron'}) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_unsaved_node_instance(memgraph):
    class User(Node):
        name: Optional[str] = Field(index=True, unique=True, db=memgraph)

    user = User(name="Ron")
    query_builder = QueryBuilder().match().node(node=user, variable="u").return_()
    expected_query = " MATCH (u:User {name: 'Ron'}) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_node_relationship_instances(memgraph):
    class User(Node):
        name: Optional[str] = Field(index=True, unique=True, db=memgraph)

    class Follows_test(Relationship, type="FOLLOWS"):
        pass

    user_1 = User(name="Ron").save(memgraph)
    user_2 = User(name="Leslie").save(memgraph)
    follows = Follows_test(_start_node_id=user_1._id, _end_node_id=user_2._id).save(memgraph)
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


def test_unsaved_node_relationship_instances(memgraph):
    class User(Node):
        name: Optional[str] = Field(index=True, unique=True, db=memgraph)

    class Follows_test(Relationship, type="FOLLOWS"):
        pass

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
