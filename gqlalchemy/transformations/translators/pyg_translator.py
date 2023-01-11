from translators.translator import Translator
from torch_geometric.data import HeteroData, Data
from gqlalchemy import Match
import torch
from constants import EDGE_INDEX, PYG_ID, NUM_NODES


# TODO: Solve order import
class PyGTranslator(Translator):
    def __init__(self, default_node_label="NODE", default_edge_type="RELATIONSHIP") -> None:
        super().__init__(default_node_label, default_edge_type)

    def get_node_properties(graph, node_label, node_id):
        node_properties = {}
        for iter_node_label, iter_node_properties in graph.node_items():
            if iter_node_label == node_label:
                for property_name, property_values in iter_node_properties.items():
                    if property_name != NUM_NODES:
                        node_properties[property_name] = property_values[node_id]
        return node_properties

    def to_cypher_queries(self, graph):
        # For handling isolated nodes, you could make use of has_isolated_nodes
        # TODO: the question is how to handle specific named properties. We know that we can obtain x, y... everything directly but we need some kind
        # of reflection since we are working with stateless modules
        # TODO: check whether edge_attr, x and y need separate handling from custom features
        # Check whether the graph is homogeneous or heterogeneous
        # For hetero, process edge_items: from there you can get edge_features
        # Node features can be obtained from node items
        # For homogeneous, process directly edge_index. Obtain features from graph data
        queries = []
        if isinstance(graph, Data):
            # Get edges
            src_nodes, dest_nodes = graph.edge_index
            # Get graph data
            graph_data = graph.to_dict()
            graph_data.pop(EDGE_INDEX, None)
            node_properties, etype_properties = {}, {}
            for property_key, property_values in graph_data.items():
                if graph.is_node_attr(property_key):
                    node_properties[property_key] = property_values
                elif graph.is_edge_attr(property_key):
                    etype_properties[property_key] = property_values
            # Process edges
            eid = 0
            for src_node_id, dest_node_id in zip(src_nodes, dest_nodes):
                # Get node properties
                source_node_properties = Translator.get_properties(node_properties, src_node_id)
                dest_node_properties = Translator.get_properties(node_properties, dest_node_id)
                # Get edge properties
                edge_properties = Translator.get_properties(etype_properties, eid)
                eid += 1
                queries.append(
                    self.create_insert_query(
                        self.default_node_label,
                        source_node_properties,
                        self.default_edge_type,
                        edge_properties,
                        self.default_node_label,
                        dest_node_properties,
                    )
                )

        elif isinstance(graph, HeteroData):
            for etype, etype_features in graph.edge_items():
                print(f"Etype features: {etype_features}")
                source_node_label, edge_type, dest_node_label = etype
                # Get edges
                edge_index = etype_features[EDGE_INDEX]
                etype_features.pop(EDGE_INDEX, None)
                src_nodes, dest_nodes = edge_index[0], edge_index[1]
                eid = 0
                for src_node_id, dest_node_id in zip(src_nodes, dest_nodes):
                    # Get src node properties
                    source_node_properties = PyGTranslator.get_node_properties(graph, source_node_label, src_node_id)
                    source_node_properties[PYG_ID] = int(src_node_id)
                    # Destination node properties
                    dest_node_properties = PyGTranslator.get_node_properties(graph, dest_node_label, dest_node_id)
                    dest_node_properties[PYG_ID] = int(dest_node_id)
                    # Get edge features
                    edge_properties = Translator.get_properties(etype_features, eid)
                    eid += 1
                    # Create query
                    queries.append(
                        self.create_insert_query(
                            source_node_label,
                            source_node_properties,
                            edge_type,
                            edge_properties,
                            dest_node_label,
                            dest_node_properties,
                        )
                    )

        return queries

    def get_instance(self):
        # Get all nodes and edges from the database
        # TODO: needs testing, if it is node_attribute, if it is edge_attribute correctly set
        # TODO: specific handling of y values upon which the prediction is made
        # Knowledge: note and edge items don't save features
        query_results = Match().node(variable="n").to(variable="r").node(variable="m").return_().execute()

        # Parse it into nice data structures
        src_nodes, dest_nodes, node_features, edge_features, mem_indexes = self._parse_mem_graph(query_results)

        # Create PyG heterograph
        graph = HeteroData()

        # Create edges in COO format
        # TODO: research about COO format
        for type_triplet in src_nodes.keys():
            graph[type_triplet].edge_index = torch.tensor(
                [src_nodes[type_triplet], dest_nodes[type_triplet]], dtype=torch.int32
            )

        # Set node features
        for node_label, features_dict in node_features.items():
            for feature_name, features in features_dict.items():
                setattr(graph[node_label], feature_name, torch.tensor(features, dtype=torch.float32))

        # Set number of nodes, otherwise PyG inferes automatically and warnings can occur
        for node_label, num_nodes_label in mem_indexes.items():
            graph[node_label].num_nodes = num_nodes_label

        # Set edge features
        for edge_triplet, features_dict in edge_features.items():
            for feature_name, features in features_dict.items():
                setattr(graph[edge_triplet], feature_name, torch.tensor(features, dtype=torch.float32))

        # PyG offers a method to validate graph so if something is wrong an error will occur
        graph.validate(raise_on_error=True)
        return graph
