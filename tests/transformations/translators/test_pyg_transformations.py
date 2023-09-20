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

from gqlalchemy import Match
from gqlalchemy.models import Node, Relationship
from gqlalchemy.transformations.translators.translator import Translator
from gqlalchemy.transformations.constants import PYG_ID, DEFAULT_NODE_LABEL, DEFAULT_EDGE_TYPE
from gqlalchemy.utilities import to_cypher_value
from tests.transformations.common import execute_queries

PyGTranslator = pytest.importorskip("gqlalchemy.transformations.translators.pyg_translator.PyGTranslator")
Data = pytest.importorskip("torch_geometric.data.Data")
HeteroData = pytest.importorskip("torch_geometric.data.HeteroData")
FakeDataset = pytest.importorskip("torch_geometric.datasets.FakeDataset")
FakeHeteroDataset = pytest.importorskip("torch_geometric.datasets.FakeHeteroDataset")
torch = pytest.importorskip("torch")

pytestmark = [pytest.mark.extras, pytest.mark.pyg]

# TODO: test number of properties that were converted

##########
# UTILS
##########


def _check_entity_exists_in_pyg(
    entity_data, entity_mark: str, properties: Dict[str, Any], translated_properties: Set[str] = {}
):
    """Checks whether the node with `node label` and `node_properties` exists in the pyg.
    Args:
        entity_data: `graph.node_items()` or `graph.edge_items()`.
        entity_mark: Node's label or edge type.
        properties: Entity's properties from the Memgraph.
        translated_properties: Properties that are translated from Memgraph to pyg.
    Returns:
        True if node with node_label and node_properties exists in the pyg, False otherwise.
    """
    for property_key, property_value in properties.items():
        if not isinstance(property_value, Number) or property_key not in translated_properties:
            continue
        for pyg_label, pyg_properties in entity_data:
            if pyg_label == entity_mark:  # because it is stored in tuples
                for entity_property_value in pyg_properties[property_key]:
                    # Check which conditions are OK
                    if (isinstance(property_value, list) and entity_property_value.tolist() == property_value) or (
                        not isinstance(property_value, list) and entity_property_value.item() == property_value
                    ):
                        return True
    return False


def _check_entity_exists_in_pyg_homogeneous(entity_data, properties: Dict[str, Any], entity_id):
    """Checks whether the node with `node label` and `node_properties` exists in the pyg.
    Args:
        entity_data: `graph.node_items()`, `graph.edge_items()' or node_properties and etype_properties when dealing with homogeneous graph.
        entity_id: Edge id or pyg id
        properties: Entity's properties from the Memgraph.
    Returns:
        True if node with node_label and node_properties exists in the pyg, False otherwise.
    """
    for property_key, property_value in entity_data.items():
        if not property_key.startswith("_"):
            assert to_cypher_value(property_value[entity_id]) == properties[property_key]
    return False


def _check_entity_exists_pyg_to_memgraph(entity_data, entity_mark, entity_id, properties: Dict[str, Any]):
    """Checks that all properties that are in pyg, exist in Memgraph too.
    Args:
        entity_data: `graph.node_items()` or `graph.edge_items()`.
        entity_mark: Node's label or edge type.
        entity_id: Edge id or pyg id
        properties: Entity's properties from the Memgraph.
    """
    for pyg_label, pyg_properties in entity_data:
        if pyg_label == entity_mark:
            for pyg_property_key, pyg_property_value in pyg_properties.items():
                if pyg_property_key.startswith("_"):
                    continue
                assert to_cypher_value(pyg_property_value[entity_id]) == properties[pyg_property_key]


def _check_all_edges_exist_memgraph_pyg(
    graph,
    translator: PyGTranslator,
    translated_node_properties: Set[str] = {},
    translated_edge_properties: Set[str] = {},
    total_num_edges: int = None,
    direction="EXP",
):
    """Check whether all edges that exist in Memgraph, exist in the pygGraph too.
    Args:
        graph: Reference to the pygGraph
        translator: Reference to the used PyGTranslator.
        total_num_edges: Total number of edges in the pyg graph, checked only when importing from pyg.
        direction: EXP for exporting Memgraph to pyg, IMP for pyg to Memgraph.
        TODO: maybe it would be better to use static variables for default node labels if this is the only dependency
    """
    query_results = list(Match().node(variable="n").to(variable="r").node(variable="m").return_().execute())
    assert total_num_edges is None or len(query_results) == total_num_edges
    if isinstance(graph, Data):
        node_properties, etype_properties = PyGTranslator.extract_node_edge_properties_from_homogeneous_graph(graph)
    for row in query_results:
        row_values = row.values()
        for entity in row_values:
            if isinstance(entity, Node):
                node_label = Translator.merge_labels(entity._labels, DEFAULT_NODE_LABEL)
                if not entity._properties:
                    assert node_label in graph.node_types
                    continue

                if direction == "EXP":
                    # If properties don't exist,just check that nodes with such label exist
                    assert _check_entity_exists_in_pyg(
                        graph.node_items(),
                        node_label,
                        entity._properties,
                        translated_node_properties,
                    )
                else:
                    if isinstance(graph, Data):
                        _check_entity_exists_in_pyg_homogeneous(
                            node_properties,
                            entity._properties,
                            entity._properties[PYG_ID],
                        )
                    elif isinstance(graph, HeteroData):
                        _check_entity_exists_pyg_to_memgraph(
                            graph.node_items(),
                            node_label,
                            entity._properties[PYG_ID],
                            entity._properties,
                        )

            elif isinstance(entity, Relationship):
                source_node_label, dest_node_label = None, None
                for new_entity in row_values:
                    if new_entity._id == entity._start_node_id and isinstance(new_entity, Node):
                        source_node_label = Translator.merge_labels(new_entity._labels, DEFAULT_NODE_LABEL)
                    elif new_entity._id == entity._end_node_id and isinstance(new_entity, Node):
                        dest_node_label = Translator.merge_labels(new_entity._labels, DEFAULT_NODE_LABEL)
                if not entity._properties:
                    assert (
                        source_node_label,
                        entity._type if entity._type else DEFAULT_EDGE_TYPE,
                        dest_node_label,
                    ) in graph.edge_types
                    continue
                if direction == "EXP":
                    # If properties don't exist,just check that edges with such label exist
                    assert _check_entity_exists_in_pyg(
                        graph.edge_items(),
                        (
                            source_node_label,
                            entity._type if entity._type else DEFAULT_EDGE_TYPE,
                            dest_node_label,
                        ),
                        entity._properties,
                        translated_edge_properties,
                    )
                else:
                    if isinstance(graph, Data):
                        _check_entity_exists_in_pyg_homogeneous(
                            etype_properties, entity._properties, translated_edge_properties
                        )
                    elif isinstance(graph, HeteroData):
                        _check_entity_exists_pyg_to_memgraph(
                            graph.edge_items(),
                            (
                                source_node_label,
                                entity._type if entity._type else DEFAULT_EDGE_TYPE,
                                dest_node_label,
                            ),
                            entity._properties[PYG_ID],
                            entity._properties,
                        )


##########
# pyg EXPORT
##########


def test_pyg_export_multigraph(memgraph):
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
    # Translate to pyg graph
    translator = PyGTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.edge_types) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.node_types) == 1
    assert graph.node_types[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.edge_types[0] == can_etype
    assert graph[source_node_label].num_nodes == 4
    assert graph[can_etype].num_edges == 8
    # print(f"Graph: {graph.num_node_features}|")
    # print(f"Graph: {graph.num_edge_features}|")
    # assert graph.num_node_features[source_node_label] == 1
    # assert graph.num_edge_features[(source_node_label, edge_type, dest_node_label)] == 1
    translated_node_properties = {"id"}
    translated_edge_properties = {"edge_id"}
    _check_all_edges_exist_memgraph_pyg(graph, translator, translated_node_properties, translated_edge_properties)


def test_pyg_multiple_nodes_same_features(memgraph):
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
    # Translate to pyg graph
    translator = PyGTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.edge_types) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.node_types) == 1
    assert graph.node_types[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.edge_types[0] == can_etype
    assert graph[source_node_label].num_nodes == 4
    assert graph[can_etype].num_edges == 7
    # Property stuff
    # assert len(graph.nodes[source_node_label].data.keys()) == 1
    # assert len(graph.edges[(source_node_label, edge_type, dest_node_label)]) == 1
    translated_node_properties = {"id"}
    translated_edge_properties = {"edge_id"}
    _check_all_edges_exist_memgraph_pyg(graph, translator, translated_node_properties, translated_edge_properties)


def test_pyg_export_graph_no_features(memgraph):
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
    execute_queries(memgraph, queries)
    # Translate to pyg graph
    translator = PyGTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.edge_types) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.node_types) == 1
    assert graph.node_types[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.edge_types[0] == can_etype
    assert graph[source_node_label].num_nodes == 4
    assert graph[can_etype].num_edges == 8
    # assert len(graph.nodes[source_node_label].data.keys()) == 0
    # assert len(graph.edges[(source_node_label, edge_type, dest_node_label)].data.keys()) == 0
    _check_all_edges_exist_memgraph_pyg(graph, translator)


def test_pyg_export_graph_no_features_no_labels(memgraph):
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
    # Translate to pyg graph
    translator = PyGTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.edge_types) == 1
    source_node_label, edge_type, dest_node_label = (
        DEFAULT_NODE_LABEL,
        "CONNECTION",
        DEFAULT_NODE_LABEL,
    )  # default node label and default edge type
    assert len(graph.node_types) == 1
    assert graph.node_types[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.edge_types[0] == can_etype
    assert graph[source_node_label].num_nodes == 4
    assert graph[can_etype].num_edges == 8
    _check_all_edges_exist_memgraph_pyg(graph, translator)


def test_pyg_export_multiple_labels(memgraph):
    """Tests exporting to pyg when using multiple labels for nodes."""
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
    # Translate to pyg graph
    translator = PyGTranslator()
    graph = translator.get_instance()
    # Check metadata
    assert len(graph.node_types) == 2  # Node and Node:Mode
    assert len(graph.edge_types) == 4
    can_type_1 = ("Node", "CONNECTION", "Mode:Node")
    can_type_2 = ("Mode:Node", "CONNECTION", "Node")
    can_type_3 = ("Mode:Node", "CONNECTION", "Mode:Node")
    can_type_4 = ("Node", "CONNECTION", "Node")
    assert can_type_1 in graph.edge_types
    assert can_type_2 in graph.edge_types
    assert can_type_3 in graph.edge_types
    assert can_type_4 in graph.edge_types
    assert graph["Node"].num_nodes == 2
    assert graph["Mode:Node"].num_nodes == 2
    assert graph[can_type_1].num_edges == 1
    assert graph[can_type_2].num_edges == 3
    assert graph[can_type_3].num_edges == 1
    assert graph[can_type_4].num_edges == 1
    # for ntype in graph.node_types:
    #     assert len(graph.nodes[ntype].data.keys()) == 1
    # for etype in graph.edge_types:
    #     assert len(graph.edges[etype].data.keys()) == 1
    translated_node_properties = {"id"}
    translated_edge_properties = {"edge_id"}
    _check_all_edges_exist_memgraph_pyg(graph, translator, translated_node_properties, translated_edge_properties)


def test_pyg_export_many_numerical_properties(memgraph):
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
    # Translate to pyg graph
    translator = PyGTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.edge_types) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.node_types) == 1
    assert graph.node_types[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.edge_types[0] == can_etype
    assert graph[source_node_label].num_nodes == 4
    assert graph[can_etype].num_edges == 8
    # assert len(graph.nodes[source_node_label].data.keys()) == 3
    # assert len(graph.edges[(source_node_label, edge_type, dest_node_label)].data.keys()) == 3
    translated_node_properties = {"id", "num", "edem"}
    translated_edge_properties = {"edge_id", "edge_num", "edge_edem"}
    _check_all_edges_exist_memgraph_pyg(graph, translator, translated_node_properties, translated_edge_properties)


def test_pyg_export_list_properties(memgraph):
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
    # Translate to pyg graph
    translator = PyGTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.edge_types) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.node_types) == 1
    assert graph.node_types[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.edge_types[0] == can_etype
    assert graph[source_node_label].num_nodes == 4
    assert graph[can_etype].num_edges == 8
    # assert len(graph.nodes[source_node_label].data.keys()) == 4
    # assert len(graph.edges[(source_node_label, edge_type, dest_node_label)].data.keys()) == 4
    translated_node_properties = {"id", "num", "edem", "lst"}
    translated_edge_properties = {"edge_id", "edge_num", "edge_edem", "edge_lst"}
    _check_all_edges_exist_memgraph_pyg(graph, translator, translated_node_properties, translated_edge_properties)


def test_pyg_export_list_properties_x_y(memgraph):
    """Test graph that has several numerical features on all nodes and edges together with lists that could represent feature vectors."""
    # Prepare queries
    queries = []
    queries.append(f"CREATE (m:Node {{id: 1, y: 82, edem: 21, x: [2, 3, 3, 2]}})")
    queries.append(f"CREATE (m:Node {{id: 2, y: 91, edem: 32, x: [2, 2, 3, 3]}})")
    queries.append(f"CREATE (m:Node {{id: 3, y: 100, edem: 34, x: [3, 2, 2, 3]}})")
    queries.append(f"CREATE (m:Node {{id: 4, y: 12, edem: 34, x: [2, 2, 2, 3]}})")
    queries.append(
        f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 1, edge_num: 99, edge_edem: 12, x: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 2, edge_num: 99, edge_edem: 12, x: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 3, edge_num: 99, edge_edem: 12, x: [1, 0, 1, 0]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 4, edge_num: 99, edge_edem: 12, x: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 5, edge_num: 99, edge_edem: 12, x: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 6, edge_num: 99, edge_edem: 12, x: [0, 1, 0, 1]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 7, edge_num: 99, edge_edem: 12, x: [1, 1, 0, 0]}}]->(m)"
    )
    queries.append(
        f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 8, edge_num: 99, edge_edem: 12, x: [0, 1, 0, 1]}}]->(m)"
    )
    execute_queries(memgraph, queries)
    # Translate to pyg graph
    translator = PyGTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.edge_types) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.node_types) == 1
    assert graph.node_types[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.edge_types[0] == can_etype
    assert graph[source_node_label].num_nodes == 4
    assert graph[can_etype].num_edges == 8
    # assert len(graph.nodes[source_node_label].data.keys()) == 4
    # assert len(graph.edges[(source_node_label, edge_type, dest_node_label)].data.keys()) == 4
    translated_node_properties = {"id", "num", "edem", "lst"}
    translated_edge_properties = {"edge_id", "edge_num", "edge_edem", "edge_lst"}
    _check_all_edges_exist_memgraph_pyg(graph, translator, translated_node_properties, translated_edge_properties)


def test_pyg_export_various_dimensionality_list_properties(memgraph):
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
    # Translate to pyg graph
    translator = PyGTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.edge_types) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.node_types) == 1
    assert graph.node_types[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.edge_types[0] == can_etype
    assert graph[source_node_label].num_nodes == 4
    assert graph[can_etype].num_edges == 8
    # assert len(graph.nodes[source_node_label].data.keys()) == 3
    # assert len(graph.edges[(source_node_label, edge_type, dest_node_label)].data.keys()) == 3
    translated_node_properties = {"id", "num", "edem"}
    translated_edge_properties = {"edge_id", "edge_num", "edge_edem"}
    _check_all_edges_exist_memgraph_pyg(graph, translator, translated_node_properties, translated_edge_properties)


def test_pyg_export_non_numeric_properties(memgraph):
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
    # Translate to pyg graph
    translator = PyGTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.edge_types) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.node_types) == 1
    assert graph.node_types[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.edge_types[0] == can_etype
    assert graph[source_node_label].num_nodes == 4
    assert graph[can_etype].num_edges == 8
    # assert len(graph.nodes[source_node_label].data.keys()) == 3
    # assert len(graph.edges[(source_node_label, edge_type, dest_node_label)].data.keys()) == 3
    translated_node_properties = {"id", "num", "lst"}
    translated_edge_properties = {"edge_id", "edge_num", "edge_lst"}
    _check_all_edges_exist_memgraph_pyg(graph, translator, translated_node_properties, translated_edge_properties)


def test_pyg_export_partially_existing_numeric_properties(memgraph):
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
    # Translate to pyg graph
    translator = PyGTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.edge_types) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.node_types) == 1
    assert graph.node_types[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.edge_types[0] == can_etype
    assert graph[source_node_label].num_nodes == 4
    assert graph[can_etype].num_edges == 8
    # assert len(graph.nodes[source_node_label].data.keys()) == 2
    # assert len(graph.edges[(source_node_label, edge_type, dest_node_label)].data.keys()) == 2
    translated_node_properties = {"id", "lst"}
    translated_edge_properties = {"edge_id", "edge_lst"}
    _check_all_edges_exist_memgraph_pyg(graph, translator, translated_node_properties, translated_edge_properties)


def test_pyg_export_same_property_multiple_types(memgraph):
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
    # Translate to pyg graph
    translator = PyGTranslator()
    graph = translator.get_instance()
    # Test some simple metadata properties
    assert len(graph.edge_types) == 1
    source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
    assert len(graph.node_types) == 1
    assert graph.node_types[0] == source_node_label
    can_etype = (source_node_label, edge_type, dest_node_label)
    assert graph.edge_types[0] == can_etype
    assert graph[source_node_label].num_nodes == 4
    assert graph[can_etype].num_edges == 8
    # assert len(graph.nodes[source_node_label].data.keys()) == 3
    # assert len(graph.edges[(source_node_label, edge_type, dest_node_label)].data.keys()) == 2
    translated_node_properties = {"id", "edem", "lst"}
    translated_edge_properties = {"edge_edem", "edge_lst"}
    _check_all_edges_exist_memgraph_pyg(graph, translator, translated_node_properties, translated_edge_properties)


##########
# pyg IMPORT
##########


def get_pyg_translator_run_queries(graph, memgraph_):
    translator = PyGTranslator()
    queries = translator.to_cypher_queries(graph)
    execute_queries(memgraph_, queries)
    return translator


def test_pyg_import_homogeneous(memgraph):
    """Test homogenous graph conversion."""
    # Init graph
    src = [
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
    dst = [
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
    graph = Data(edge_index=torch.tensor([src, dst], dtype=torch.int32))
    # Initialize translator and insert into the Memgraph
    # Let's test
    # Check all that are in Memgraph are in pyg too
    _check_all_edges_exist_memgraph_pyg(
        graph,
        get_pyg_translator_run_queries(graph, memgraph),
        total_num_edges=78,
        direction="IMP",
    )


def test_pyg_import_simple_heterogeneous(memgraph):
    """Test heterogeneous graph conversion."""
    graph = HeteroData()
    graph[("user", "PLUS", "movie")].edge_index = torch.tensor([[0, 0, 1], [0, 1, 0]], dtype=torch.int32)
    graph[("user", "MINUS", "movie")].edge_index = torch.tensor([[2], [1]], dtype=torch.int32)
    _check_all_edges_exist_memgraph_pyg(
        graph, get_pyg_translator_run_queries(graph, memgraph), total_num_edges=4, direction="IMP"
    )


def test_pyg_import_simple_heterogeneous_with_features(memgraph):
    """Simple heterogeneous graph for which also node and edge features are set."""
    graph = HeteroData()
    graph[("user", "PLUS", "movie")].edge_index = torch.tensor([[0, 0, 1], [0, 1, 0]], dtype=torch.int32)
    graph[("user", "MINUS", "movie")].edge_index = torch.tensor([[2], [1]], dtype=torch.int32)
    # Set node features
    graph["user"].prop1 = torch.randn(size=(3, 1))
    graph["user"].prop2 = torch.randn(size=(3, 1))
    graph["movie"].prop1 = torch.randn(size=(2, 1))
    graph["movie"].prop2 = torch.randn(size=(2, 1))
    graph["movie"].prop3 = torch.randn(size=(2, 1))
    graph["movie"].x = torch.randn(size=(2, 1))
    graph["movie"].y = torch.randn(size=(2, 1))
    # Set edge features
    graph[("user", "PLUS", "movie")].edge_prop1 = torch.randn(size=(3, 1))
    graph[("user", "PLUS", "movie")].edge_prop2 = torch.randn(size=(3, 1))
    graph[("user", "MINUS", "movie")].edge_prop1 = torch.randn(size=(1, 1))

    _check_all_edges_exist_memgraph_pyg(
        graph, get_pyg_translator_run_queries(graph, memgraph), total_num_edges=4, direction="IMP"
    )


def test_pyg_import_multidimensional_features(memgraph):
    """Tests how conversion works when having multidimensional features."""
    # Set node features
    graph = HeteroData()
    graph[("user", "PLUS", "movie")].edge_index = torch.tensor([[0, 0, 1], [0, 1, 0]], dtype=torch.int32)
    graph[("user", "MINUS", "movie")].edge_index = torch.tensor([[2], [1]], dtype=torch.int32)
    # Set node features
    graph["user"].prop1 = torch.randn(size=(3, 2, 2))
    graph["user"].prop2 = torch.randn(size=(3, 2, 3))
    graph["movie"].prop1 = torch.randn(size=(2, 3))
    graph["movie"].prop2 = torch.randn(size=(2, 3))
    graph["movie"].prop3 = torch.randn(size=(2, 2))
    # Set edge features
    graph[("user", "PLUS", "movie")].edge_prop1 = torch.randn(size=(3, 2))
    graph[("user", "PLUS", "movie")].edge_prop2 = torch.randn(size=(3, 3, 10))
    graph[("user", "MINUS", "movie")].edge_prop1 = torch.randn(size=(1, 4))
    graph["movie"].x = torch.randn(size=(2, 4, 6))
    graph["movie"].y = torch.randn(size=(2, 8, 4))

    _check_all_edges_exist_memgraph_pyg(
        graph, get_pyg_translator_run_queries(graph, memgraph), total_num_edges=4, direction="IMP"
    )


def test_pyg_import_custom_dataset(memgraph):
    """Tests how conversion from some custom pyg's dataset works."""
    graph = FakeDataset(avg_num_nodes=100, avg_degree=4, num_channels=10)[0]
    # Get queries
    _check_all_edges_exist_memgraph_pyg(graph, get_pyg_translator_run_queries(graph, memgraph), direction="IMP")


def test_pyg_import_custom_hetero_dataset(memgraph):
    """Tests how conversion from some custom pyg's dataset works."""
    graph = FakeHeteroDataset(avg_num_nodes=100, avg_degree=4, num_channels=10)[0]
    # Get queries
    _check_all_edges_exist_memgraph_pyg(graph, get_pyg_translator_run_queries(graph, memgraph), direction="IMP")
