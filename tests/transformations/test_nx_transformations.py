import networkx as nx

from gqlalchemy.transformations.translators.nx_translator import NxTranslator
from gqlalchemy.transformations.translators.translator import Translator
from gqlalchemy.models import Node, Relationship
from gqlalchemy.transformations.constants import LABEL, EDGE_TYPE
from gqlalchemy import Match
from tests.transformations.utils import init_database


def _check_entity_exists_in_nx(graph_data, entity_properties):
    """Checks that entity with `entity_properties` exists in the Nx graph.
    Args:
        graph;
        entity_properties: Entity's Memgraph properties.
    """
    for *_, properties in graph_data:
        if properties == entity_properties:
            return True
    return False


def _check_nx_graph_structure(graph: nx.Graph, translator: NxTranslator):
    query_results = list(Match().node(variable="n").to(variable="r").node(variable="m").return_().execute())
    for row in query_results:
        row_values = row.values()
        for entity in row_values:
            if isinstance(entity, Node):
                entity._properties[LABEL] = Translator.merge_labels(entity._labels, translator.default_node_label)
                assert _check_entity_exists_in_nx(graph.nodes(data=True), entity._properties)
            elif isinstance(entity, Relationship):
                entity._properties[EDGE_TYPE] = entity._type if entity._type else translator.default_edge_type
                assert _check_entity_exists_in_nx(graph.edges(data=True), entity._properties)

def test_export_simple_graph():
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
    translator = NxTranslator()
    graph = translator.get_instance()
    assert graph.number_of_edges() == 8
    assert graph.number_of_nodes() == 4
    _check_nx_graph_structure(graph, translator)
    memgraph.drop_database()
