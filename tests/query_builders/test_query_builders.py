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
from typing import Optional
from unittest.mock import patch
from datetime import datetime

from gqlalchemy.exceptions import (
    GQLAlchemyExtraKeywordArguments,
    GQLAlchemyInstantiationError,
    GQLAlchemyLiteralAndExpressionMissing,
    GQLAlchemyResultQueryTypeError,
    GQLAlchemyTooLargeTupleInResultQuery,
    GQLAlchemyOperatorTypeError,
)
from gqlalchemy import Field, InvalidMatchChainException, Node, QueryBuilder, Relationship
from gqlalchemy.exceptions import GQLAlchemyMissingOrder, GQLAlchemyOrderByTypeError
from gqlalchemy.query_builders.declarative_base import Operator, Order, _ResultPartialQuery
from gqlalchemy.utilities import CypherVariable


@pytest.mark.parametrize("vendor", ["neo4j_query_builder", "memgraph_query_builder"], indirect=True)
class TestMemgraphNeo4jQueryBuilder:
    def test_invalid_match_chain_throws_exception(self, vendor):
        with pytest.raises(InvalidMatchChainException):
            vendor[1].node(labels=":Label", variable="n").node(labels=":Label", variable="m").return_()

    def test_simple_create(self, vendor):
        query_builder = (
            vendor[1].create().node(labels="L1", variable="n").to(relationship_type="TO").node(labels="L2").return_()
        )
        expected_query = " CREATE (n:L1)-[:TO]->(:L2) RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_simple_match(self, vendor):
        query_builder = (
            vendor[1].match().node(labels="L1", variable="n").to(relationship_type="TO").node(labels="L2").return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(:L2) RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_simple_with_multiple_labels(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels=["L1", "L2", "L3"], variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .return_()
        )
        expected_query = " MATCH (n:L1:L2:L3)-[:TO]->(m:L2) RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_multiple_matches(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .match(optional=True)
            .node(variable="n")
            .to(relationship_type="TO")
            .node(labels="L3")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) OPTIONAL MATCH (n)-[:TO]->(:L3) RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_with_empty(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .with_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WITH * "

        with patch.object(vendor[0], "execute", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_with(self, vendor):
        query_builder = vendor[1].match().node(variable="n").with_(results={"n": ""})
        expected_query = " MATCH (n) WITH n "

        with patch.object(vendor[0], "execute", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_with_str_args(self, vendor):
        query_builder = vendor[1].match().node(variable="n").with_(results="n")
        expected_query = " MATCH (n) WITH n "

        with patch.object(vendor[0], "execute", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_union(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(variable="n1", labels="Node1")
            .return_(results="n1")
            .union(include_duplicates=False)
            .match()
            .node(variable="n2", labels="Node2")
            .return_(results="n2")
        )
        expected_query = " MATCH (n1:Node1) RETURN n1 UNION MATCH (n2:Node2) RETURN n2 "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_union_2(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(variable="c", labels="Country")
            .return_(results=("c.name", "columnName"))
            .union(include_duplicates=False)
            .match()
            .node(variable="p", labels="Person")
            .return_(results=("p.name", "columnName"))
        )
        expected_query = (
            " MATCH (c:Country) RETURN c.name AS columnName UNION MATCH (p:Person) RETURN p.name AS columnName "
        )

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_union_all(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(variable="n1", labels="Node1")
            .return_(results="n1")
            .union()
            .match()
            .node(variable="n2", labels="Node2")
            .return_(results="n2")
        )
        expected_query = " MATCH (n1:Node1) RETURN n1 UNION ALL MATCH (n2:Node2) RETURN n2 "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_union_all_2(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(variable="c", labels="Country")
            .return_(results=("c.name", "columnName"))
            .union()
            .match()
            .node(variable="p", labels="Person")
            .return_(results=("p.name", "columnName"))
        )
        expected_query = (
            " MATCH (c:Country) RETURN c.name AS columnName UNION ALL MATCH (p:Person) RETURN p.name AS columnName "
        )

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_delete(self, vendor):
        query_builder = vendor[1].match().node(variable="n1", labels="Node1").delete("n1")
        expected_query = " MATCH (n1:Node1) DELETE n1 "

        with patch.object(vendor[0], "execute", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_delete_list(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(variable="n1", labels="Node1")
            .to()
            .node(variable="n2", labels="Node2")
            .delete(variable_expressions=["n1", "n2"])
        )
        expected_query = " MATCH (n1:Node1)-[]->(n2:Node2) DELETE n1, n2 "

        with patch.object(vendor[0], "execute", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_simple_create_with_variables(self, vendor):
        query_builder = (
            vendor[1]
            .create()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO", variable="e")
            .node(labels="L2", variable="m")
            .return_()
        )
        expected_query = " CREATE (n:L1)-[e:TO]->(m:L2) RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_simple_match_with_variables(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO", variable="e")
            .node(labels="L2", variable="m")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[e:TO]->(m:L2) RETURN * "
        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_delete_detach(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(variable="n1", labels="Node1")
            .to(relationship_type="RELATIONSHIP")
            .node(variable="n2", labels="Node2")
            .delete(["n1", "n2"], True)
        )
        expected_query = " MATCH (n1:Node1)-[:RELATIONSHIP]->(n2:Node2) DETACH DELETE n1, n2 "

        with patch.object(vendor[0], "execute", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_remove_property(self, vendor):
        query_builder = vendor[1].match().node(variable="n", labels="Node").remove(items="n.name")
        expected_query = " MATCH (n:Node) REMOVE n.name "

        with patch.object(vendor[0], "execute", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_multiple_merges(self, vendor):
        query_builder = (
            vendor[1]
            .merge()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .merge()
            .node(variable="n")
            .to(relationship_type="TO")
            .node(labels="L3")
            .return_()
        )
        expected_query = " MERGE (n:L1)-[:TO]->(m:L2) MERGE (n)-[:TO]->(:L3) RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    @pytest.mark.parametrize("operator", ["=", "<>", "<", "!=", ">", "<=", ">=", "=~"])
    def test_where_without_operator_enum(self, vendor, operator):
        query_builder = (
            vendor[1]
            .match()
            .node("L1", variable="n")
            .to("TO")
            .node("L2", variable="m")
            .where(item="n.name", operator=operator, literal="best_name")
            .return_()
        )
        expected_query = f' MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name {operator} "best_name" RETURN * '
        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_where_literal(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, literal="best_name")
            .return_()
        )
        expected_query = ' MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = "best_name" RETURN * '

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_where_property(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, expression="m.name")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = m.name RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_where_not_property(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where_not(item="n.name", operator=Operator.EQUAL, expression="m.name")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE NOT n.name = m.name RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_where_label_without_operator_enum(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n", operator=":", expression="Node")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_where_label_with_rand_string_operator(self, vendor):
        with pytest.raises(GQLAlchemyOperatorTypeError):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where(item="n", operator="heyhey", expression="Node")
                .return_()
            )

    def test_where_label(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n", operator=Operator.LABEL_FILTER, expression="Node")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_where_not_label(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where_not(item="n", operator=Operator.LABEL_FILTER, expression="Node")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE NOT n:Node RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_where_literal_and_expression_missing(self, vendor):
        with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where(item="n.name", operator=Operator.EQUAL)
                .return_()
            )

    def test_where_not_literal_and_expression_missing(self, vendor):
        with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where_not(item="n.name", operator=Operator.EQUAL)
                .return_()
            )

    def test_where_extra_values(self, vendor):
        with pytest.raises(GQLAlchemyExtraKeywordArguments):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where(item="n.name", operator=Operator.EQUAL, literal="best_name", expression="Node")
                .return_()
            )

    def test_where_not_extra_values(self, vendor):
        with pytest.raises(GQLAlchemyExtraKeywordArguments):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where_not(item="n.name", operator=Operator.EQUAL, literal="best_name", expression="Node")
                .return_()
            )

    def test_or_where_literal(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, literal="best_name")
            .or_where(item="m.id", operator=Operator.LESS_THAN, literal=4)
            .return_()
        )
        expected_query = ' MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = "best_name" OR m.id < 4 RETURN * '

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_or_not_where_literal(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, literal="best_name")
            .or_not_where(item="m.id", operator=Operator.LESS_THAN, literal=4)
            .return_()
        )
        expected_query = ' MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = "best_name" OR NOT m.id < 4 RETURN * '

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_or_where_property(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, expression="m.name")
            .or_where(item="m.name", operator=Operator.EQUAL, expression="n.last_name")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = m.name OR m.name = n.last_name RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_or_not_where_property(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, expression="m.name")
            .or_not_where(item="m.name", operator=Operator.EQUAL, expression="n.last_name")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = m.name OR NOT m.name = n.last_name RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_or_where_label(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n", operator=Operator.LABEL_FILTER, expression="Node")
            .or_where(item="m", operator=Operator.LABEL_FILTER, expression="User")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node OR m:User RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_or_not_where_label(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n", operator=Operator.LABEL_FILTER, expression="Node")
            .or_not_where(item="m", operator=Operator.LABEL_FILTER, expression="User")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node OR NOT m:User RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_or_where_literal_and_expression_missing(self, vendor):
        with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where(item="n.name", operator=Operator.EQUAL, literal="my_name")
                .or_where(item="m.name", operator=Operator.EQUAL)
                .return_()
            )

    def test_or_not_where_literal_and_expression_missing(self, vendor):
        with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where(item="n.name", operator=Operator.EQUAL, literal="my_name")
                .or_not_where(item="m.name", operator=Operator.EQUAL)
                .return_()
            )

    def test_or_where_extra_values(self, vendor):
        with pytest.raises(GQLAlchemyExtraKeywordArguments):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where(item="m.name", operator=Operator.EQUAL, literal="best_name")
                .or_where(item="n.name", operator=Operator.EQUAL, literal="best_name", expression="Node")
                .return_()
            )

    def test_or_not_where_extra_values(self, vendor):
        with pytest.raises(GQLAlchemyExtraKeywordArguments):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where(item="m.name", operator=Operator.EQUAL, literal="best_name")
                .or_not_where(item="n.name", operator=Operator.EQUAL, literal="best_name", expression="Node")
                .return_()
            )

    def test_and_where_literal(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, literal="best_name")
            .and_where(item="m.id", operator=Operator.LEQ_THAN, literal=4)
            .return_()
        )
        expected_query = ' MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = "best_name" AND m.id <= 4 RETURN * '

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_and_not_where_literal(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, literal="best_name")
            .and_not_where(item="m.id", operator=Operator.LESS_THAN, literal=4)
            .return_()
        )
        expected_query = ' MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = "best_name" AND NOT m.id < 4 RETURN * '

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_and_where_property(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, expression="m.name")
            .and_where(item="m.name", operator=Operator.EQUAL, expression="n.last_name")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = m.name AND m.name = n.last_name RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_and_not_where_property(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, expression="m.name")
            .and_not_where(item="m.name", operator=Operator.EQUAL, expression="n.last_name")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = m.name AND NOT m.name = n.last_name RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_and_where_label(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n", operator=Operator.LABEL_FILTER, expression="Node")
            .and_where(item="m", operator=Operator.LABEL_FILTER, expression="User")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node AND m:User RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_and_not_where_label(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node("L2", variable="m")
            .where(item="n", operator=Operator.LABEL_FILTER, expression="Node")
            .and_not_where(item="m", operator=Operator.LABEL_FILTER, expression="User")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node AND NOT m:User RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_and_where_literal_and_expression_missing(self, vendor):
        with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where(item="n.name", operator=Operator.EQUAL, literal="my_name")
                .and_where(item="m.name", operator=Operator.EQUAL)
                .return_()
            )

    def test_and_not_where_literal_and_expression_missing(self, vendor):
        with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where(item="n.name", operator=Operator.EQUAL, literal="my_name")
                .and_not_where(item="m.name", operator=Operator.EQUAL)
                .return_()
            )

    def test_and_where_extra_values(self, vendor):
        with pytest.raises(GQLAlchemyExtraKeywordArguments):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where(item="m.name", operator=Operator.EQUAL, literal="best_name")
                .and_where(item="n.name", operator=Operator.EQUAL, literal="best_name", expression="Node")
                .return_()
            )

    def test_and_not_where_extra_values(self, vendor):
        with pytest.raises(GQLAlchemyExtraKeywordArguments):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where(item="m.name", operator=Operator.EQUAL, literal="best_name")
                .and_not_where(item="n.name", operator=Operator.EQUAL, literal="best_name", expression="Node")
                .return_()
            )

    def test_xor_where_literal(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, literal="best_name")
            .xor_where(item="m.id", operator=Operator.LESS_THAN, literal=4)
            .return_()
        )
        expected_query = ' MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = "best_name" XOR m.id < 4 RETURN * '

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_xor_not_where_literal(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, literal="best_name")
            .xor_not_where(item="m.id", operator=Operator.LESS_THAN, literal=4)
            .return_()
        )
        expected_query = ' MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = "best_name" XOR NOT m.id < 4 RETURN * '

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_xor_where_property(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, expression="m.name")
            .xor_where(item="m.name", operator=Operator.EQUAL, expression="n.last_name")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = m.name XOR m.name = n.last_name RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_xor_not_where_property(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n.name", operator=Operator.EQUAL, expression="m.name")
            .xor_not_where(item="m.name", operator=Operator.EQUAL, expression="n.last_name")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = m.name XOR NOT m.name = n.last_name RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_xor_where_label(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n", operator=Operator.LABEL_FILTER, expression="Node")
            .xor_where(item="m", operator=Operator.LABEL_FILTER, expression="User")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node XOR m:User RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_xor_not_where_label(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .where(item="n", operator=Operator.LABEL_FILTER, expression="Node")
            .xor_not_where(item="m", operator=Operator.LABEL_FILTER, expression="User")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node XOR NOT m:User RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_xor_where_literal_and_expression_missing(self, vendor):
        with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where(item="n.name", operator=Operator.EQUAL, literal="my_name")
                .xor_where(item="m.name", operator=Operator.EQUAL)
                .return_()
            )

    def test_xor_not_where_literal_and_expression_missing(self, vendor):
        with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where(item="n.name", operator=Operator.EQUAL, literal="my_name")
                .xor_not_where(item="m.name", operator=Operator.EQUAL)
                .return_()
            )

    def test_xor_and_where_extra_values(self, vendor):
        with pytest.raises(GQLAlchemyExtraKeywordArguments):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where(item="m.name", operator=Operator.EQUAL, literal="best_name")
                .xor_where(item="n.name", operator=Operator.EQUAL, literal="best_name", expression="Node")
                .return_()
            )

    def test_xor_not_and_where_extra_values(self, vendor):
        with pytest.raises(GQLAlchemyExtraKeywordArguments):
            (
                vendor[1]
                .match()
                .node(labels="L1", variable="n")
                .to(relationship_type="TO")
                .node(labels="L2", variable="m")
                .where(item="m.name", operator=Operator.EQUAL, literal="best_name")
                .xor_not_where(item="n.name", operator=Operator.EQUAL, literal="best_name", expression="Node")
                .return_()
            )

    def test_and_or_xor_not_where(self, vendor):
        query_builder = (
            vendor[1]
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
        expected_query = ' MATCH (n:L1)-[:TO]->(m:L2) WHERE n:Node AND n.age > 5 OR n:Node2 XOR n.name = m.name XOR NOT m:User OR NOT m:Node AND NOT m.name = "John" RETURN * '

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_get_single(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .return_(results="n")
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN n "

        with patch.object(vendor[0], "execute_and_fetch", return_value=iter([{"n": None}])) as mock:
            query_builder.get_single(retrieve="n")

        mock.assert_called_with(expected_query)

    def test_return_empty(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .return_()
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_return_alias(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .return_(results=("L1", "first"))
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 AS first "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_return_alias_dict(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .return_(results={"L1": "first"})
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 AS first "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_return_alias_set(self, vendor):
        test_set = set()
        test_set.add(("L1", "first"))
        test_set.add("L2")

        query_builder = vendor[1].return_(results=test_set).construct_query()
        expected_query = [" RETURN L1 AS first, L2 ", " RETURN L2, L1 AS first "]

        assert query_builder in expected_query

    def test_return_alias_set_int(self, vendor):
        test_set = set()
        test_set.add(("L1", 1))
        test_set.add("L2")

        with pytest.raises(GQLAlchemyResultQueryTypeError):
            vendor[1].return_(results=test_set).construct_query()

    def test_return_alias_set_datetime(self, vendor):
        test_set = set()
        test_set.add(("L1", "first"))
        test_set.add(datetime.date)

        with pytest.raises(GQLAlchemyResultQueryTypeError):
            vendor[1].return_(results=test_set).construct_query()

    def test_return_alias_set_too_large_tuple(self, vendor):
        test = ("L1", "first", "L2")

        with pytest.raises(GQLAlchemyTooLargeTupleInResultQuery):
            vendor[1].return_(test).construct_query()

    def test_return_alias_set_multiple(self, vendor):
        test_set = set()
        test_set.add(("L1", "first"))
        test_set.add(("L2", "second"))

        query_builder = vendor[1].return_(results=test_set).construct_query()
        expected_query = [" RETURN L1 AS first, L2 AS second ", " RETURN L2 AS second, L1 AS first "]

        assert query_builder in expected_query

    def test_return_alias_set_multiple_2(self, vendor):
        test_set = set()
        test_set.add(("L1", "first"))
        test_set.add(("L2", "second"))
        test_set.add("L3")

        query_builder = vendor[1].return_(test_set).construct_query()
        expected_query = [
            " RETURN L1 AS first, L2 AS second, L3 ",
            " RETURN L2 AS second, L3, L1 AS first ",
            " RETURN L3, L2 AS second, L1 AS first ",
            " RETURN L1 AS first, L3, L2 AS second ",
            " RETURN L3, L1 AS first, L2 AS second ",
            " RETURN L2 AS second, L1 AS first, L3 ",
        ]

        assert query_builder in expected_query

    def test_return_multiple_alias(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .return_(results=[("L1", "first"), "L2", ("L3", "third")])
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 AS first, L2, L3 AS third "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_return_alias_instantiate(self, vendor):
        with pytest.raises(GQLAlchemyInstantiationError):
            _ResultPartialQuery(keyword="RETURN")

    def test_return_multiple_alias_dict(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .return_(results={"L1": "first", "L2": "", "L3": "third"})
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 AS first, L2, L3 AS third "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_return_alias_same_as_variable(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .return_(results=("L1", "L1"))
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_return_alias_same_as_variable_dict(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .return_(results={"L1": "L1"})
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_return_alias_empty(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .return_(results="L1")
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_return_alias_empty_dict(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2", variable="m")
            .return_(results={"L1": ""})
        )
        expected_query = " MATCH (n:L1)-[:TO]->(m:L2) RETURN L1 "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_unwind(self, vendor):
        query_builder = (
            vendor[1]
            .unwind(list_expression="[1, 2, 3, null]", variable="x")
            .return_(results=[("x", ""), ("'val'", "y")])
        )
        expected_query = " UNWIND [1, 2, 3, null] AS x RETURN x, 'val' AS y "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_remove_label(self, vendor):
        query_builder = vendor[1].match().node(variable="n", labels=["Node1", "Node2"]).remove(items="n:Node2")
        expected_query = " MATCH (n:Node1:Node2) REMOVE n:Node2 "

        with patch.object(vendor[0], "execute", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_remove_property_and_label(self, vendor):
        query_builder = (
            vendor[1].match().node(variable="n", labels=["Node1", "Node2"]).remove(items=["n:Node2", "n.name"])
        )
        expected_query = " MATCH (n:Node1:Node2) REMOVE n:Node2, n.name "

        with patch.object(vendor[0], "execute", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_order_by(self, vendor):
        query_builder = vendor[1].match().node(variable="n").return_().order_by(properties="n.id")
        expected_query = " MATCH (n) RETURN * ORDER BY n.id "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_order_by_desc(self, vendor):
        query_builder = vendor[1].match().node(variable="n").return_().order_by(properties=("n.id", Order.DESC))
        expected_query = " MATCH (n) RETURN * ORDER BY n.id DESC "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_order_by_asc(self, vendor):
        query_builder = vendor[1].match().node(variable="n").return_().order_by(properties=("n.id", Order.ASC))
        expected_query = " MATCH (n) RETURN * ORDER BY n.id ASC "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_order_by_wrong_ordering(self, vendor):
        with pytest.raises(GQLAlchemyMissingOrder):
            vendor[1].match().node(variable="n").return_().order_by(properties=("n.id", "DESCE"))

    def test_order_by_wrong_type(self, vendor):
        with pytest.raises(GQLAlchemyOrderByTypeError):
            vendor[1].match().node(variable="n").return_().order_by(properties=1)

    def test_order_by_properties(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(variable="n")
            .return_()
            .order_by(properties=[("n.id", Order.DESC), "n.name", ("n.last_name", Order.DESC)])
        )
        expected_query = " MATCH (n) RETURN * ORDER BY n.id DESC, n.name, n.last_name DESC "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_order_by_asc_desc(self, vendor):
        query_builder = (
            vendor[1]
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
        expected_query = " MATCH (n) RETURN * ORDER BY n.id ASC, n.name, n.last_name DESC, n.age ASCENDING, n.middle_name DESCENDING "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    @pytest.mark.parametrize("integer_expression", ["3", 3])
    def test_limit(self, vendor, integer_expression):
        query_builder = vendor[1].match().node(variable="n").return_().limit(integer_expression=integer_expression)
        expected_query = f" MATCH (n) RETURN * LIMIT {integer_expression} "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    @pytest.mark.parametrize("integer_expression", ["1", 1])
    def test_skip(self, vendor, integer_expression):
        query_builder = (
            vendor[1].match().node(variable="n").return_(results="n").skip(integer_expression=integer_expression)
        )
        expected_query = f" MATCH (n) RETURN n SKIP {integer_expression} "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()
        mock.assert_called_with(expected_query)

    def test_from(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="L1", variable="n")
            .from_(relationship_type="FROM", variable="e")
            .node(labels="L2", variable="m")
            .return_()
        )
        expected_query = " MATCH (n:L1)<-[e:FROM]-(m:L2) RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_to(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="Town", variable="t")
            .to(relationship_type="BELONGS_TO", variable="b")
            .node(labels="Country", variable="c")
            .return_(results="b")
        )
        expected_query = " MATCH (t:Town)-[b:BELONGS_TO]->(c:Country) RETURN b "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()
        mock.assert_called_with(expected_query)

    def test_add_string_partial(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(labels="Node1", variable="n")
            .to(relationship_type="TO", variable="e")
            .add_custom_cypher("(m:L2) ")
            .return_()
        )
        expected_query = " MATCH (n:Node1)-[e:TO]->(m:L2) RETURN * "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_add_string_complete(self, vendor):
        query_builder = vendor[1].add_custom_cypher("MATCH (n) RETURN n")
        expected_query = "MATCH (n) RETURN n"

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_set_label_without_operator_enum(self, vendor):
        query_builder = vendor[1].set_(item="a", operator=":", expression="L1")
        expected_query = " SET a:L1"

        assert query_builder.construct_query() == expected_query

    def test_set_label_with_rand_operator(self, vendor):
        with pytest.raises(GQLAlchemyOperatorTypeError):
            vendor[1].set_(item="a", operator="heyhey", expression="L1")

    def test_set_label(self, vendor):
        query_builder = vendor[1].set_(item="a", operator=Operator.LABEL_FILTER, expression="L1")
        expected_query = " SET a:L1"

        assert query_builder.construct_query() == expected_query

    @pytest.mark.parametrize("operator", [Operator.ASSIGNMENT, Operator.INCREMENT])
    def test_set_assign_expression(self, vendor, operator):
        query_builder = vendor[1].set_(item="a", operator=operator, expression="value")
        expected_query = f" SET a {operator.value} value"

        assert query_builder.construct_query() == expected_query

    @pytest.mark.parametrize("operator", ["=", "+="])
    def test_set_assign_expression_without_operator_enum(self, vendor, operator):
        query_builder = vendor[1].set_(item="a", operator=operator, expression="value")
        expected_query = f" SET a {operator} value"

        assert query_builder.construct_query() == expected_query

    @pytest.mark.parametrize("operator", [Operator.ASSIGNMENT, Operator.INCREMENT])
    def test_set_assign_literal(self, vendor, operator):
        query_builder = vendor[1].set_(item="a", operator=operator, literal="value")
        expected_query = f' SET a {operator.value} "value"'

        assert query_builder.construct_query() == expected_query

    def test_multiple_set_label(self, vendor):
        query_builder = (
            vendor[1]
            .set_(item="a", operator=Operator.LABEL_FILTER, expression="L1")
            .set_(item="a", operator=Operator.ASSIGNMENT, expression="L2")
        )
        expected_query = " SET a:L1 SET a = L2"

        assert query_builder.construct_query() == expected_query

    @pytest.mark.parametrize("operator", [Operator.ASSIGNMENT, Operator.INCREMENT])
    def test_set_literal_and_expression_missing(self, vendor, operator):
        with pytest.raises(GQLAlchemyLiteralAndExpressionMissing):
            vendor[1].set_(item="n.name", operator=operator)

    @pytest.mark.parametrize("operator", [Operator.ASSIGNMENT, Operator.INCREMENT])
    def test_set_extra_values(self, vendor, operator):
        with pytest.raises(GQLAlchemyExtraKeywordArguments):
            vendor[1].set_(item="n.name", operator=operator, literal="best_name", expression="Node")

    def test_set_docstring_example_1(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(variable="n")
            .where(item="n.name", operator=Operator.EQUAL, literal="Germany")
            .set_(item="n.population", operator=Operator.ASSIGNMENT, literal=83000001)
            .return_()
        )
        expected_query = ' MATCH (n) WHERE n.name = "Germany" SET n.population = 83000001 RETURN * '
        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_set_docstring_example_2(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(variable="n")
            .where(item="n.name", operator=Operator.EQUAL, literal="Germany")
            .set_(item="n.population", operator=Operator.ASSIGNMENT, literal=83000001)
            .set_(item="n.capital", operator=Operator.ASSIGNMENT, literal="Berlin")
            .return_()
        )
        expected_query = (
            ' MATCH (n) WHERE n.name = "Germany" SET n.population = 83000001 SET n.capital = "Berlin" RETURN * '
        )
        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_set_docstring_example_3(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(variable="n")
            .where(item="n.name", operator=Operator.EQUAL, literal="Germany")
            .set_(item="n", operator=Operator.LABEL_FILTER, expression="Land")
            .return_()
        )
        expected_query = ' MATCH (n) WHERE n.name = "Germany" SET n:Land RETURN * '
        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_set_docstring_example_4(self, vendor):
        query_builder = (
            vendor[1]
            .match()
            .node(variable="c", labels="Country")
            .where(item="c.name", operator=Operator.EQUAL, literal="Germany")
            .set_(item="c", operator=Operator.INCREMENT, literal={"name": "Germany", "population": "85000000"})
            .return_()
        )
        expected_query = (
            ' MATCH (c:Country) WHERE c.name = "Germany" SET c += {name: "Germany", population: "85000000"} RETURN * '
        )
        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_node_instance(self, vendor):
        class User(Node):
            name: Optional[str] = Field(unique=True, db=vendor[0])

        user = User(name="Ron").save(vendor[0])
        query_builder = vendor[1].match().node(node=user, variable="u").return_()
        expected_query = ' MATCH (u:User {name: "Ron"}) RETURN * '

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_unsaved_node_instance(self, vendor):
        class User(Node):
            name: Optional[str] = Field(unique=True, db=vendor[0])

        user = User(name="Ron")
        query_builder = vendor[1].match().node(node=user, variable="u").return_()
        expected_query = ' MATCH (u:User {name: "Ron"}) RETURN * '

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_node_relationship_instances(self, vendor):
        class User(Node):
            name: Optional[str] = Field(unique=True, db=vendor[0])

        class Follows_test(Relationship, type="FOLLOWS"):
            pass

        user_1 = User(name="Ron").save(vendor[0])
        user_2 = User(name="Leslie").save(vendor[0])
        follows = Follows_test(_start_node_id=user_1._id, _end_node_id=user_2._id).save(vendor[0])
        query_builder = (
            vendor[1]
            .match()
            .node(node=user_1, variable="user_1")
            .to(relationship=follows)
            .node(node=user_2, variable="user_2")
            .return_()
        )
        expected_query = ' MATCH (user_1:User {name: "Ron"})-[:FOLLOWS]->(user_2:User {name: "Leslie"}) RETURN * '

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_unsaved_node_relationship_instances(self, vendor):
        class User(Node):
            name: Optional[str] = Field(unique=True, db=vendor[0])

        class Follows_test(Relationship, type="FOLLOWS"):
            pass

        user_1 = User(name="Ron")
        user_2 = User(name="Leslie")
        follows = Follows_test()
        query_builder = (
            vendor[1]
            .match()
            .node(node=user_1, variable="user_1")
            .to(relationship=follows)
            .node(node=user_2, variable="user_2")
            .return_()
        )
        expected_query = ' MATCH (user_1:User {name: "Ron"})-[:FOLLOWS]->(user_2:User {name: "Leslie"}) RETURN * '

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_property_variable(self, vendor):
        query = (
            vendor[1]
            .with_(results={"[1,2,3]": "list"})
            .unwind("list", "element")
            .create()
            .node(num=CypherVariable(name="element"))
        )

        expected_query = " WITH [1,2,3] AS list UNWIND list AS element CREATE ( {num: element})"

        with patch.object(vendor[0], "execute", return_value=None) as mock:
            query.execute()

        mock.assert_called_with(expected_query)

    def test_property_variable_edge(self, vendor):
        query = (
            vendor[1]
            .with_(results={"15": "number"})
            .create()
            .node(variable="n")
            .to(relationship_type="REL", num=CypherVariable(name="number"))
            .node(variable="m")
        )

        expected_query = " WITH 15 AS number CREATE (n)-[:REL{num: number}]->(m)"

        with patch.object(vendor[0], "execute", return_value=None) as mock:
            query.execute()

        mock.assert_called_with(expected_query)

    def test_foreach(self, vendor):
        update_clause = QueryBuilder().create().node(variable="n", id=CypherVariable(name="i"))
        query_builder = vendor[1].foreach(
            variable="i", expression="[1, 2, 3]", update_clause=update_clause.construct_query()
        )
        expected_query = " FOREACH ( i IN [1, 2, 3] | CREATE (n {id: i}) ) "

        with patch.object(vendor[0], "execute", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_foreach_multiple_update_clauses(self, vendor):
        variable_li = CypherVariable(name="li")
        update_clause_1 = QueryBuilder().create().node(labels="F4", prop=variable_li)
        update_clause_2 = QueryBuilder().create().node(labels="F5", prop2=variable_li)
        query = (
            vendor[1]
            .match()
            .node(variable="n")
            .foreach(
                variable="li",
                expression="[1, 2]",
                update_clause=[update_clause_1.construct_query(), update_clause_2.construct_query()],
            )
            .return_({"n": ""})
        )
        expected_query = (
            " MATCH (n) FOREACH ( li IN [1, 2] | CREATE (:F4 {prop: li}) CREATE (:F5 {prop2: li}) ) RETURN n "
        )

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query.execute()

        mock.assert_called_with(expected_query)

    def test_foreach_nested(self, vendor):
        create_query = QueryBuilder().create().node(variable="u", prop=CypherVariable(name="j"))
        nested_query = QueryBuilder().foreach(
            variable="j", expression="i", update_clause=create_query.construct_query()
        )
        query = (
            vendor[1]
            .match()
            .node(variable="n")
            .foreach(variable="i", expression="n.prop", update_clause=nested_query.construct_query())
        )

        expected_query = " MATCH (n) FOREACH ( i IN n.prop | FOREACH ( j IN i | CREATE (u {prop: j}) ) ) "

        with patch.object(vendor[0], "execute", return_value=None) as mock:
            query.execute()

        mock.assert_called_with(expected_query)

    def test_merge(self, vendor):
        query_builder = (
            vendor[1]
            .merge()
            .node(variable="city")
            .where(item="city.name", operator="=", literal="London")
            .return_(results="city")
        )
        expected_query = ' MERGE (city) WHERE city.name = "London" RETURN city '

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_create(self, vendor):
        query_builder = vendor[1].create().node(labels="Person", variable="p").return_(results="p")
        expected_query = " CREATE (p:Person) RETURN p "

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_create_with_properties(self, vendor):
        query_builder = vendor[1].create().node(labels="Person", variable="p", first_name="Kate").return_(results="p")
        expected_query = ' CREATE (p:Person {first_name: "Kate"}) RETURN p '

        with patch.object(vendor[0], "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)
