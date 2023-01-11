from constants import LABEL, EDGE_TYPE
from translators.translator import Translator
from gqlalchemy import Match
from gqlalchemy.models import Node, Relationship
import networkx as nx

# TODO: fix the import order


class NxTranslator(Translator):
    """Uses original ids from Memgraph. Labels are encoded as properties. Since Networkx allows
    that nodes have properties of different dimensionality, this modules makes use of it and stores properties
    as dictionary entries. All properties are saved to Networkx data structure.
    """

    # TODO: maybe we would like to have specific `weight` property for out users
    def __init__(self, default_node_label="NODE", default_edge_type="RELATIONSHIP") -> None:
        super().__init__(default_node_label, default_edge_type)

    def to_cypher_queries(self, graph):
        return super().to_cypher_queries()

    def get_instance(self):
        # Get all nodes and edges from the database
        query_results = Match().node(variable="n").to(variable="r").node(variable="m").return_().execute()

        # Data structures
        graph_data = []  # List[Tuple[source_node_id, dest_node_id]]
        node_info = dict()  # Dict[id, Dict[prop: value]]
        edge_info = dict()  # Dict[(source_node_id, dest_node_id), Dict[prop: value]]

        # Parse each row from query results
        for row in query_results:
            row_values = row.values()
            for entity in row_values:
                if isinstance(entity, Node) and entity._id not in node_info:
                    node_properties = {}  # TODO: extract node properties
                    node_properties[LABEL] = Translator.merge_labels(entity._labels, self.default_node_label)
                    node_info[entity._id] = node_properties
                elif isinstance(entity, Relationship):
                    edge_properties = {}  # TODO: extract edge properties
                    edge_properties[EDGE_TYPE] = entity._type if entity._type else self.default_edge_type
                    edge_info[(entity._start_node_id, entity._end_node_id)] = edge_properties
                    graph_data.append((entity._start_node_id, entity._end_node_id))

        # Create Nx graph
        graph = nx.Graph(graph_data)
        nx.set_node_attributes(graph, node_info)
        nx.set_edge_attributes(graph, edge_info)
        return graph
