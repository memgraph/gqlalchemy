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

from torch_geometric.data import HeteroData, Data
import torch

from gqlalchemy.transformations.translators.translator import Translator
from gqlalchemy.transformations.constants import EDGE_INDEX, PYG_ID, NUM_NODES, DEFAULT_NODE_LABEL, DEFAULT_EDGE_TYPE
from gqlalchemy.memgraph_constants import (
    MG_HOST,
    MG_PORT,
    MG_USERNAME,
    MG_PASSWORD,
    MG_ENCRYPTED,
    MG_CLIENT_NAME,
    MG_LAZY,
)


class PyGTranslator(Translator):
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

    @classmethod
    def get_node_properties(cls, graph, node_label: str, node_id: int):
        """Extracts node properties from heterogeneous graph based on the node_label.
        Args:
            graph: A reference to the PyG graph.
            node_label: Node label
            node_id: Node_id
        """
        node_properties = {}
        for iter_node_label, iter_node_properties in graph.node_items():
            if iter_node_label != node_label:
                continue
            for property_name, property_values in iter_node_properties.items():
                if property_name == NUM_NODES:
                    continue
                node_properties[property_name] = property_values[node_id]
        return node_properties

    @classmethod
    def extract_node_edge_properties_from_homogeneous_graph(cls, graph):
        """Homogenous graph don't have node and etype properties so it is hard to extract node and edge attributes.
        Args:
            graph: Data = reference to the PyG graph.
        Returns:
            node and edge attributes as dictionaries
        """
        graph_data = graph.to_dict()
        graph_data.pop(EDGE_INDEX, None)
        node_properties = dict(filter(lambda pair: graph.is_node_attr(pair[0]), graph_data.items()))
        etype_properties = dict(filter(lambda pair: graph.is_edge_attr(pair[0]), graph_data.items()))
        return node_properties, etype_properties

    def to_cypher_queries(self, graph):
        """Produce cypher queries for data saved as part of thePyG graph. The method handles both homogeneous and heterogeneous graph.
        The method converts 1D as well as multidimensional features. If there are some isolated nodes inside the graph, they won't get transferred. Nodes and edges
         created in Memgraph DB will, for the consistency reasons, have property `pyg_id` set to the id they have as part of the PyG graph. Note that this method doesn't insert anything inside
         the database, it just creates cypher queries. To insert queries the following code can be used:
         >>> memgraph = Memgraph()
         pyg_graph = HeteroData(...)
         for query in PyGTranslator().to_cypher_queries(pyg_graph):
            memgraph.execute(query)

         Args:
            graph: A reference to the PyG graph.
        Returns:
            cypher queries.
        """
        queries = []
        if graph is None:
            return queries

        if isinstance(graph, HeteroData):
            for etype, etype_features in graph.edge_items():
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
                    edge_properties[PYG_ID] = eid
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
        elif isinstance(graph, Data):
            # Get edges
            src_nodes, dest_nodes = graph.edge_index
            # Get graph data
            node_properties, etype_properties = PyGTranslator.extract_node_edge_properties_from_homogeneous_graph(graph)
            # Process edges
            eid = 0
            for src_node_id, dest_node_id in zip(src_nodes, dest_nodes):
                # Get node properties
                source_node_properties = Translator.get_properties(node_properties, src_node_id)
                source_node_properties[PYG_ID] = int(src_node_id)
                dest_node_properties = Translator.get_properties(node_properties, dest_node_id)
                dest_node_properties[PYG_ID] = int(dest_node_id)
                edge_properties = Translator.get_properties(etype_properties, eid)
                edge_properties[PYG_ID] = eid
                eid += 1
                queries.append(
                    self.create_insert_query(
                        DEFAULT_NODE_LABEL,
                        source_node_properties,
                        DEFAULT_EDGE_TYPE,
                        edge_properties,
                        DEFAULT_NODE_LABEL,
                        dest_node_properties,
                    )
                )

        return queries

    def get_instance(self):
        """Create instance of PyG graph from all edges that are inside Memgraph. Currently, isolated nodes are ignored because they don't contribute in message passing neural networks. Only numerical features
        that are set on all nodes or all edges are transferred to the PyG instance since this is PyG's requirement. That means that any string values properties won't be transferred, as well as numerical properties
        that aren't set on all nodes. However, features that are of type list are transferred to the PyG instance and can be used as any other feature in the PyG graph. Regardless of data residing inside Memgraph database, the created
        PyG graph is a heterograph instance.
        Returns:
            PyG heterograph instance.
        """
        # Parse into nice data structures
        src_nodes, dest_nodes, node_features, edge_features, mem_indexes = self._parse_memgraph()

        # Create PyG heterograph
        graph = HeteroData()

        # Create edges in COO format
        for type_triplet in src_nodes.keys():
            graph[type_triplet].edge_index = torch.tensor(
                [src_nodes[type_triplet], dest_nodes[type_triplet]], dtype=torch.int32
            )

        # Set number of nodes, otherwise PyG infers automatically and warnings can occur
        for node_label, num_nodes_label in mem_indexes.items():
            graph[node_label].num_nodes = num_nodes_label

        # Set node features
        for node_label, features_dict in node_features.items():
            for feature_name, features in features_dict.items():
                features = Translator.validate_features(features, graph[node_label].num_nodes)
                if features is not None:
                    setattr(graph[node_label], feature_name, torch.tensor(features, dtype=torch.float32))

        # Set edge features
        for edge_triplet, features_dict in edge_features.items():
            for feature_name, features in features_dict.items():
                features = Translator.validate_features(features, graph[edge_triplet].num_edges)
                if features is not None:
                    setattr(graph[edge_triplet], feature_name, torch.tensor(features, dtype=torch.float32))

        # PyG offers a method to validate graph so if something is wrong an error will occur
        graph.validate(raise_on_error=True)
        return graph
