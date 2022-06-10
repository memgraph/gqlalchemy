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

from datetime import datetime
from gqlalchemy.exceptions import (
    GQLAlchemyExtraKeywordArguments,
    GQLAlchemyInstantiationError,
    GQLAlchemyLiteralAndExpressionMissing,
    GQLAlchemyResultQueryTypeError,
    GQLAlchemyTooLargeTupleInResultQuery,
    GQLAlchemyOperatorTypeError,
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
from gqlalchemy.graph_algorithms.integrated_algorithms import BreadthFirstSearch, DepthFirstSearch, WeightedShortestPath
from typing import Optional
from unittest.mock import patch
from gqlalchemy.exceptions import GQLAlchemyMissingOrder, GQLAlchemyOrderByTypeError
from gqlalchemy.query_builder import Operator, Order, _ResultPartialQuery
from gqlalchemy.utilities import PropertyVariable


def test_invalid_match_chain_throws_exception():
    with pytest.raises(InvalidMatchChainException):
        QueryBuilder().node(labels=":Label", variable="n").node(labels=":Label", variable="m").return_()


def test_simple_create(memgraph):
    query_builder = (
        QueryBuilder().create().node(labels="L1", variable="n").to(relationship_type="TO").node(labels="L2").return_()
    )
    expected_query = " CREATE (n:L1)-[:TO]->(:L2) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_simple_match(memgraph):
    query_builder = (
        QueryBuilder().match().node(labels="L1", variable="n").to(relationship_type="TO").node(labels="L2").return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(:L2) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_simple_with_multiple_labels(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels=["L1", "L2", "L3"], variable="n")
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .return_()
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
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .with_()
    )
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
        .to(relationship_type="RELATIONSHIP")
        .node(variable="n2", labels="Node2")
        .delete(["n1", "n2"], True)
    )
    expected_query = " MATCH (n1:Node1)-[:RELATIONSHIP]->(n2:Node2) DETACH DELETE n1, n2 "

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


@pytest.mark.parametrize("operator", ["=", "<>", "<", "!=", ">", "<=", ">="])
def test_where_without_operator_enum(memgraph, operator):
    query_builder = (
        QueryBuilder()
        .match()
        .node("L1", variable="n")
        .to("TO")
        .node("L2", variable="m")
        .where(item="n.name", operator=operator, literal="best_name")
        .return_()
    )
    expected_query = f" MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name {operator} 'best_name' RETURN * "

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
        .where(item="n.name", operator=Operator.EQUAL, literal="best_name")
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
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator=Operator.EQUAL, expression="m.name")
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
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where_not(item="n.name", operator=Operator.EQUAL, expression="m.name")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE NOT n.name = m.name RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_where_label_without_operator_enum(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n", operator=":", expression="Node")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_where_label_with_rand_string_operator(memgraph):
    with pytest.raises(GQLAlchemyOperatorTypeError):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n", operator="heyhey", expression="Node")
            .return_()
        )


def test_where_label(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n", operator=Operator.LABEL_FILTER, expression="Node")
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
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where_not(item="n", operator=Operator.LABEL_FILTER, expression="Node")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE NOT n:Node RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_where_literal_and_expression_missing(memgraph):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL)
            .return_()
        )


def test_where_not_literal_and_expression_missing(memgraph):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where_not(item="n.name", operator=Operator.EQUAL)
            .return_()
        )


def test_where_extra_values(memgraph):
    with pytest.raises(GQLAlchemyExtraKeywordArguments):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, literal="best_name", expression="Node")
            .return_()
        )


def test_where_not_extra_values(memgraph):
    with pytest.raises(GQLAlchemyExtraKeywordArguments):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where_not(item="n.name", operator=Operator.EQUAL, literal="best_name", expression="Node")
            .return_()
        )


def test_or_where_literal(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator=Operator.EQUAL, literal="best_name")
        .or_where(item="m.id", operator=Operator.LESS_THAN, literal=4)
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
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator=Operator.EQUAL, literal="best_name")
        .or_not_where(item="m.id", operator=Operator.LESS_THAN, literal=4)
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
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator=Operator.EQUAL, expression="m.name")
        .or_where(item="m.name", operator=Operator.EQUAL, expression="n.last_name")
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
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator=Operator.EQUAL, expression="m.name")
        .or_not_where(item="m.name", operator=Operator.EQUAL, expression="n.last_name")
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
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n", operator=Operator.LABEL_FILTER, expression="Node")
        .or_where(item="m", operator=Operator.LABEL_FILTER, expression="User")
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
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n", operator=Operator.LABEL_FILTER, expression="Node")
        .or_not_where(item="m", operator=Operator.LABEL_FILTER, expression="User")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node OR NOT m:User RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_or_where_literal_and_expression_missing(memgraph):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, literal="my_name")
            .or_where(item="m.name", operator=Operator.EQUAL)
            .return_()
        )


def test_or_not_where_literal_and_expression_missing(memgraph):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, literal="my_name")
            .or_not_where(item="m.name", operator=Operator.EQUAL)
            .return_()
        )


def test_or_where_extra_values(memgraph):
    with pytest.raises(GQLAlchemyExtraKeywordArguments):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="m.name", operator=Operator.EQUAL, literal="best_name")
            .or_where(item="n.name", operator=Operator.EQUAL, literal="best_name", expression="Node")
            .return_()
        )


def test_or_not_where_extra_values(memgraph):
    with pytest.raises(GQLAlchemyExtraKeywordArguments):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="m.name", operator=Operator.EQUAL, literal="best_name")
            .or_not_where(item="n.name", operator=Operator.EQUAL, literal="best_name", expression="Node")
            .return_()
        )


def test_and_where_literal(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator=Operator.EQUAL, literal="best_name")
        .and_where(item="m.id", operator=Operator.LEQ_THAN, literal=4)
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = 'best_name' AND m.id <= 4 RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_and_not_where_literal(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator=Operator.EQUAL, literal="best_name")
        .and_not_where(item="m.id", operator=Operator.LESS_THAN, literal=4)
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
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator=Operator.EQUAL, expression="m.name")
        .and_where(item="m.name", operator=Operator.EQUAL, expression="n.last_name")
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
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator=Operator.EQUAL, expression="m.name")
        .and_not_where(item="m.name", operator=Operator.EQUAL, expression="n.last_name")
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
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n", operator=Operator.LABEL_FILTER, expression="Node")
        .and_where(item="m", operator=Operator.LABEL_FILTER, expression="User")
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
        .to(relationship_type="TO")
        .node("L2", variable="m")
        .where(item="n", operator=Operator.LABEL_FILTER, expression="Node")
        .and_not_where(item="m", operator=Operator.LABEL_FILTER, expression="User")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node AND NOT m:User RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_and_where_literal_and_expression_missing(memgraph):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, literal="my_name")
            .and_where(item="m.name", operator=Operator.EQUAL)
            .return_()
        )


def test_and_not_where_literal_and_expression_missing(memgraph):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, literal="my_name")
            .and_not_where(item="m.name", operator=Operator.EQUAL)
            .return_()
        )


def test_and_where_extra_values(memgraph):
    with pytest.raises(GQLAlchemyExtraKeywordArguments):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="m.name", operator=Operator.EQUAL, literal="best_name")
            .and_where(item="n.name", operator=Operator.EQUAL, literal="best_name", expression="Node")
            .return_()
        )


def test_and_not_where_extra_values(memgraph):
    with pytest.raises(GQLAlchemyExtraKeywordArguments):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="m.name", operator=Operator.EQUAL, literal="best_name")
            .and_not_where(item="n.name", operator=Operator.EQUAL, literal="best_name", expression="Node")
            .return_()
        )


def test_xor_where_literal(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator=Operator.EQUAL, literal="best_name")
        .xor_where(item="m.id", operator=Operator.LESS_THAN, literal=4)
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
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator=Operator.EQUAL, literal="best_name")
        .xor_not_where(item="m.id", operator=Operator.LESS_THAN, literal=4)
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
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator=Operator.EQUAL, expression="m.name")
        .xor_where(item="m.name", operator=Operator.EQUAL, expression="n.last_name")
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
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n.name", operator=Operator.EQUAL, expression="m.name")
        .xor_not_where(item="m.name", operator=Operator.EQUAL, expression="n.last_name")
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
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n", operator=Operator.LABEL_FILTER, expression="Node")
        .xor_where(item="m", operator=Operator.LABEL_FILTER, expression="User")
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
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n", operator=Operator.LABEL_FILTER, expression="Node")
        .xor_not_where(item="m", operator=Operator.LABEL_FILTER, expression="User")
        .return_()
    )
    expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node XOR NOT m:User RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_xor_where_literal_and_expression_missing(memgraph):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, literal="my_name")
            .xor_where(item="m.name", operator=Operator.EQUAL)
            .return_()
        )


def test_xor_not_where_literal_and_expression_missing(memgraph):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, literal="my_name")
            .xor_not_where(item="m.name", operator=Operator.EQUAL)
            .return_()
        )


def test_xor_and_where_extra_values(memgraph):
    with pytest.raises(GQLAlchemyExtraKeywordArguments):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="m.name", operator=Operator.EQUAL, literal="best_name")
            .xor_where(item="n.name", operator=Operator.EQUAL, literal="best_name", expression="Node")
            .return_()
        )


def test_xor_not_and_where_extra_values(memgraph):
    with pytest.raises(GQLAlchemyExtraKeywordArguments):
        (
            QueryBuilder()
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="m.name", operator=Operator.EQUAL, literal="best_name")
            .xor_not_where(item="n.name", operator=Operator.EQUAL, literal="best_name", expression="Node")
            .return_()
        )


def test_and_or_xor_not_where(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="L1", variable="n")
        .to(relationship_type="TO")
        .node(labels="L2", variable="m")
        .where(item="n", operator=Operator.LABEL_FILTER, expression="Node")
        .and_where(item="n.age", operator=Operator.GREATER_THAN, literal=5)
        .or_where(item="n", operator=Operator.LABEL_FILTER, expression="Node2")
        .xor_where(item="n.name", operator=Operator.EQUAL, expression="m.name")
        .xor_not_where(item="m", operator=Operator.LABEL_FILTER, expression="User")
        .or_not_where(item="m", operator=Operator.LABEL_FILTER, expression="Node")
        .and_not_where(item="m.name", operator=Operator.EQUAL, literal="John")
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


def test_return_alias_set(memgraph):
    test_set = set()
    test_set.add(("L1", "first"))
    test_set.add("L2")

    query_builder = QueryBuilder().return_(test_set).construct_query()
    expected_query = [" RETURN L1 AS first, L2 ", " RETURN L2, L1 AS first "]

    assert query_builder in expected_query


def test_return_alias_set_int(memgraph):
    test_set = set()
    test_set.add(("L1", 1))
    test_set.add("L2")

    with pytest.raises(GQLAlchemyResultQueryTypeError):
        QueryBuilder().return_(test_set).construct_query()


def test_return_alias_set_datetime(memgraph):
    test_set = set()
    test_set.add(("L1", "first"))
    test_set.add(datetime.date)

    with pytest.raises(GQLAlchemyResultQueryTypeError):
        QueryBuilder().return_(test_set).construct_query()


def test_return_alias_set_too_large_tuple(memgraph):
    test = ("L1", "first", "L2")

    with pytest.raises(GQLAlchemyTooLargeTupleInResultQuery):
        QueryBuilder().return_(test).construct_query()


def test_return_alias_set_multiple(memgraph):
    test_set = set()
    test_set.add(("L1", "first"))
    test_set.add(("L2", "second"))

    query_builder = QueryBuilder().return_(test_set).construct_query()
    expected_query = [" RETURN L1 AS first, L2 AS second ", " RETURN L2 AS second, L1 AS first "]

    assert query_builder in expected_query


def test_return_alias_set_multiple_2(memgraph):
    test_set = set()
    test_set.add(("L1", "first"))
    test_set.add(("L2", "second"))
    test_set.add("L3")

    query_builder = QueryBuilder().return_(test_set).construct_query()
    expected_query = [
        " RETURN L1 AS first, L2 AS second, L3 ",
        " RETURN L2 AS second, L3, L1 AS first ",
        " RETURN L3, L2 AS second, L1 AS first ",
        " RETURN L1 AS first, L3, L2 AS second ",
        " RETURN L3, L1 AS first, L2 AS second ",
        " RETURN L2 AS second, L1 AS first, L3 ",
    ]

    assert query_builder in expected_query


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


def test_return_alias_instantiate(memgraph):
    with pytest.raises(GQLAlchemyInstantiationError):
        _ResultPartialQuery(keyword="RETURN")


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


def test_set_label_without_operator_enum(memgraph):
    query_builder = QueryBuilder().set_(item="a", operator=":", expression="L1")
    expected_query = " SET a:L1"

    assert query_builder.construct_query() == expected_query


def test_set_label_with_rand_operator(memgraph):
    with pytest.raises(GQLAlchemyOperatorTypeError):
        QueryBuilder().set_(item="a", operator="heyhey", expression="L1")


def test_set_label(memgraph):
    query_builder = QueryBuilder().set_(item="a", operator=Operator.LABEL_FILTER, expression="L1")
    expected_query = " SET a:L1"

    assert query_builder.construct_query() == expected_query


@pytest.mark.parametrize("operator", [Operator.ASSIGNMENT, Operator.INCREMENT])
def test_set_assign_expression(memgraph, operator):
    query_builder = QueryBuilder().set_(item="a", operator=operator, expression="value")
    expected_query = f" SET a {operator.value} value"

    assert query_builder.construct_query() == expected_query


@pytest.mark.parametrize("operator", ["=", "+="])
def test_set_assign_expression_without_operator_enum(memgraph, operator):
    query_builder = QueryBuilder().set_(item="a", operator=operator, expression="value")
    expected_query = f" SET a {operator} value"

    assert query_builder.construct_query() == expected_query


@pytest.mark.parametrize("operator", [Operator.ASSIGNMENT, Operator.INCREMENT])
def test_set_assign_literal(memgraph, operator):
    query_builder = QueryBuilder().set_(item="a", operator=operator, literal="value")
    expected_query = f" SET a {operator.value} 'value'"

    assert query_builder.construct_query() == expected_query


def test_multiple_set_label(memgraph):
    query_builder = (
        QueryBuilder()
        .set_(item="a", operator=Operator.LABEL_FILTER, expression="L1")
        .set_(item="a", operator=Operator.ASSIGNMENT, expression="L2")
    )
    expected_query = " SET a:L1 SET a = L2"

    assert query_builder.construct_query() == expected_query


@pytest.mark.parametrize("operator", [Operator.ASSIGNMENT, Operator.INCREMENT])
def test_set_literal_and_expression_missing(memgraph, operator):
    with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
        QueryBuilder().set_(item="n.name", operator=operator)


@pytest.mark.parametrize("operator", [Operator.ASSIGNMENT, Operator.INCREMENT])
def test_set_extra_values(memgraph, operator):
    with pytest.raises(GQLAlchemyExtraKeywordArguments):
        QueryBuilder().set_(item="n.name", operator=operator, literal="best_name", expression="Node")


def test_set_docstring_example_1(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(variable="n")
        .where(item="n.name", operator=Operator.EQUAL, literal="Germany")
        .set_(item="n.population", operator=Operator.ASSIGNMENT, literal=83000001)
        .return_()
    )
    expected_query = " MATCH (n) WHERE n.name = 'Germany' SET n.population = 83000001 RETURN * "
    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_set_docstring_example_2(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(variable="n")
        .where(item="n.name", operator=Operator.EQUAL, literal="Germany")
        .set_(item="n.population", operator=Operator.ASSIGNMENT, literal=83000001)
        .set_(item="n.capital", operator=Operator.ASSIGNMENT, literal="Berlin")
        .return_()
    )
    expected_query = (
        " MATCH (n) WHERE n.name = 'Germany' SET n.population = 83000001 SET n.capital = 'Berlin' RETURN * "
    )
    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_set_docstring_example_3(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(variable="n")
        .where(item="n.name", operator=Operator.EQUAL, literal="Germany")
        .set_(item="n", operator=Operator.LABEL_FILTER, expression="Land")
        .return_()
    )
    expected_query = " MATCH (n) WHERE n.name = 'Germany' SET n:Land RETURN * "
    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_set_docstring_example_4(memgraph):
    query_builder = (
        QueryBuilder()
        .match()
        .node(variable="c", labels="Country")
        .where(item="c.name", operator=Operator.EQUAL, literal="Germany")
        .set_(item="c", operator=Operator.INCREMENT, literal={"name": "Germany", "population": "85000000"})
        .return_()
    )
    expected_query = (
        " MATCH (c:Country) WHERE c.name = 'Germany' SET c += {name: 'Germany', population: '85000000'} RETURN * "
    )
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


def test_bfs():
    bfs_alg = BreadthFirstSearch()

    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="City", name="Zagreb")
        .to(relationship_type="Road", algorithm=bfs_alg)
        .node(labels="City", name="Paris")
        .return_()
    )
    expected_query = " MATCH (:City {name: 'Zagreb'})-[:Road *BFS]->(:City {name: 'Paris'}) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_bfs_filter_label():
    bfs_alg = BreadthFirstSearch(condition="r.length <= 200 AND n.name != 'Metz'")

    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="City", name="Paris")
        .to(relationship_type="Road", algorithm=bfs_alg)
        .node(labels="City", name="Berlin")
        .return_()
    )

    expected_query = " MATCH (:City {name: 'Paris'})-[:Road *BFS (r, n | r.length <= 200 AND n.name != 'Metz')]->(:City {name: 'Berlin'}) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


@pytest.mark.parametrize(
    "lower_bound, upper_bound, expected_query",
    [
        (1, 15, " MATCH (a {id: 723})-[ *BFS 1..15 (r, n | r.x > 12 AND n.y < 3)]-() RETURN * "),
        (3, None, " MATCH (a {id: 723})-[ *BFS 3.. (r, n | r.x > 12 AND n.y < 3)]-() RETURN * "),
        (None, 10, " MATCH (a {id: 723})-[ *BFS ..10 (r, n | r.x > 12 AND n.y < 3)]-() RETURN * "),
        (None, None, " MATCH (a {id: 723})-[ *BFS (r, n | r.x > 12 AND n.y < 3)]-() RETURN * "),
    ],
)
def test_bfs_bounds(lower_bound, upper_bound, expected_query):
    bfs_alg = BreadthFirstSearch(lower_bound=lower_bound, upper_bound=upper_bound, condition="r.x > 12 AND n.y < 3")

    query_builder = (
        QueryBuilder().match().node(variable="a", id=723).to(directed=False, algorithm=bfs_alg).node().return_()
    )

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_dfs():
    dfs_alg = DepthFirstSearch()

    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="City", name="Zagreb")
        .to(relationship_type="Road", algorithm=dfs_alg)
        .node(labels="City", name="Paris")
        .return_()
    )
    expected_query = " MATCH (:City {name: 'Zagreb'})-[:Road *]->(:City {name: 'Paris'}) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_dfs_filter_label():
    dfs_alg = DepthFirstSearch(condition="r.length <= 200 AND n.name != 'Metz'")

    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="City", name="Paris")
        .to(relationship_type="Road", algorithm=dfs_alg)
        .node(labels="City", name="Berlin")
        .return_()
    )

    expected_query = " MATCH (:City {name: 'Paris'})-[:Road * (r, n | r.length <= 200 AND n.name != 'Metz')]->(:City {name: 'Berlin'}) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


@pytest.mark.parametrize(
    "lower_bound, upper_bound, expected_query",
    [
        (1, 15, " MATCH (a {id: 723})-[ * 1..15 (r, n | r.x > 12 AND n.y < 3)]-() RETURN * "),
        (3, None, " MATCH (a {id: 723})-[ * 3.. (r, n | r.x > 12 AND n.y < 3)]-() RETURN * "),
        (None, 10, " MATCH (a {id: 723})-[ * ..10 (r, n | r.x > 12 AND n.y < 3)]-() RETURN * "),
        (None, None, " MATCH (a {id: 723})-[ * (r, n | r.x > 12 AND n.y < 3)]-() RETURN * "),
    ],
)
def test_dfs_bounds(lower_bound, upper_bound, expected_query):
    dfs_alg = DepthFirstSearch(lower_bound=lower_bound, upper_bound=upper_bound, condition="r.x > 12 AND n.y < 3")

    query_builder = (
        QueryBuilder().match().node(variable="a", id=723).to(directed=False, algorithm=dfs_alg).node().return_()
    )

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_wshortest():
    weighted_shortest = WeightedShortestPath(weight_property="r.weight")

    query_builder = (
        QueryBuilder()
        .match()
        .node(variable="a", id=723)
        .to(variable="r", directed=False, algorithm=weighted_shortest)
        .node(variable="b", id=882)
        .return_()
    )

    expected_query = " MATCH (a {id: 723})-[r *WSHORTEST (r, n | r.weight) total_weight]-(b {id: 882}) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_wShortest_bound():
    weighted_shortest = WeightedShortestPath(upper_bound=10, weight_property="weight")

    query_builder = (
        QueryBuilder()
        .match()
        .node(variable="a", id=723)
        .to(variable="r", directed=False, algorithm=weighted_shortest)
        .node(variable="b", id=882)
        .return_()
    )

    expected_query = " MATCH (a {id: 723})-[r *WSHORTEST 10 (r, n | r.weight) total_weight]-(b {id: 882}) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_wShortest_filter_label():
    weighted_shortest = WeightedShortestPath(
        upper_bound=10, weight_property="weight", condition="r.x > 12 AND n.y < 3", total_weight_var="weight_sum"
    )

    query_builder = (
        QueryBuilder()
        .match()
        .node(variable="a", id=723)
        .to(variable="r", directed=False, algorithm=weighted_shortest)
        .node(variable="b", id=882)
        .return_()
    )

    expected_query = " MATCH (a {id: 723})-[r *WSHORTEST 10 (r, n | r.weight) weight_sum (r, n | r.x > 12 AND n.y < 3)]-(b {id: 882}) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_property_variable():
    query = (
        QueryBuilder()
        .with_({"[1,2,3]": "list"})
        .unwind("list", "element")
        .create()
        .node(num=PropertyVariable(name="element"))
    )

    expected_query = " WITH [1,2,3] AS list UNWIND list AS element CREATE ( {num: element})"

    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query.execute()

    mock.assert_called_with(expected_query)


def test_property_variable_edge():
    query = (
        QueryBuilder()
        .with_({"15": "number"})
        .create()
        .node(variable="n")
        .to(relationship_type="REL", num=PropertyVariable(name="number"))
        .node(variable="m")
    )

    expected_query = " WITH 15 AS number CREATE (n)-[:REL{num: number}]->(m)"

    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query.execute()

    mock.assert_called_with(expected_query)
