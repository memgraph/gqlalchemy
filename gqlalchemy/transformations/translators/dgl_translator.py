from typing import List

import dgl
import torch

from gqlalchemy.transformations.translators.translator import Translator
from gqlalchemy import Match
from gqlalchemy.transformations.constants import DGL_ID
from gqlalchemy.utilities import to_cypher_value


class DGLTranslator(Translator):
    """Performs conversion from cypher queries to the DGL graph representation. DGL assigns to each edge a unique integer, called the edge ID,
    based on the order in which it was added to the graph. In DGL, all the edges are directed, and an edge (u,v) indicates that the direction goes
    from node u to node v. Only features of numerical types (e.g., float, double, and int) are allowed. They can be scalars, vectors or multi-dimensional
    tensors (DQL requirement). Each node feature has a unique name and each edge feature has a unique name. The features of nodes and edges can have
    the same name. A feature is created via tensor assignment, which assigns a feature to each node/edge in the graph. The leading dimension of that
    tensor must be equal to the number of nodes/edges in the graph. You cannot assign a feature to a subset of the nodes/edges in the graph. Features of the
    same name must have the same dimensionality and data type.
    """

    def __init__(self, default_node_label="NODE", default_edge_type="RELATIONSHIP") -> None:
        super().__init__(default_node_label, default_edge_type)

    def to_cypher_queries(self, graph):
        """Produce cypher queries for data saved as part of the DGL graph. The method handles both homogeneous and heterogeneous graph. If the graph is homogeneous, a default DGL's labels will be used.
         _N as a node label and _E as edge label. The method converts 1D as well as multidimensional features. If there are some isolated nodes inside DGL graph, they won't get transferred. Nodes and edges
         created in Memgraph DB will, for the consistency reasons, have property `dgl_id` set to the id they have as part of the DGL graph. Note that this method doesn't insert anything inside the database,
         it just creates cypher queries. To insert queries the following code can be used:
         >>> memegraph = Memgraph()
         dgl_graph = DGLGraph(...)
         for query in DGLTranslator().to_cypher_queries(dgl_graph):
            memgraph.execute(query)

         Args:
            graph: A reference to the DGL graph.
        Returns:
            cypher queries.
        """
        queries = []
        for etype in graph.canonical_etypes:
            source_node_label, edge_type, dest_node_label = etype
            source_nodes, dest_nodes, eids = graph.edges(etype=etype, form="all")
            # Get label and type properties
            node_src_label_properties = graph.nodes[source_node_label].data
            node_dest_label_properties = graph.nodes[dest_node_label].data
            etype_properties = graph.edges[etype].data
            for source_node_id, dest_node_id, eid in zip(source_nodes, dest_nodes, eids):
                # Handle properties
                source_node_properties, dest_node_properties, edge_properties = {}, {}, {}
                # Copy source node properties
                source_node_properties[DGL_ID] = int(source_node_id)
                for property_name, property_value in node_src_label_properties.items():
                    source_node_properties[property_name] = to_cypher_value(property_value[source_node_id])
                # Copy destination node properties
                dest_node_properties[DGL_ID] = int(dest_node_id)
                for property_name, property_value in node_dest_label_properties.items():
                    dest_node_properties[property_name] = to_cypher_value(property_value[dest_node_id])
                # Copy edge features
                edge_properties[DGL_ID] = int(eid)
                for property_name, property_value in etype_properties.items():
                    edge_properties[property_name] = to_cypher_value(property_value[eid])

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
        """Create instance of DGL graph from all edges that are inside Memgraph. Currently, isolated nodes are ignored because they don't contribute in message passing neural networks. Only numerical features
        that are set on all nodes or all edges are transferred to the DGL instance since this is DGL's requirement. That means thay any string values properties won't be transferred, as well as numerical properties
        that aren't set on all nodes. However, features of type list are transferred to the DGL and can be used as any other feature in the DGL graph. Regardless of data residing inside Memgraph database, the created
        DGL graph is a heterograph instance.
        Returns:
            DGL heterograph instance.
        """
        # Get all nodes and edges from the database
        query_results = Match().node(variable="n").to(variable="r").node(variable="m").return_().execute()

        # Parse it into nice data structures
        src_nodes, dest_nodes, node_features, edge_features, _ = self._parse_mem_graph(query_results)

        graph_data = {}
        # Iterating over src_nodes and dest_nodes should be the same
        for type_triplet in src_nodes.keys():
            graph_data[type_triplet] = (
                torch.tensor(src_nodes[type_triplet], dtype=torch.int32),
                torch.tensor(dest_nodes[type_triplet], dtype=torch.int32),
            )

        # Create heterograph
        graph = dgl.heterograph(graph_data)
        # Set node features
        for node_label, features_dict in node_features.items():
            for feature_name, features in features_dict.items():
                features = Translator.validate_features(features, graph.num_nodes(node_label))
                if not features is None:
                    graph.nodes[node_label].data[feature_name] = features

        # Set edge features
        for edge_triplet, features_dict in edge_features.items():
            for feature_name, features in features_dict.items():
                features = Translator.validate_features(features, graph.num_edges(edge_triplet))
                if not features is None:
                    graph.edges[edge_triplet].data[feature_name] = features

        return graph

