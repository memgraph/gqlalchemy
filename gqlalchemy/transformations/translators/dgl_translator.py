# Copyright (c) 2016-2023 Memgraph Ltd. [https://memgraph.com]
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

from typing import Union

import dgl
import torch

from gqlalchemy.transformations.translators.translator import Translator
from gqlalchemy.transformations.constants import DGL_ID
from gqlalchemy.utilities import to_cypher_value
from gqlalchemy.memgraph_constants import (
    MG_HOST,
    MG_PORT,
    MG_USERNAME,
    MG_PASSWORD,
    MG_ENCRYPTED,
    MG_CLIENT_NAME,
    MG_LAZY,
)


class DGLTranslator(Translator):
    """Performs conversion from cypher queries to the DGL graph representation. DGL assigns to each edge a unique integer, called the edge ID,
    based on the order in which it was added to the graph. In DGL, all the edges are directed, and an edge (u,v) indicates that the direction goes
    from node u to node v. Only features of numerical types (e.g., float, double, and int) are allowed. They can be scalars, vectors or multi-dimensional
    tensors (DGL requirement). Each node feature has a unique name and each edge feature has a unique name. The features of nodes and edges can have
    the same name. A feature is created via tensor assignment, which assigns a feature to each node/edge in the graph. The leading dimension of that
    tensor must be equal to the number of nodes/edges in the graph. You cannot assign a feature to a subset of the nodes/edges in the graph. Features of the
    same name must have the same dimensionality and data type.
    """

    def __init__(
        self,
        host: str = MG_HOST,
        port: int = MG_PORT,
        username: str = MG_USERNAME,
        password: str = MG_PASSWORD,
        encrypted: bool = MG_ENCRYPTED,
        client_name: str = MG_CLIENT_NAME,
        lazy: bool = MG_LAZY,
    ) -> None:
        super().__init__(host, port, username, password, encrypted, client_name, lazy)

    def to_cypher_queries(self, graph: Union[dgl.DGLGraph, dgl.DGLHeteroGraph]):
        """Produce cypher queries for data saved as part of the DGL graph. The method handles both homogeneous and heterogeneous graph. If the graph is homogeneous, a default DGL's labels will be used.
         _N as a node label and _E as edge label. The method converts 1D as well as multidimensional features. If there are some isolated nodes inside DGL graph, they won't get transferred. Nodes and edges
         created in Memgraph DB will, for the consistency reasons, have property `dgl_id` set to the id they have as part of the DGL graph. Note that this method doesn't insert anything inside the database,
         it just creates cypher queries. To insert queries the following code can be used:
         >>> memgraph = Memgraph()
         dgl_graph = DGLGraph(...)
         for query in DGLTranslator().to_cypher_queries(dgl_graph):
            memgraph.execute(query)

         Args:
            graph: A reference to the DGL graph.
        Returns:
            cypher queries.
        """
        queries = []
        if graph is None:
            return queries
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
                source_node_properties = dict(
                    map(
                        lambda pair: (pair[0], to_cypher_value(pair[1][source_node_id])),
                        node_src_label_properties.items(),
                    )
                )
                source_node_properties[DGL_ID] = int(source_node_id)
                # Copy destination node properties
                dest_node_properties = dict(
                    map(
                        lambda pair: (pair[0], to_cypher_value(pair[1][dest_node_id])),
                        node_dest_label_properties.items(),
                    )
                )
                dest_node_properties[DGL_ID] = int(dest_node_id)
                # Copy edge features
                edge_properties = dict(
                    map(lambda pair: (pair[0], to_cypher_value(pair[1][eid])), etype_properties.items())
                )
                edge_properties[DGL_ID] = int(eid)

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

    def get_instance(self) -> dgl.DGLHeteroGraph:
        """Create instance of DGL graph from all edges that are inside Memgraph. Currently, isolated nodes are ignored because they don't contribute in message passing neural networks. Only numerical features
        that are set on all nodes or all edges are transferred to the DGL instance since this is DGL's requirement. That means that any string values properties won't be transferred, as well as numerical properties
        that aren't set on all nodes. However, features of type list are transferred to the DGL and can be used as any other feature in the DGL graph. Regardless of data residing inside Memgraph database, the created
        DGL graph is a heterograph instance.
        Returns:
            DGL heterograph instance.
        """
        # Parse it into nice data structures
        src_nodes, dest_nodes, node_features, edge_features, _ = self._parse_memgraph()

        graph_data = {}
        # Iterating over src_nodes and dest_nodes should be the same
        for type_triplet in src_nodes.keys():
            graph_data[type_triplet] = (
                torch.tensor(src_nodes[type_triplet], dtype=torch.int32),
                torch.tensor(dest_nodes[type_triplet], dtype=torch.int32),
            )

        # Fail safely when graph is empty
        if len(graph_data) == 0:
            return None

        # Create heterograph
        graph = dgl.heterograph(graph_data)
        # Set node features
        for node_label, features_dict in node_features.items():
            for feature_name, features in features_dict.items():
                translated_features = Translator.validate_features(features, graph.num_nodes(node_label))
                if translated_features is None:
                    continue
                graph.nodes[node_label].data[feature_name] = translated_features

        # Set edge features
        for edge_triplet, features_dict in edge_features.items():
            for feature_name, features in features_dict.items():
                translated_features = Translator.validate_features(features, graph.num_edges(edge_triplet))
                if translated_features is None:
                    continue
                graph.edges[edge_triplet].data[feature_name] = translated_features

        return graph
