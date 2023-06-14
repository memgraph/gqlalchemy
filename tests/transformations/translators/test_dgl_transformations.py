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

from numbers import Number
import pytest
from typing import Dict, Any, Set

import numpy as np


from gqlalchemy import Match
from gqlalchemy.models import Node, Relationship

from gqlalchemy.transformations.translators.translator import Translator
from gqlalchemy.transformations.constants import DGL_ID, DEFAULT_NODE_LABEL, DEFAULT_EDGE_TYPE
from gqlalchemy.utilities import to_cypher_value
from tests.transformations.common import execute_queries

dgl = pytest.importorskip("dgl")
TUDataset = pytest.importorskip("dgl.data.TUDataset")
torch = pytest.importorskip("torch")
DGLTranslator = pytest.importorskip("gqlalchemy.transformations.translators.dgl_translator.DGLTranslator")

pytestmark = [pytest.mark.extras, pytest.mark.dgl]

##########
# UTILS
##########


def _check_entity_exists_in_dgl(entity_data, properties: Dict[str, Any], translated_properties: Set[str] = {}):
    """Checks whether the node with `node label` and `node_properties` exists in the DGL.
    Args:
        entity_data: `graph.nodes[node_label]` or `graph.edges[etype]`
        properties: Entity's properties from the Memgraph.
        translated_properties: Properties that are translated from Memgraph to DGL.
    Returns:
        True if node with node_label and node_properties exists in the DGL, False otherwise.
    """
    for property_key, property_value in properties.items():
        if not isinstance(property_value, Number) or property_key not in translated_properties:
            continue
        for entity_property_value in entity_data[property_key]:
            # Check which conditions are OK
            if (isinstance(property_value, list) and entity_property_value.tolist() == property_value) or (
                not isinstance(property_value, list) and entity_property_value.item() == property_value
            ):
                return True
    return False


def _check_entity_exists_dgl_to_memgraph(entity_data, entity_id: int, properties: Dict[str, Any]):
    """Checks that all properties that are in DGL, exist in Memgraph too.
    Args:
        entity_data: `graph.nodes[node_label]` or `graph.edges[etype]`
        entity_id: Edge id or dgl id
        properties: Entity's properties from the Memgraph.
    """
    for dgl_property_key, dgl_property_value in entity_data.items():
        if not dgl_property_key.startswith("_"):
            assert to_cypher_value(dgl_property_value[entity_id]) == properties[dgl_property_key]


def _check_all_edges_exist_memgraph_dgl(
    graph,
    translator: DGLTranslator,
    translated_node_properties: Set[str] = {},
    translated_edge_properties: Set[str] = {},
    total_num_edges: int = None,
    direction="EXP",
):
    """Check whether all edges that exist in Memgraph, exist in the DGLGraph too.
    Args:
        graph: Reference to the DGLGraph
        translator: Reference to the used DGLTranslator.
        total_num_edges: Total number of edges in the DGL graph, checked only when importing from DGL.
        direction: EXP for exporting Memgraph to DGL, IMP for DGL to Memgraph.
    """
    query_results = list(Match().node(variable="n").to(variable="r").node(variable="m").return_().execute())
    assert total_num_edges is None or len(query_results) == total_num_edges
    for row in query_results:
        row_values = row.values()
        for entity in row_values:
            if isinstance(entity, Node):
                if direction == "EXP":
                    # If properties don't exist,just check that nodes with such label exist
                    if not entity._properties:
                        assert Translator.merge_labels(entity._labels, DEFAULT_NODE_LABEL) in graph.ntypes
                    else:
                        assert _check_entity_exists_in_dgl(
                            graph.nodes[Translator.merge_labels(entity._labels, DEFAULT_NODE_LABEL)].data,
                            entity._properties,
                            translated_node_properties,
                        )
                else:
                    _check_entity_exists_dgl_to_memgraph(
                        graph.nodes[Translator.merge_labels(entity._labels, DEFAULT_NODE_LABEL)].data,
                        entity._properties[DGL_ID],
                        entity._properties,
                    )

            elif isinstance(entity, Relationship):
                source_node_label, dest_node_label = None, None
                for new_entity in row_values:
                    if new_entity._id == entity._start_node_id and isinstance(new_entity, Node):
                        source_node_label = Translator.merge_labels(new_entity._labels, DEFAULT_NODE_LABEL)
                    elif new_entity._id == entity._end_node_id and isinstance(new_entity, Node):
                        dest_node_label = Translator.merge_labels(new_entity._labels, DEFAULT_NODE_LABEL)
                if direction == "EXP":
                    # If properties don't exist,just check that edges with such label exist
                    if not entity._properties:
                        assert (
                            source_node_label,
                            entity._type if entity._type else DEFAULT_EDGE_TYPE,
                            dest_node_label,
                        ) in graph.canonical_etypes
                    else:
                        assert _check_entity_exists_in_dgl(
                            graph.edges[
                                (
                                    source_node_label,
                                    entity._type if entity._type else DEFAULT_EDGE_TYPE,
                                    dest_node_label,
                                )
                            ].data,
                            entity._properties,
                            translated_edge_properties,
                        )
                else:
                    _check_entity_exists_dgl_to_memgraph(
                        graph.edges[
                            (
                                source_node_label,
                                entity._type if entity._type else DEFAULT_EDGE_TYPE,
                                dest_node_label,
                            )
                        ].data,
                        entity._properties[DGL_ID],
                        entity._properties,
                    )


##########
# DGL EXPORT
##########


def test_dgl_export_multigraph(memgraph):
    """Test graph with no isolated nodes and only one numerical feature and bidirectional edges."""
    # Prepare queries
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
    translator = DGLTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.canonical_etypes) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.ntypes) == 1
    assert graph.ntypes[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.canonical_etypes[0] == can_etype
    assert graph[can_etype].number_of_nodes() == 4
    assert graph[can_etype].number_of_edges() == 8
    assert len(graph.nodes[source_node_label].data.keys()) == 1
    assert len(graph.edges[(source_node_label, edge_type, dest_node_label)]) == 1
    translated_node_properties = {"id"}
    translated_edge_properties = {"edge_id"}
    _check_all_edges_exist_memgraph_dgl(graph, translator, translated_node_properties, translated_edge_properties)


def test_dgl_multiple_nodes_same_features(memgraph):
    """Test graph with no isolated nodes and only one numerical feature and bidirectional edges."""
    # Prepare queries
    queries = []
    queries.append(f"CREATE (m:Node {{id: 1}})")
    queries.append(f"CREATE (m:Node {{id: 1}})")
    queries.append(f"CREATE (m:Node {{id: 3}})")
    queries.append(f"CREATE (m:Node {{id: 4}})")
    queries.append(f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 3}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 4}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 5}}]->(m)")
    queries.append(f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 8}}]->(m)")
    execute_queries(memgraph, queries)
    # Translate to DGL graph
    translator = DGLTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.canonical_etypes) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.ntypes) == 1
    assert graph.ntypes[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.canonical_etypes[0] == can_etype
    assert graph[can_etype].number_of_nodes() == 4
    assert graph[can_etype].number_of_edges() == 7
    assert len(graph.nodes[source_node_label].data.keys()) == 1
    assert len(graph.edges[(source_node_label, edge_type, dest_node_label)]) == 1
    translated_node_properties = {"id"}
    translated_edge_properties = {"edge_id"}
    _check_all_edges_exist_memgraph_dgl(graph, translator, translated_node_properties, translated_edge_properties)


def test_dgl_export_graph_no_features(memgraph):
    """Export graph which has all nodes and edges without properties."""
    # Prepare queries
    queries = []
    queries.append(f"CREATE (m:Node {{id: 1}})")
    queries.append(f"CREATE (m:Node {{id: 2}})")
    queries.append(f"CREATE (m:Node {{id: 3}})")
    queries.append(f"CREATE (m:Node {{id: 4}})")
    queries.append(f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION]->(m)")
    queries.append(f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION]->(m)")
    queries.append(f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION]->(m)")
    queries.append(f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION]->(m)")
    queries.append(f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION]->(m)")
    queries.append(f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION]->(m)")
    queries.append(f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION]->(m)")
    queries.append(f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION]->(m)")
    queries.append(f"MATCH (n:Node) REMOVE n.id")
    memgraph = execute_queries(memgraph, queries)
    # Translate to DGL graph
    translator = DGLTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.canonical_etypes) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.ntypes) == 1
    assert graph.ntypes[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.canonical_etypes[0] == can_etype
    assert graph[can_etype].number_of_nodes() == 4
    assert graph[can_etype].number_of_edges() == 8
    assert len(graph.nodes[source_node_label].data.keys()) == 0
    assert len(graph.edges[(source_node_label, edge_type, dest_node_label)].data.keys()) == 0
    _check_all_edges_exist_memgraph_dgl(graph, translator)


def test_dgl_export_graph_no_features_no_labels(memgraph):
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
    # Translate to DGL graph
    translator = DGLTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.canonical_etypes) == 1
    source_node_label, edge_type, dest_node_label = (
        DEFAULT_NODE_LABEL,
        "CONNECTION",
        DEFAULT_NODE_LABEL,
    )  # default node label and default edge type
    assert len(graph.ntypes) == 1
    assert graph.ntypes[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.canonical_etypes[0] == can_etype
    assert graph[can_etype].number_of_nodes() == 4
    assert graph[can_etype].number_of_edges() == 8
    _check_all_edges_exist_memgraph_dgl(graph, translator)


def test_dgl_export_multiple_labels(memgraph):
    """Tests exporting to DGL when using multiple labels for nodes."""
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
    # Translate to DGL graph
    translator = DGLTranslator()
    graph = translator.get_instance()
    # Check metadata
    assert len(graph.ntypes) == 2  # Node and Node:Mode
    assert len(graph.canonical_etypes) == 4
    can_type_1 = ("Node", "CONNECTION", "Mode:Node")
    can_type_2 = ("Mode:Node", "CONNECTION", "Node")
    can_type_3 = ("Mode:Node", "CONNECTION", "Mode:Node")
    can_type_4 = ("Node", "CONNECTION", "Node")
    assert can_type_1 in graph.canonical_etypes
    assert can_type_2 in graph.canonical_etypes
    assert can_type_3 in graph.canonical_etypes
    assert can_type_4 in graph.canonical_etypes
    assert graph.num_nodes("Node") == 2
    assert graph.num_nodes("Mode:Node") == 2
    assert graph.num_edges(etype=can_type_1) == 1
    assert graph.num_edges(etype=can_type_2) == 3
    assert graph.num_edges(etype=can_type_3) == 1
    assert graph.num_edges(etype=can_type_4) == 1
    for ntype in graph.ntypes:
        assert len(graph.nodes[ntype].data.keys()) == 1
    for etype in graph.canonical_etypes:
        assert len(graph.edges[etype].data.keys()) == 1
    translated_node_properties = {"id"}
    translated_edge_properties = {"edge_id"}
    _check_all_edges_exist_memgraph_dgl(graph, translator, translated_node_properties, translated_edge_properties)


def test_dgl_export_many_numerical_properties(memgraph):
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
    # Translate to DGL graph
    translator = DGLTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.canonical_etypes) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.ntypes) == 1
    assert graph.ntypes[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.canonical_etypes[0] == can_etype
    assert graph[can_etype].number_of_nodes() == 4
    assert graph[can_etype].number_of_edges() == 8
    assert len(graph.nodes[source_node_label].data.keys()) == 3
    assert len(graph.edges[(source_node_label, edge_type, dest_node_label)].data.keys()) == 3
    translated_node_properties = {"id", "num", "edem"}
    translated_edge_properties = {"edge_id", "edge_num", "edge_edem"}
    _check_all_edges_exist_memgraph_dgl(graph, translator, translated_node_properties, translated_edge_properties)


def test_dgl_export_list_properties(memgraph):
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
    # Translate to DGL graph
    translator = DGLTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.canonical_etypes) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.ntypes) == 1
    assert graph.ntypes[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.canonical_etypes[0] == can_etype
    assert graph[can_etype].number_of_nodes() == 4
    assert graph[can_etype].number_of_edges() == 8
    assert len(graph.nodes[source_node_label].data.keys()) == 4
    assert len(graph.edges[(source_node_label, edge_type, dest_node_label)].data.keys()) == 4
    translated_node_properties = {"id", "num", "edem", "lst"}
    translated_edge_properties = {"edge_id", "edge_num", "edge_edem", "edge_lst"}
    _check_all_edges_exist_memgraph_dgl(graph, translator, translated_node_properties, translated_edge_properties)


def test_dgl_export_various_dimensionality_list_properties(memgraph):
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
    # Translate to DGL graph
    translator = DGLTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.canonical_etypes) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.ntypes) == 1
    assert graph.ntypes[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.canonical_etypes[0] == can_etype
    assert graph[can_etype].number_of_nodes() == 4
    assert graph[can_etype].number_of_edges() == 8
    assert len(graph.nodes[source_node_label].data.keys()) == 3
    assert len(graph.edges[(source_node_label, edge_type, dest_node_label)].data.keys()) == 3
    translated_node_properties = {"id", "num", "edem"}
    translated_edge_properties = {"edge_id", "edge_num", "edge_edem"}
    _check_all_edges_exist_memgraph_dgl(graph, translator, translated_node_properties, translated_edge_properties)


def test_dgl_export_non_numeric_properties(memgraph):
    """Test graph which has some non-numeric properties. Non-numeric properties will be discarded."""
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
    # Translate to DGL graph
    translator = DGLTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.canonical_etypes) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.ntypes) == 1
    assert graph.ntypes[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.canonical_etypes[0] == can_etype
    assert graph[can_etype].number_of_nodes() == 4
    assert graph[can_etype].number_of_edges() == 8
    assert len(graph.nodes[source_node_label].data.keys()) == 3
    assert len(graph.edges[(source_node_label, edge_type, dest_node_label)].data.keys()) == 3
    translated_node_properties = {"id", "num", "lst"}
    translated_edge_properties = {"edge_id", "edge_num", "edge_lst"}
    _check_all_edges_exist_memgraph_dgl(graph, translator, translated_node_properties, translated_edge_properties)


def test_dgl_export_partially_existing_numeric_properties(memgraph):
    """Test graph for which some numeric feature is not set on all nodes. Then such a feature is ignored."""
    # Prepare queries
    queries = []
    queries.append(f"CREATE (m:Node {{id: 1, num: 212, lst: [2, 3, 3, 2]}})")
    queries.append(f"CREATE (m:Node {{id: 2, num: 211, lst: [2, 2, 3, 3]}})")
    queries.append(f"CREATE (m:Node {{id: 3, lst: [3, 2, 2, 3]}})")
    queries.append(f"CREATE (m:Node {{id: 4, lst: [2, 2, 2, 3]}})")
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
        f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 4, edge_edem: 'la', edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 5, edge_edem: 'le', edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 6, edge_edem: 'do', edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 7, edge_num: 99, edge_edem: 're', edge_lst: [1, 1, 0, 0]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 8, edge_num: 99, edge_edem: 'mi', edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    execute_queries(memgraph, queries)
    # Translate to DGL graph
    translator = DGLTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.canonical_etypes) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.ntypes) == 1
    assert graph.ntypes[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.canonical_etypes[0] == can_etype
    assert graph[can_etype].number_of_nodes() == 4
    assert graph[can_etype].number_of_edges() == 8
    assert len(graph.nodes[source_node_label].data.keys()) == 2
    assert len(graph.edges[(source_node_label, edge_type, dest_node_label)].data.keys()) == 2
    translated_node_properties = {"id", "lst"}
    translated_edge_properties = {"edge_id", "edge_lst"}
    _check_all_edges_exist_memgraph_dgl(graph, translator, translated_node_properties, translated_edge_properties)


def test_dgl_export_same_property_multiple_types(memgraph):
    """Test graph for which some feature has multiple data types, e.g str and Number. Such feature won't be parsed for every node -> the policy is don't insert features on nodes
    and edges that cannot be set on all of them."""
    # Prepare queries
    queries = []
    queries.append(f"CREATE (m:Node {{id: 1, num: 80, edem: 30, lst: [2, 3, 3, 2]}})")
    queries.append(f"CREATE (m:Node {{id: 2, num: 91, edem: 32, lst: [2, 2, 3, 3]}})")
    queries.append(f"CREATE (m:Node {{id: 3, num: 'not num', edem: 34, lst: [3, 2, 2, 3]}})")
    queries.append(f"CREATE (m:Node {{id: 4, num: '12', edem: 34, lst: [2, 2, 2, 3]}})")
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
        f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 5, edge_num: '99', edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 6, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 'rnd id', edge_num: 'unknown', edge_edem: 12, edge_lst: [1, 1, 0, 0]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 8, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
    )
    execute_queries(memgraph, queries)
    # Translate to DGL graph
    translator = DGLTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.canonical_etypes) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.ntypes) == 1
    assert graph.ntypes[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.canonical_etypes[0] == can_etype
    assert graph[can_etype].number_of_nodes() == 4
    assert graph[can_etype].number_of_edges() == 8
    assert len(graph.nodes[source_node_label].data.keys()) == 3
    assert len(graph.edges[(source_node_label, edge_type, dest_node_label)].data.keys()) == 2
    translated_node_properties = {"id", "edem", "lst"}
    translated_edge_properties = {"edge_edem", "edge_lst"}
    _check_all_edges_exist_memgraph_dgl(graph, translator, translated_node_properties, translated_edge_properties)


##########
# DGL IMPORT
##########


def get_dgl_translator_run_queries(graph, memgraph_):
    translator = DGLTranslator()
    queries = translator.to_cypher_queries(graph)
    execute_queries(memgraph_, queries)
    return translator


def test_dgl_import_homogeneous(memgraph):
    """Test homogenous graph conversion."""
    # Init graph
    src = np.array(
        [
            1,
            2,
            2,
            3,
            3,
            3,
            4,
            5,
            6,
            6,
            6,
            7,
            7,
            7,
            7,
            8,
            8,
            9,
            10,
            10,
            10,
            11,
            12,
            12,
            13,
            13,
            13,
            13,
            16,
            16,
            17,
            17,
            19,
            19,
            21,
            21,
            25,
            25,
            27,
            27,
            27,
            28,
            29,
            29,
            30,
            30,
            31,
            31,
            31,
            31,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            33,
            33,
            33,
            33,
            33,
            33,
            33,
            33,
            33,
            33,
            33,
            33,
            33,
            33,
            33,
            33,
            33,
        ]
    )
    dst = np.array(
        [
            0,
            0,
            1,
            0,
            1,
            2,
            0,
            0,
            0,
            4,
            5,
            0,
            1,
            2,
            3,
            0,
            2,
            2,
            0,
            4,
            5,
            0,
            0,
            3,
            0,
            1,
            2,
            3,
            5,
            6,
            0,
            1,
            0,
            1,
            0,
            1,
            23,
            24,
            2,
            23,
            24,
            2,
            23,
            26,
            1,
            8,
            0,
            24,
            25,
            28,
            2,
            8,
            14,
            15,
            18,
            20,
            22,
            23,
            29,
            30,
            31,
            8,
            9,
            13,
            14,
            15,
            18,
            19,
            20,
            22,
            23,
            26,
            27,
            28,
            29,
            30,
            31,
            32,
        ]
    )
    graph = dgl.DGLGraph((src, dst))
    # Initialize translator and insert into the Memgraph
    # Let's test
    # Check all that are in Memgraph are in DGL too
    _check_all_edges_exist_memgraph_dgl(
        graph, get_dgl_translator_run_queries(graph, memgraph), total_num_edges=78, direction="IMP"
    )


def test_dgl_import_simple_heterogeneous(memgraph):
    """Test heterogeneous graph conversion."""
    graph = dgl.heterograph(
        {
            ("user", "PLUS", "movie"): (np.array([0, 0, 1]), np.array([0, 1, 0])),
            ("user", "MINUS", "movie"): (np.array([2]), np.array([1])),
        }
    )
    _check_all_edges_exist_memgraph_dgl(
        graph, get_dgl_translator_run_queries(graph, memgraph), total_num_edges=4, direction="IMP"
    )


def test_dgl_import_simple_heterogeneous_with_features(memgraph):
    """Simple heterogeneous graph for which also node and edge features are set."""
    graph = dgl.heterograph(
        {
            ("user", "PLUS", "movie"): (np.array([0, 0, 1]), np.array([0, 1, 0])),
            ("user", "MINUS", "movie"): (np.array([2]), np.array([1])),
        }
    )
    # Set node features
    graph.nodes["user"].data["prop1"] = torch.randn(size=(3, 1))
    graph.nodes["user"].data["prop2"] = torch.randn(size=(3, 1))
    graph.nodes["movie"].data["prop1"] = torch.randn(size=(2, 1))
    graph.nodes["movie"].data["prop2"] = torch.randn(size=(2, 1))
    graph.nodes["movie"].data["prop3"] = torch.randn(size=(2, 1))
    # Set edge features
    graph.edges[("user", "PLUS", "movie")].data["edge_prop1"] = torch.randn(size=(3, 1))
    graph.edges[("user", "PLUS", "movie")].data["edge_prop2"] = torch.randn(size=(3, 1))
    graph.edges[("user", "MINUS", "movie")].data["edge_prop1"] = torch.randn(size=(1, 1))

    _check_all_edges_exist_memgraph_dgl(
        graph, get_dgl_translator_run_queries(graph, memgraph), total_num_edges=4, direction="IMP"
    )


def test_dgl_import_multidimensional_features(memgraph):
    """Tests how conversion works when having multidimensional features."""
    graph = dgl.heterograph(
        {
            ("user", "PLUS", "movie"): (np.array([0, 0, 1]), np.array([0, 1, 0])),
            ("user", "MINUS", "movie"): (np.array([2]), np.array([1])),
        }
    )
    # Set node features
    graph.nodes["user"].data["prop1"] = torch.randn(size=(3, 2, 2))
    graph.nodes["user"].data["prop2"] = torch.randn(size=(3, 2, 3))
    graph.nodes["movie"].data["prop1"] = torch.randn(size=(2, 3))
    graph.nodes["movie"].data["prop2"] = torch.randn(size=(2, 3))
    graph.nodes["movie"].data["prop3"] = torch.randn(size=(2, 2))
    # Set edge features
    graph.edges[("user", "PLUS", "movie")].data["edge_prop1"] = torch.randn(size=(3, 2))
    graph.edges[("user", "PLUS", "movie")].data["edge_prop2"] = torch.randn(size=(3, 3, 10))
    graph.edges[("user", "MINUS", "movie")].data["edge_prop1"] = torch.randn(size=(1, 4))

    _check_all_edges_exist_memgraph_dgl(
        graph, get_dgl_translator_run_queries(graph, memgraph), total_num_edges=4, direction="IMP"
    )


def test_dgl_import_custom_dataset(memgraph):
    """Tests how conversion from some custom DGL's dataset works."""
    dataset = TUDataset("ENZYMES")
    graph = dataset[0][0]
    # Get queries
    _check_all_edges_exist_memgraph_dgl(
        graph, get_dgl_translator_run_queries(graph, memgraph), total_num_edges=168, direction="IMP"
    )
