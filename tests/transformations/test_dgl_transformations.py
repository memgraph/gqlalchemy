# import pytest
from gqlalchemy import Memgraph, Match
from gqlalchemy.models import Node, Relationship
from gqlalchemy.transformations.translators.dgl_translator import DGLTranslator
from gqlalchemy.transformations.translators.translator import Translator
from typing import Dict, Any

# TODO: fix import order


def init_database():
    memgraph = Memgraph()
    memgraph.drop_database()
    return memgraph


# TODO: tests
# multiple nodes that have same properties
# multiple properties for nodes and edges
# different node and edge property types
# loop in the graph
# numerical and non-numerical features
# homogeneous graph
# feature vectors not having same dimensionality
# we have problems when transferring lists


def _check_entity_exists_in_dgl(entity_data, node_properties: Dict[str, Any]):
    """Checks whether the node with `node label` and `node_properties` exists in the DGL.
    Args:
        entity_data: `graph.nodes[node_label]` or `graph.edges[etype]`
        node_properties: Node's properties from the Memgraph.
    Returns:
        True if node with node_label and node_properties exists in the DGL, False otherwise.
    """
    for property_key, property_value in node_properties.items():
        print(f"Property key: {property_key} {property_value} {type(property_value)}")
        for entity_property_value in entity_data[property_key]:
            print(f"Entity property value: {entity_property_value}")
            if (isinstance(property_value, list) and entity_property_value.tolist() == property_value) or (
                not isinstance(property_value, list) and entity_property_value.item() == property_value
            ):
                return True
    return False


def _check_all_edges_exist_memgraph_dgl(graph, translator: DGLTranslator):
    """Check whether all edges that exist in Memgraph, exist in the DGLGraph too.
    Args:
        graph: Reference to the DGLGraph
        translator: Reference to the used DGLTranslator.
        TODO: maybe it would be better to use static variables
    """
    query_results = Match().node(variable="n").to(variable="r").node(variable="m").return_().execute()
    for row in query_results:
        row_values = row.values()
        for entity in row_values:
            if isinstance(entity, Node):
                assert _check_entity_exists_in_dgl(
                    graph.nodes[Translator.merge_labels(entity._labels, translator.default_node_label)].data,
                    entity._properties,
                )
            elif isinstance(entity, Relationship):
                source_node_label, dest_node_label = None, None
                for new_entity in row_values:
                    if new_entity._id == entity._start_node_id and isinstance(new_entity, Node):
                        source_node_label = Translator.merge_labels(new_entity._labels, translator.default_node_label)
                    elif new_entity._id == entity._end_node_id and isinstance(new_entity, Node):
                        dest_node_label = Translator.merge_labels(new_entity._labels, translator.default_node_label)

                assert _check_entity_exists_in_dgl(
                    graph.edges[
                        (
                            source_node_label,
                            entity._type if entity._type else translator.default_edge_type,
                            dest_node_label,
                        )
                    ].data,
                    entity._properties,
                )


def test_dgl_export_multigraph():
    """Test graph with no isolated nodes and only one numerical feature and bidirected edges."""
    # Prepare queries
    memgraph = init_database()
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

    for query in queries:
        memgraph.execute(query)
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
    _check_all_edges_exist_memgraph_dgl(graph, translator)
    memgraph.drop_database()


def test_dgl_export_multiple_labels():
    """Tests exporting to DGL when using multiple labels for nodes."""
    # Prepare queries
    memgraph = init_database()
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
    for query in queries:
        memgraph.execute(query)
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
    _check_all_edges_exist_memgraph_dgl(graph, translator)

    memgraph.drop_database()


def test_dgl_export_many_numerical_properties():
    """Test graph that has several numerical features on nodes and edges."""
    # Prepare queries
    memgraph = init_database()
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

    for query in queries:
        memgraph.execute(query)
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
    _check_all_edges_exist_memgraph_dgl(graph, translator)
    memgraph.drop_database()


def test_dgl_export_list_properties():
    """Test graph that has several numerical features on all nodes and edges together with lists that could represent feature vectors."""
    # Prepare queries
    memgraph = init_database()
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

    for query in queries:
        memgraph.execute(query)
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
    _check_all_edges_exist_memgraph_dgl(graph, translator)
    memgraph.drop_database()
