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

import networkx as nx

from gqlalchemy.transformations.translators.nx_translator import (
    NxTranslator,
    NoNetworkXConfigException,
    NetworkXCypherBuilder,
)
from gqlalchemy.transformations.translators.translator import Translator
from gqlalchemy.models import Node, Relationship
from gqlalchemy.transformations.constants import LABEL, EDGE_TYPE, DEFAULT_NODE_LABEL, DEFAULT_EDGE_TYPE
from gqlalchemy.utilities import NetworkXCypherConfig
from tests.transformations.common import execute_queries


def _check_entity_exists_in_nx(graph_data, entity_properties, expected_num_features):
    """Checks that entity with `entity_properties` exists in the Nx graph.
    Args:
        graph_data: NX node info or edge info.
        entity_properties: Entity's Memgraph properties.
        expected_num_features: Expected number of properties.
    """
    # print(f"Entity properties: {entity_properties}")
    for *_, properties in graph_data:
        # print(f"Graph properties: {properties}")
        if properties == entity_properties and len(properties.keys()) == expected_num_features:
            return True
    return False


def _check_nx_graph_structure(
    graph: nx.Graph, translator: NxTranslator, node_expected_num_features, edge_expected_num_features
):
    # Test all edges
    query_results = translator.get_all_edges_from_db()
    for row in query_results:
        row_values = row.values()
        for entity in row_values:
            entity_properties = entity._properties
            if isinstance(entity, Node):
                entity_properties[LABEL] = Translator.merge_labels(entity._labels, DEFAULT_NODE_LABEL)
                assert _check_entity_exists_in_nx(graph.nodes(data=True), entity_properties, node_expected_num_features)
            elif isinstance(entity, Relationship):
                entity_properties[EDGE_TYPE] = entity._type if entity._type else DEFAULT_EDGE_TYPE
                assert _check_entity_exists_in_nx(graph.edges(data=True), entity_properties, edge_expected_num_features)

    # Test isolated nodes if any
    isolated_nodes_results = translator.get_all_isolated_nodes_from_db()
    for isolated_node in isolated_nodes_results:
        isolated_node = isolated_node["n"]  #
        entity_properties = isolated_node._properties
        entity_properties[LABEL] = Translator.merge_labels(isolated_node._labels, DEFAULT_NODE_LABEL)
        assert _check_entity_exists_in_nx(graph.nodes(data=True), entity_properties, node_expected_num_features)


def test_export_simple_graph(memgraph):
    queries = []
    queries.append(f"CREATE (m:Node {{id: 1}})")
    queries.append(f"CREATE (m:Node {{id: 2}})")
    queries.append(f"CREATE (m:Node {{id: 3}})")
    queries.append(f"CREATE (m:Node {{id: 4}})")
    queries.append(f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 1}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 2}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 3}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 4}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 5}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 6}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 7}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 8}}]->(m)")
    execute_queries(memgraph, queries)
    # Translate to DGL graph
    translator = NxTranslator()
    graph = translator.get_instance()
    assert graph.number_of_edges() == 8
    assert graph.number_of_nodes() == 4
    _check_nx_graph_structure(graph, translator, 2, 2)
    memgraph.drop_database()


def test_export_simple_graph_isolated_nodes(memgraph):
    queries = []
    queries.append(f"CREATE (m:Node {{id: 1}})")
    queries.append(f"CREATE (m:Node {{id: 2}})")
    queries.append(f"CREATE (m:Node {{id: 3}})")
    queries.append(f"CREATE (m:Node {{id: 4}})")
    queries.append(f"CREATE (m:Node {{id: 5}})")  # isolated node
    queries.append(f"CREATE (m:Node {{id: 6}})")  # isolated node
    queries.append(f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 1}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 2}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 3}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 4}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 5}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 6}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 7}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 8}}]->(m)")
    execute_queries(memgraph, queries)
    # Translate to DGL graph
    translator = NxTranslator()
    graph = translator.get_instance()
    assert graph.number_of_edges() == 8
    assert graph.number_of_nodes() == 6
    _check_nx_graph_structure(graph, translator, 2, 2)


def test_nx_export_graph_no_features_no_labels(memgraph):
    """Export graph which has all nodes and edges without properties."""
    # Prepare queries
    queries = []
    queries.append(f"CREATE (m {{id: 1}})")
    queries.append(f"CREATE (m {{id: 2}})")
    queries.append(f"CREATE (m {{id: 3}})")
    queries.append(f"CREATE (m {{id: 4}})")
    queries.append(f"MATCH (n {{id: 1}}), (m {{id: 2}}) CREATE (n)-[r:CONNECTION]->(m)")
    queries.append(f"MATCH (n {{id: 2}}), (m {{id: 3}}) CREATE (n)-[r:CONNECTION]->(m)")
    queries.append(f"MATCH (n {{id: 3}}), (m {{id: 4}}) CREATE (n)-[r:CONNECTION]->(m)")
    queries.append(f"MATCH (n {{id: 4}}), (m {{id: 1}}) CREATE (n)-[r:CONNECTION]->(m)")
    queries.append(f"MATCH (n {{id: 1}}), (m {{id: 3}}) CREATE (n)-[r:CONNECTION]->(m)")
    queries.append(f"MATCH (n {{id: 2}}), (m {{id: 4}}) CREATE (n)-[r:CONNECTION]->(m)")
    queries.append(f"MATCH (n {{id: 4}}), (m {{id: 2}}) CREATE (n)-[r:CONNECTION]->(m)")
    queries.append(f"MATCH (n {{id: 3}}), (m {{id: 1}}) CREATE (n)-[r:CONNECTION]->(m)")
    queries.append(f"MATCH (n) REMOVE n.id")
    execute_queries(memgraph, queries)
    # Translate to nx graph
    translator = NxTranslator()
    graph = translator.get_instance()
    assert graph.number_of_edges() == 8
    assert graph.number_of_nodes() == 4
    _check_nx_graph_structure(graph, translator, 1, 1)
    # Test some simple metadata properties


def test_nx_export_multiple_labels(memgraph):
    """Tests exporting to nx when using multiple labels for nodes."""
    # Prepare queries
    queries = []
    queries.append(f"CREATE (m:Node:Mode {{id: 1}})")
    queries.append(f"CREATE (m:Node:Mode {{id: 2}})")
    queries.append(f"CREATE (m:Node {{id: 3}})")
    queries.append(f"CREATE (m:Node {{id: 4}})")
    queries.append(
        f"MATCH (n:Node:Mode {{id: 1}}), (m:Node:Mode {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 1}}]->(m)"
    )
    queries.append(f"MATCH (n:Node:Mode {{id: 2}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 2}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 3}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 4}}), (m:Node:Mode {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 4}}]->(m)")
    queries.append(f"MATCH (n:Node:Mode {{id: 1}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 5}}]->(m)")
    queries.append(f"MATCH (n:Node:Mode {{id: 2}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 6}}]->(m)")
    execute_queries(memgraph, queries)
    translator = NxTranslator()
    graph = translator.get_instance()
    assert graph.number_of_edges() == 6
    assert graph.number_of_nodes() == 4
    _check_nx_graph_structure(graph, translator, 2, 2)


def test_nx_export_many_numerical_properties(memgraph):
    """Test graph that has several numerical features on nodes and edges."""
    # Prepare queries
    queries = []
    queries.append(f"CREATE (m:Node {{id: 1, num: 80, edem: 30}})")
    queries.append(f"CREATE (m:Node {{id: 2, num: 91, edem: 32}})")
    queries.append(f"CREATE (m:Node {{id: 3, num: 100, edem: 34}})")
    queries.append(f"CREATE (m:Node {{id: 4, num: 12, edem: 34}})")
    queries.append(
        f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 1, edge_num: 99, edge_edem: 12}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 2, edge_num: 99, edge_edem: 12}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 3, edge_num: 99, edge_edem: 12}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 4, edge_num: 99, edge_edem: 12}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 5, edge_num: 99, edge_edem: 12}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 6, edge_num: 99, edge_edem: 12}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 7, edge_num: 99, edge_edem: 12}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 8, edge_num: 99, edge_edem: 12}}]->(m)"
    )
    execute_queries(memgraph, queries)
    translator = NxTranslator()
    graph = translator.get_instance()
    assert graph.number_of_edges() == 8
    assert graph.number_of_nodes() == 4
    _check_nx_graph_structure(graph, translator, 4, 4)


def test_nx_export_list_properties(memgraph):
    """Test graph that has several numerical features on all nodes and edges together with lists that could represent feature vectors."""
    # Prepare queries
    queries = []
    queries.append(f"CREATE (m:Node {{id: 1, num: 80, edem: 30, lst: [2, 3, 3, 2]}})")
    queries.append(f"CREATE (m:Node {{id: 2, num: 91, edem: 32, lst: [2, 2, 3, 3]}})")
    queries.append(f"CREATE (m:Node {{id: 3, num: 100, edem: 34, lst: [3, 2, 2, 3]}})")
    queries.append(f"CREATE (m:Node {{id: 4, num: 12, edem: 34, lst: [2, 2, 2, 3]}})")
    queries.append(
        f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 1, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 2, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 3, edge_num: 99, edge_edem: 12, edge_lst: [1, 0, 1, 0]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 4, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 5, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 6, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 7, edge_num: 99, edge_edem: 12, edge_lst: [1, 1, 0, 0]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 8, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    execute_queries(memgraph, queries)
    translator = NxTranslator()
    graph = translator.get_instance()
    assert graph.number_of_edges() == 8
    assert graph.number_of_nodes() == 4
    _check_nx_graph_structure(graph, translator, 5, 5)


def test_nx_export_various_dimensionality_list_properties(memgraph):
    """When lists have various dimensions, they should get translated in the same way as when for all nodes are of the same dimension."""
    # Prepare queries
    queries = []
    queries.append(f"CREATE (m:Node {{id: 1, num: 80, edem: 30, lst: [2, 3, 3, 2]}})")
    queries.append(f"CREATE (m:Node {{id: 2, num: 91, edem: 32, lst: [2, 2, 3, 3]}})")
    queries.append(f"CREATE (m:Node {{id: 3, num: 100, edem: 34, lst: [3, 2, 2, 3, 4, 4]}})")
    queries.append(f"CREATE (m:Node {{id: 4, num: 12, edem: 34, lst: [2, 2, 2, 3, 5, 5]}})")
    queries.append(
        f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 1, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1, 0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 2, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 3, edge_num: 99, edge_edem: 12, edge_lst: [1, 0, 1, 0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 4, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 5, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 6, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1, 0, 0]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 7, edge_num: 99, edge_edem: 12, edge_lst: [1, 1, 0, 0, 1, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 8, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    execute_queries(memgraph, queries)
    translator = NxTranslator()
    graph = translator.get_instance()
    assert graph.number_of_edges() == 8
    assert graph.number_of_nodes() == 4
    _check_nx_graph_structure(graph, translator, 5, 5)


def test_nx_export_non_numeric_properties(memgraph):
    """Test graph which has some non-numeric properties. Non-numeric properties should be translated in the same way as those numeric."""
    # Prepare queries
    queries = []
    queries.append(f"CREATE (m:Node {{id: 1, num: 80, edem: 'one', lst: [2, 3, 3, 2]}})")
    queries.append(f"CREATE (m:Node {{id: 2, num: 91, edem: 'two', lst: [2, 2, 3, 3]}})")
    queries.append(f"CREATE (m:Node {{id: 3, num: 100, edem: 'three', lst: [3, 2, 2, 3]}})")
    queries.append(f"CREATE (m:Node {{id: 4, num: 12, edem: 'fourth', lst: [2, 2, 2, 3]}})")
    queries.append(
        f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 1, edge_num: 99, edge_edem: 'hi', edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 2, edge_num: 99, edge_edem: 'hu', edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 3, edge_num: 99, edge_edem: 'ho', edge_lst: [1, 0, 1, 0]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 4, edge_num: 99, edge_edem: 'la', edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 5, edge_num: 99, edge_edem: 'le', edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 6, edge_num: 99, edge_edem: 'do', edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 7, edge_num: 99, edge_edem: 're', edge_lst: [1, 1, 0, 0]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 8, edge_num: 99, edge_edem: 'mi', edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    execute_queries(memgraph, queries)
    translator = NxTranslator()
    graph = translator.get_instance()
    assert graph.number_of_edges() == 8
    assert graph.number_of_nodes() == 4
    _check_nx_graph_structure(graph, translator, 5, 5)


def test_nx_create_nodes():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2])
    expected_cypher_queries = [
        "CREATE ( {id: 1});",
        "CREATE ( {id: 2});",
    ]
    translator = NxTranslator()

    actual_cypher_queries = list(translator.to_cypher_queries(graph))

    assert actual_cypher_queries == expected_cypher_queries


def test_nx_create_nodes_with_string():
    graph = nx.Graph()
    graph.add_nodes_from(
        [
            (1, {"id": "id1"}),
            (2, {"id": "id2"}),
        ]
    )
    expected_cypher_queries = [
        'CREATE ( {id: "id1"});',
        'CREATE ( {id: "id2"});',
    ]

    translator = NxTranslator()

    actual_cypher_queries = list(translator.to_cypher_queries(graph))

    assert actual_cypher_queries == expected_cypher_queries


def test_nx_create_nodes_with_properties():
    graph = nx.Graph()
    graph.add_nodes_from(
        [
            (1, {"color": "blue", "labels": "L1"}),
            (2, {"age": 32}),
            (3, {"data": [1, 2, 3], "labels": ["L1", "L2", "L3"]}),
        ]
    )
    expected_cypher_queries = [
        'CREATE (:L1 {color: "blue", id: 1});',
        "CREATE ( {age: 32, id: 2});",
        "CREATE (:L1:L2:L3 {data: [1, 2, 3], id: 3});",
    ]

    translator = NxTranslator()
    actual_cypher_queries = list(translator.to_cypher_queries(graph))

    assert actual_cypher_queries == expected_cypher_queries


def test_nx_create_edges():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3])
    graph.add_edges_from([(1, 2), (2, 3)])
    expected_cypher_queries = [
        "CREATE ( {id: 1});",
        "CREATE ( {id: 2});",
        "CREATE ( {id: 3});",
        "MATCH (n {id: 1}), (m {id: 2}) CREATE (n)-[:TO ]->(m);",
        "MATCH (n {id: 2}), (m {id: 3}) CREATE (n)-[:TO ]->(m);",
    ]

    translator = NxTranslator()

    actual_cypher_queries = list(translator.to_cypher_queries(graph))

    assert actual_cypher_queries == expected_cypher_queries


def test_nx_create_edges_with_string_ids():
    graph = nx.Graph()
    graph.add_nodes_from(
        [
            (1, {"id": "id1"}),
            (2, {"id": "id2"}),
            (3, {"id": "id3"}),
        ]
    )
    graph.add_edges_from([(1, 2), (2, 3)])
    expected_cypher_queries = [
        'CREATE ( {id: "id1"});',
        'CREATE ( {id: "id2"});',
        'CREATE ( {id: "id3"});',
        'MATCH (n {id: "id1"}), (m {id: "id2"}) CREATE (n)-[:TO ]->(m);',
        'MATCH (n {id: "id2"}), (m {id: "id3"}) CREATE (n)-[:TO ]->(m);',
    ]

    translator = NxTranslator()
    actual_cypher_queries = list(translator.to_cypher_queries(graph))

    assert actual_cypher_queries == expected_cypher_queries


def test_nx_create_edges_with_properties():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3])
    graph.add_edges_from([(1, 2, {"type": "TYPE1"}), (2, 3, {"type": "TYPE2", "data": "abc"})])
    expected_cypher_queries = [
        "CREATE ( {id: 1});",
        "CREATE ( {id: 2});",
        "CREATE ( {id: 3});",
        "MATCH (n {id: 1}), (m {id: 2}) CREATE (n)-[:TYPE1 ]->(m);",
        'MATCH (n {id: 2}), (m {id: 3}) CREATE (n)-[:TYPE2 {data: "abc"}]->(m);',
    ]

    translator = NxTranslator()
    actual_cypher_queries = list(translator.to_cypher_queries(graph))

    assert actual_cypher_queries == expected_cypher_queries


def test_nx_create_edge_and_node_with_properties():
    graph = nx.Graph()
    graph.add_nodes_from(
        [(1, {"labels": "Label1"}), (2, {"labels": ["Label1", "Label2"], "name": "name1"}), (3, {"labels": "Label1"})]
    )
    graph.add_edges_from([(1, 2, {"type": "TYPE1"}), (2, 3, {"type": "TYPE2", "data": "abc"})])
    expected_cypher_queries = [
        "CREATE (:Label1 {id: 1});",
        'CREATE (:Label1:Label2 {name: "name1", id: 2});',
        "CREATE (:Label1 {id: 3});",
        "MATCH (n:Label1 {id: 1}), (m:Label1:Label2 {id: 2}) CREATE (n)-[:TYPE1 ]->(m);",
        'MATCH (n:Label1:Label2 {id: 2}), (m:Label1 {id: 3}) CREATE (n)-[:TYPE2 {data: "abc"}]->(m);',
    ]

    translator = NxTranslator()

    actual_cypher_queries = list(translator.to_cypher_queries(graph))

    assert actual_cypher_queries == expected_cypher_queries


def test_nx_create_edge_and_node_with_index():
    graph = nx.Graph()
    graph.add_nodes_from(
        [(1, {"labels": "Label1"}), (2, {"labels": ["Label1", "Label2"], "name": "name1"}), (3, {"labels": "Label1"})]
    )
    graph.add_edges_from([(1, 2, {"type": "TYPE1"}), (2, 3, {"type": "TYPE2", "data": "abc"})])
    expected_cypher_queries = [
        "CREATE (:Label1 {id: 1});",
        'CREATE (:Label1:Label2 {name: "name1", id: 2});',
        "CREATE (:Label1 {id: 3});",
        "CREATE INDEX ON :Label2(id);",
        "CREATE INDEX ON :Label1(id);",
        "MATCH (n:Label1 {id: 1}), (m:Label1:Label2 {id: 2}) CREATE (n)-[:TYPE1 ]->(m);",
        'MATCH (n:Label1:Label2 {id: 2}), (m:Label1 {id: 3}) CREATE (n)-[:TYPE2 {data: "abc"}]->(m);',
    ]

    translator = NxTranslator()
    actual_cypher_queries = list(translator.to_cypher_queries(graph, NetworkXCypherConfig(create_index=True)))

    assert actual_cypher_queries[0:3] == expected_cypher_queries[0:3]
    assert set(actual_cypher_queries[3:5]) == set(expected_cypher_queries[3:5])
    assert actual_cypher_queries[5:7] == expected_cypher_queries[5:7]


def test_creating_builder_with_no_config_throws_exception():
    with pytest.raises(NoNetworkXConfigException):
        NetworkXCypherBuilder(None)
