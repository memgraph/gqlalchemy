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
from unittest.mock import patch

from gqlalchemy import InvalidMatchChainException, Memgraph, QueryBuilder
from gqlalchemy.query_builders.memgraph_query_builder import (
    Call,
    Create,
    Foreach,
    LoadCsv,
    Match,
    Merge,
    Return,
    Unwind,
    With,
)

from gqlalchemy.graph_algorithms.integrated_algorithms import (
    BreadthFirstSearch,
    DepthFirstSearch,
    WeightedShortestPath,
    AllShortestPath,
)
from gqlalchemy.utilities import CypherVariable, RelationshipDirection


def test_invalid_match_chain_throws_exception():
    with pytest.raises(InvalidMatchChainException):
        QueryBuilder().node(labels=":Label", variable="n").node(labels=":Label", variable="m").return_()


def test_load_csv_with_header(memgraph):
    query_builder = QueryBuilder().load_csv(path="path/to/my/file.csv", header=True, row="row").return_()
    expected_query = " LOAD CSV FROM 'path/to/my/file.csv' WITH HEADER AS row RETURN * "
    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()
    mock.assert_called_with(expected_query)


def test_load_csv_no_header(memgraph):
    query_builder = QueryBuilder().load_csv(path="path/to/my/file.csv", header=False, row="row").return_()
    expected_query = " LOAD CSV FROM 'path/to/my/file.csv' NO HEADER AS row RETURN * "
    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()
    mock.assert_called_with(expected_query)


def test_call_subgraph_with_labels_and_types(memgraph):
    label = "LABEL"
    types = [["TYPE1", "TYPE2"]]
    query_builder = QueryBuilder().call("export_util.json", "/home/user", node_labels=label, relationship_types=types)
    expected_query = ' MATCH p=(a)-[:TYPE1 | :TYPE2]->(b) WHERE (a:LABEL) AND (b:LABEL) WITH project(p) AS graph CALL export_util.json(graph, "/home/user") '
    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()
    mock.assert_called_with(expected_query)


def test_call_subgraph_with_labels(memgraph):
    label = "LABEL"
    query_builder = QueryBuilder().call("export_util.json", "/home/user", node_labels=label)
    expected_query = ' MATCH p=(a)-->(b) WHERE (a:LABEL) AND (b:LABEL) WITH project(p) AS graph CALL export_util.json(graph, "/home/user") '
    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()
    mock.assert_called_with(expected_query)


def test_call_subgraph_with_multiple_labels(memgraph):
    labels = [["LABEL1"], ["LABEL2"]]
    query_builder = QueryBuilder().call(
        "export_util.json", "/home/user", node_labels=labels, relationship_directions=RelationshipDirection.LEFT
    )
    expected_query = ' MATCH p=(a)<--(b) WHERE (a:LABEL1) AND (b:LABEL2) WITH project(p) AS graph CALL export_util.json(graph, "/home/user") '
    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()
    mock.assert_called_with(expected_query)


def test_call_subgraph_with_type(memgraph):
    relationship_type = "TYPE1"
    query_builder = QueryBuilder().call("export_util.json", "/home/user", relationship_types=relationship_type)
    expected_query = ' MATCH p=(a)-[:TYPE1]->(b) WITH project(p) AS graph CALL export_util.json(graph, "/home/user") '
    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()
    mock.assert_called_with(expected_query)


def test_call_subgraph_with_many(memgraph):
    node_labels = [["COMP", "DEVICE"], ["USER"], ["SERVICE", "GATEWAY"]]
    relationship_types = [["OWNER", "RENTEE"], ["USES", "MAKES"]]
    relationship_directions = [RelationshipDirection.LEFT, RelationshipDirection.RIGHT]
    query_builder = QueryBuilder().call(
        "export_util.json",
        "/home/user",
        relationship_types=relationship_types,
        node_labels=node_labels,
        relationship_directions=relationship_directions,
    )
    expected_query = ' MATCH p=(a)<-[:OWNER | :RENTEE]-(b)-[:USES | :MAKES]->(c) WHERE (a:COMP or a:DEVICE) AND (b:USER) AND (c:SERVICE or c:GATEWAY) WITH project(p) AS graph CALL export_util.json(graph, "/home/user") '
    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()
    mock.assert_called_with(expected_query)


@pytest.mark.parametrize(
    "subgraph_path, expected_query",
    [
        (
            "(n:LABEL1)-[:TYPE1]->(m:LABEL2)",
            ' MATCH p=(n:LABEL1)-[:TYPE1]->(m:LABEL2) WITH project(p) AS graph CALL export_util.json(graph, "/home/user") ',
        ),
        (
            "(n:LABEL1)-[:TYPE1 | :TYPE2]->(m:LABEL2)",
            ' MATCH p=(n:LABEL1)-[:TYPE1 | :TYPE2]->(m:LABEL2) WITH project(p) AS graph CALL export_util.json(graph, "/home/user") ',
        ),
    ],
)
def test_call_subgraph_with_query(memgraph, subgraph_path, expected_query):
    query_builder = QueryBuilder().call("export_util.json", "/home/user", subgraph_path=subgraph_path)
    with patch.object(Memgraph, "execute", return_value=None) as mock:
        query_builder.execute()
    mock.assert_called_with(expected_query)


def test_call_procedure_pagerank(memgraph):
    query_builder = (
        QueryBuilder()
        .call(procedure="pagerank.get")
        .yield_(results={"node": "", "rank": ""})
        .return_(results=[("node", "node"), ("rank", "rank")])
    )
    expected_query = " CALL pagerank.get() YIELD node, rank RETURN node, rank "
    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_call_procedure_pagerank_new_yield(memgraph):
    query_builder = QueryBuilder().call(procedure="pagerank.get").yield_(["node", "rank"]).return_(["node", "rank"])
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
        .return_(results=["node", "betweenness"])
    )
    expected_query = " CALL nxalg.betweenness_centrality(20, True) YIELD * RETURN node, betweenness "
    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_yield_multiple_alias(memgraph):
    query_builder = (
        QueryBuilder()
        .call(procedure="nxalg.betweenness_centrality", arguments="20, True")
        .yield_(results=[("node", "n"), "betweenness"])
        .return_(results=["n", "betweenness"])
    )
    expected_query = " CALL nxalg.betweenness_centrality(20, True) YIELD node AS n, betweenness RETURN n, betweenness "
    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_base_class_load_csv(memgraph):
    query_builder = LoadCsv("path/to/my/file.csv", True, "row").return_()
    expected_query = " LOAD CSV FROM 'path/to/my/file.csv' WITH HEADER AS row RETURN * "

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
    expected_query = ' MATCH (:City {name: "Zagreb"})-[:Road *BFS]->(:City {name: "Paris"}) RETURN * '

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_bfs_filter_label():
    bfs_alg = BreadthFirstSearch(condition='r.length <= 200 AND n.name != "Metz"')

    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="City", name="Paris")
        .to(relationship_type="Road", algorithm=bfs_alg)
        .node(labels="City", name="Berlin")
        .return_()
    )

    expected_query = ' MATCH (:City {name: "Paris"})-[:Road *BFS (r, n | r.length <= 200 AND n.name != "Metz")]->(:City {name: "Berlin"}) RETURN * '

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
    expected_query = ' MATCH (:City {name: "Zagreb"})-[:Road *]->(:City {name: "Paris"}) RETURN * '

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_dfs_filter_label():
    dfs_alg = DepthFirstSearch(condition='r.length <= 200 AND n.name != "Metz"')

    query_builder = (
        QueryBuilder()
        .match()
        .node(labels="City", name="Paris")
        .to(relationship_type="Road", algorithm=dfs_alg)
        .node(labels="City", name="Berlin")
        .return_()
    )

    expected_query = ' MATCH (:City {name: "Paris"})-[:Road * (r, n | r.length <= 200 AND n.name != "Metz")]->(:City {name: "Berlin"}) RETURN * '

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


def test_wShortest():
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


def test_allShortest():
    all_shortest = AllShortestPath(weight_property="r.weight")

    query_builder = (
        QueryBuilder()
        .match()
        .node(variable="a", id=723)
        .to(variable="r", directed=False, algorithm=all_shortest)
        .node(variable="b", id=882)
        .return_()
    )

    expected_query = " MATCH (a {id: 723})-[r *ALLSHORTEST (r, n | r.weight) total_weight]-(b {id: 882}) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_allShortest_bound():
    all_shortest = AllShortestPath(upper_bound=10, weight_property="weight")

    query_builder = (
        QueryBuilder()
        .match()
        .node(variable="a", id=723)
        .to(variable="r", directed=False, algorithm=all_shortest)
        .node(variable="b", id=882)
        .return_()
    )

    expected_query = " MATCH (a {id: 723})-[r *ALLSHORTEST 10 (r, n | r.weight) total_weight]-(b {id: 882}) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


def test_allShortest_filter_label():
    all_shortest = AllShortestPath(
        upper_bound=10, weight_property="weight", condition="r.x > 12 AND n.y < 3", total_weight_var="weight_sum"
    )

    query_builder = (
        QueryBuilder()
        .match()
        .node(variable="a", id=723)
        .to(variable="r", directed=False, algorithm=all_shortest)
        .node(variable="b", id=882)
        .return_()
    )

    expected_query = " MATCH (a {id: 723})-[r *ALLSHORTEST 10 (r, n | r.weight) weight_sum (r, n | r.x > 12 AND n.y < 3)]-(b {id: 882}) RETURN * "

    with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
        query_builder.execute()

    mock.assert_called_with(expected_query)


class TestMemgraphBaseClasses:
    def test_base_class_call(self):
        query_builder = Call("pagerank.get").yield_().return_()
        expected_query = " CALL pagerank.get() YIELD * RETURN * "

        with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_base_class_create(self):
        query_builder = Create().node(variable="n", labels="TEST", prop="test").return_(results=("n", "n"))
        expected_query = ' CREATE (n:TEST {prop: "test"}) RETURN n '

        with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_base_class_foreach(self, memgraph):
        update_clause = Create().node(variable="n", id=CypherVariable(name="i"))
        query_builder = Foreach(variable="i", expression="[1, 2, 3]", update_clauses=update_clause.construct_query())
        expected_query = " FOREACH ( i IN [1, 2, 3] | CREATE (n {id: i}) ) "

        with patch.object(Memgraph, "execute", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_base_class_match(self):
        query_builder = Match().node(variable="n").return_(results="n")
        expected_query = " MATCH (n) RETURN n "

        with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_base_merge(self):
        query_builder = (
            QueryBuilder()
            .merge()
            .node(labels="L1", variable="n")
            .to(relationship_type="TO")
            .node(labels="L2")
            .return_()
        )
        expected_query = " MERGE (n:L1)-[:TO]->(:L2) RETURN * "

        with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_simple_merge_with_variables(self):
        query_builder = Merge().node(labels="L1", variable="n").to(relationship_type="TO").node(labels="L2")
        expected_query = " MERGE (n:L1)-[:TO]->(:L2)"

        with patch.object(Memgraph, "execute", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_base_class_unwind(self):
        query_builder = Unwind("[1, 2, 3]", "x").return_(results=("x", "x"))
        expected_query = " UNWIND [1, 2, 3] AS x RETURN x "

        with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_base_class_with_dict(self):
        query_builder = With(results={"10": "n"}).return_(results={"n": ""})
        expected_query = " WITH 10 AS n RETURN n "

        with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_base_class_with_tuple(self):
        query_builder = With(results=("10", "n")).return_(results=("n", ""))
        expected_query = " WITH 10 AS n RETURN n "

        with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_base_class_return(self):
        query_builder = Return(("n", "n"))
        expected_query = " RETURN n "

        with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)
