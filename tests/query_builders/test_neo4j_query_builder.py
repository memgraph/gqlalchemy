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

from gqlalchemy import Neo4j, Neo4jQueryBuilder
from gqlalchemy.query_builders.neo4j_query_builder import (
    Call,
    Create,
    Foreach,
    Match,
    Merge,
    Return,
    Unwind,
    With,
)
from gqlalchemy.utilities import CypherVariable


class TestNeo4jBaseClasses:
    def test_base_class_call(self, neo4j):
        query_builder = Call("pagerank.get", connection=neo4j).yield_().return_()
        expected_query = " CALL pagerank.get() YIELD * RETURN * "

        with patch.object(Neo4j, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_base_class_create(self, neo4j):
        query_builder = (
            Create(connection=neo4j).node(variable="n", labels="TEST", prop="test").return_(results=("n", "n"))
        )
        expected_query = ' CREATE (n:TEST {prop: "test"}) RETURN n '

        with patch.object(Neo4j, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_base_class_foreach(self, neo4j):
        update_clause = Neo4jQueryBuilder(connection=neo4j).create().node(variable="n", id=CypherVariable(name="i"))
        query_builder = Foreach(
            variable="i", expression="[1, 2, 3]", update_clauses=update_clause.construct_query(), connection=neo4j
        )
        expected_query = " FOREACH ( i IN [1, 2, 3] | CREATE (n {id: i}) ) "

        with patch.object(Neo4j, "execute", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_base_class_match(self, neo4j):
        query_builder = Match(connection=neo4j).node(variable="n").return_(results="n")
        expected_query = " MATCH (n) RETURN n "

        with patch.object(Neo4j, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_base_merge(self, neo4j):
        query_builder = (
            Merge(connection=neo4j)
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2")
            .return_()
        )
        expected_query = " MERGE (n:L1)-[:TO]->(:L2) RETURN * "

        with patch.object(Neo4j, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_simple_merge_with_variables(self, neo4j):
        query_builder = (
            Merge(connection=neo4j).node(labels="L1", variable="n").to(relationship_type="TO").node(labels="L2")
        )
        expected_query = " MERGE (n:L1)-[:TO]->(:L2)"

        with patch.object(Neo4j, "execute", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_base_class_unwind(self, neo4j):
        query_builder = Unwind("[1, 2, 3]", "x", connection=neo4j).return_(results=("x", "x"))
        expected_query = " UNWIND [1, 2, 3] AS x RETURN x "

        with patch.object(Neo4j, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_base_class_with_dict(self, neo4j):
        query_builder = With(results={"10": "n"}, connection=neo4j).return_(results={"n": ""})
        expected_query = " WITH 10 AS n RETURN n "

        with patch.object(Neo4j, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_base_class_with_tuple(self, neo4j):
        query_builder = With(results=("10", "n"), connection=neo4j).return_(results=("n", ""))
        expected_query = " WITH 10 AS n RETURN n "

        with patch.object(Neo4j, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_base_class_return(self, neo4j):
        query_builder = Return(("n", "n"), connection=neo4j)
        expected_query = " RETURN n "

        with patch.object(Neo4j, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)
