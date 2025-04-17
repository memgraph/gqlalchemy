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

from typing import Any, Dict, List, Optional, Union

from gqlalchemy.query_builders.declarative_base import DeclarativeBase
from gqlalchemy.query_builders.memgraph_query_builder import QueryBuilder
from gqlalchemy.vendors.memgraph import Connection, Memgraph


class MemgraphQueryBuilder(QueryBuilder):
    """
    This query builder extends the usual Cypher query builder capabilities with Memgraph's query modules.
    User gets with this module autocomplete features of graph algorithms.
    Documentation on the methods can be found on Memgraph's web page.
    """

    def __init__(self, connection: Optional[Union[Connection, Memgraph]] = None):
        super().__init__(connection)

    def example_c_procedure(self, required_arg: Any, optional_arg=None) -> DeclarativeBase:
        return self.call("example.procedure", (required_arg, optional_arg))

    def example_c_write_procedure(self, required_arg: str) -> DeclarativeBase:
        return self.call("example.write_procedure", (required_arg))

    def graph_analyzer_analyze(self, analyses: Optional[List[str]] = None) -> DeclarativeBase:
        return self.call("graph_analyzer.analyze", (analyses))

    def graph_analyzer_analyze_subgraph(
        self, vertices: List[Any], edges: List[Any], analyses: Optional[List[str]] = None
    ) -> DeclarativeBase:
        return self.call("graph_analyzer.analyze_subgraph", (vertices, edges, analyses))

    def graph_analyzer_help(self, name: str, value: str) -> DeclarativeBase:
        return self.call("graph_analyzer.help", (name, value))

    def mg_create_module_file(self, filename: str, content: str) -> DeclarativeBase:
        return self.call("mg.create_module_file", (filename, content))

    def mg_delete_module_file(self, path: str) -> DeclarativeBase:
        return self.call("mg.delete_module_file", (path))

    def mg_functions(self) -> DeclarativeBase:
        return self.call("mg.functions")

    def mg_get_module_file(self, path: str) -> DeclarativeBase:
        return self.call("mg.get_module_file", (path))

    def mg_get_module_files(self, is_editable: bool, path: str) -> DeclarativeBase:
        return self.call("mg.get_module_files", (is_editable, path))

    def mg_kafka_set_stream_offset(self, stream_name: str, offset: int) -> DeclarativeBase:
        return self.call("mg.kafka_set_stream_offset", (stream_name, offset))

    def mg_kafka_stream_info(self, stream_name: str) -> DeclarativeBase:
        return self.call("mg.kafka_stream_info", (stream_name))

    def mg_load(self, module_name: str) -> DeclarativeBase:
        return self.call("mg.load", (module_name))

    def mg_load_all(self) -> DeclarativeBase:
        return self.call("mg.load_all")

    def mg_procedures(self) -> DeclarativeBase:
        return self.call("mg.procedures")

    def mg_pulsar_stream_info(self, stream_name: str) -> DeclarativeBase:
        return self.call("mg.procedures", (stream_name))

    def mg_transformations(self) -> DeclarativeBase:
        return self.call("mg.transformations")

    def mg_update_module_file(self, path: str, content: str) -> DeclarativeBase:
        return self.call("mg.update_module_file", (path, content))

    def nxalg_all_shortest_paths(
        self, source: Any, target: Any, weight: Optional[str] = None, method: str = "dijkstra"
    ) -> DeclarativeBase:
        return self.call("nxalg.all_shortest_paths", (source, target, weight, method))

    def nxalg_all_simple_paths(self, source: Any, target: Any, cutoff: Optional[int] = None) -> DeclarativeBase:
        return self.call("nxalg.all_simple_paths", (source, target, cutoff))

    def nxalg_ancestors(self, source: Any) -> DeclarativeBase:
        return self.call("nxalg.all_simple_paths", (source))

    def nxalg_betweenness_centrality(
        self,
        k: Optional[int] = None,
        normalized: bool = True,
        weight: Optional[str] = None,
        endpoints: bool = False,
        seed: Optional[int] = None,
    ) -> DeclarativeBase:
        return self.call("nxalg.betweenness_centrality", (k, normalized, weight, endpoints, seed))

    def nxalg_bfs_edges(self, source: Any, reverse: bool = False, depth_limit: Optional[int] = None) -> DeclarativeBase:
        return self.call("nxalg.bfs_edges", (source, reverse, depth_limit))

    def nxalg_bfs_predecessors(self, source: Any, depth_limit: Optional[int] = None) -> DeclarativeBase:
        return self.call("nxalg.bfs_predecessors", (source, depth_limit))

    def nxalg_bfs_successors(self, source: Any, depth_limit: Optional[int] = None) -> DeclarativeBase:
        return self.call("nxalg.bfs_successors", (source, depth_limit))

    def nxalg_bfs_tree(self, source: Any, reverse: bool = False, depth_limit: Optional[int] = None) -> DeclarativeBase:
        return self.call("nxalg.bfs_tree", (source, reverse, depth_limit))

    def nxalg_biconnected_components(self) -> DeclarativeBase:
        return self.call("nxalg.biconnected_components")

    def nxalg_bridges(self, root: Any) -> DeclarativeBase:
        return self.call("nxalg.bridges", (root))

    def nxalg_center(self) -> DeclarativeBase:
        return self.call("nxalg.center")

    def nxalg_chain_decomposition(self, root: Any) -> DeclarativeBase:
        return self.call("nxalg.chain_decomposition", (root))

    def nxalg_check_planarity(self) -> DeclarativeBase:
        return self.call("nxalg.check_planarity")

    def nxalg_clustering(self, nodes: Optional[List[Any]] = None, weight: Optional[str] = None) -> DeclarativeBase:
        return self.call("nxalg.clustering", (nodes, weight))

    def nxalg_communicability(self) -> DeclarativeBase:
        return self.call("nxalg.communicability")

    def nxalg_core_number(self) -> DeclarativeBase:
        return self.call("nxalg.core_number")

    def nxalg_degree_assortativity_coefficient(
        self, x: str = "out", y: str = "in", weight: Optional[str] = None, nodes: Optional[List[Any]] = None
    ) -> DeclarativeBase:
        return self.call("nxalg.degree_assortativity_coefficient", (x, y, weight, nodes))

    def nxalg_descendants(self, source: Any) -> DeclarativeBase:
        return self.call("nxalg.descendants", (source))

    def nxalg_dfs_postorder_nodes(self, source: Any, depth_limit: Optional[int] = None) -> DeclarativeBase:
        return self.call("nxalg.dfs_postorder_nodes", (source, depth_limit))

    def nxalg_dfs_predecessors(self, source: Any, depth_limit: Optional[int] = None) -> DeclarativeBase:
        return self.call("nxalg.dfs_predecessors", (source, depth_limit))

    def nxalg_dfs_preorder_nodes(self, source: Any, depth_limit: Optional[int] = None) -> DeclarativeBase:
        return self.call("nxalg.dfs_preorder_nodes", (source, depth_limit))

    def nxalg_dfs_successors(self, source: Any, depth_limit: Optional[int] = None) -> DeclarativeBase:
        return self.call("nxalg.dfs_successors", (source, depth_limit))

    def nxalg_dfs_tree(self, source: Any, depth_limit: Optional[int] = None) -> DeclarativeBase:
        return self.call("nxalg.dfs_tree", (source, depth_limit))

    def nxalg_diameter(self) -> DeclarativeBase:
        return self.call("nxalg.diameter")

    def nxalg_dominance_frontiers(self, start: Any) -> DeclarativeBase:
        return self.call("nxalg.dominance_frontiers", (start))

    def nxalg_dominating_set(self, start: Any) -> DeclarativeBase:
        return self.call("nxalg.dominance_frontiers", (start))

    def nxalg_edge_bfs(self, source: Optional[Any], orientation: Optional[str] = None) -> DeclarativeBase:
        return self.call("nxalg.edge_bfs", (source, orientation))

    def nxalg_edge_dfs(self, source: Optional[Any], orientation: Optional[str] = None) -> DeclarativeBase:
        return self.call("nxalg.edge_dfs", (source, orientation))

    def nxalg_find_cliques(self) -> DeclarativeBase:
        return self.call("nxalg.find_cliques")

    def nxalg_find_cycle(
        self, source: Optional[List[Any]] = None, orientation: Optional[str] = None
    ) -> DeclarativeBase:
        return self.call("nxalg.find_cycle", (source, orientation))

    def nxalg_flow_hierarchy(self, weight: Optional[str] = None) -> DeclarativeBase:
        return self.call("nxalg.flow_hierarchy", (weight))

    def nxalg_global_efficiency(self) -> DeclarativeBase:
        return self.call("nxalg.global_efficiency")

    def nxalg_greedy_color(self, strategy: str = "largest_first", interchange: bool = False) -> DeclarativeBase:
        return self.call("nxalg.greedy_color", (strategy, interchange))

    def nxalg_has_eulerian_path(self) -> DeclarativeBase:
        return self.call("nxalg.has_eulerian_path")

    def nxalg_has_path(self, source: Any, target: Any) -> DeclarativeBase:
        return self.call("nxalg.has_path", (source, target))

    def nxalg_immediate_dominators(self, start: Any) -> DeclarativeBase:
        return self.call("nxalg.immediate_dominators", (start))

    def nxalg_is_arborescence(self) -> DeclarativeBase:
        return self.call("nxalg.is_arborescence")

    def nxalg_is_at_free(self) -> DeclarativeBase:
        return self.call("nxalg.is_at_free")

    def nxalg_is_bipartite(self) -> DeclarativeBase:
        return self.call("nxalg.is_bipartite")

    def nxalg_is_branching(self) -> DeclarativeBase:
        return self.call("nxalg.is_branching")

    def nxalg_is_chordal(self) -> DeclarativeBase:
        return self.call("nxalg.is_chordal")

    def nxalg_is_distance_regular(self) -> DeclarativeBase:
        return self.call("nxalg.is_distance_regular")

    def nxalg_is_edge_cover(self, cover: List[Any]) -> DeclarativeBase:
        return self.call("nxalg.is_edge_cover", (cover))

    def nxalg_is_eulerian(self) -> DeclarativeBase:
        return self.call("nxalg.is_eulerian")

    def nxalg_is_forest(self) -> DeclarativeBase:
        return self.call("nxalg.is_forest")

    def nxalg_is_isolate(self, n: Any) -> DeclarativeBase:
        return self.call("nxalg.is_isolate", (n))

    def nxalg_is_isomorphic(
        self, nodes1: List[Any], edges1: List[Any], nodes2: List[Any], edges2: List[Any]
    ) -> DeclarativeBase:
        return self.call("nxalg.is_isomorphic", (nodes1, edges1, nodes2, edges2))

    def nxalg_is_semieulerian(self) -> DeclarativeBase:
        return self.call("nxalg.is_semieulerian")

    def nxalg_is_simple_path(self, nodes: List[Any]) -> DeclarativeBase:
        return self.call("nxalg.is_simple_path", (nodes))

    def nxalg_is_strongly_regular(self) -> DeclarativeBase:
        return self.call("nxalg.is_strongly_regular")

    def nxalg_is_tournament(self) -> DeclarativeBase:
        return self.call("nxalg.is_tournament")

    def nxalg_is_tree(self) -> DeclarativeBase:
        return self.call("nxalg.is_tree")

    def nxalg_isolates(self) -> DeclarativeBase:
        return self.call("nxalg.isolates")

    def nxalg_jaccard_coefficient(self, ebunch: Optional[List[Any]] = None) -> DeclarativeBase:
        return self.call("nxalg.jaccard_coefficient", (ebunch))

    def nxalg_k_clique_communities(self, k: int, cliques: List[List[Any]] = None) -> DeclarativeBase:
        return self.call("nxalg.k_clique_communities", (k, cliques))

    def nxalg_k_components(self, density: float = 0.95) -> DeclarativeBase:
        return self.call("nxalg.k_components", (density))

    def nxalg_k_edge_components(self, k: int) -> DeclarativeBase:
        return self.call("nxalg.k_edge_components", (k))

    def nxalg_local_efficiency(self) -> DeclarativeBase:
        return self.call("nxalg.local_efficiency")

    def nxalg_lowest_common_ancestor(self, node1: Any, node2: Any) -> DeclarativeBase:
        return self.call("nxalg.lowest_common_ancestor", (node1, node2))

    def nxalg_maximal_matching(self) -> DeclarativeBase:
        return self.call("nxalg.maximal_matching")

    def nxalg_minimum_spanning_tree(
        self, weight: str = "weight", algorithm: str = "kruskal", ignore_nan: bool = False
    ) -> DeclarativeBase:
        return self.call("nxalg.minimum_spanning_tree", (weight, algorithm, ignore_nan))

    def nxalg_multi_source_dijkstra_path(
        self, sources: List[Any], cutoff: Optional[int] = None, weight: str = "weight"
    ) -> DeclarativeBase:
        return self.call("nxalg.multi_source_dijkstra_path", (sources, cutoff, weight))

    def nxalg_multi_source_dijkstra_path_length(
        self, sources: List[Any], cutoff: Optional[int] = None, weight: str = "weight"
    ) -> DeclarativeBase:
        return self.call("nxalg.multi_source_dijkstra_path_length", (sources, cutoff, weight))

    def nxalg_node_boundary(self, nbunch1: List[Any], nbunch2: List[Any] = None) -> DeclarativeBase:
        return self.call("nxalg.node_boundary", (nbunch1, nbunch2))

    def nxalg_node_connectivity(self, source: List[Any] = None, target: List[Any] = None) -> DeclarativeBase:
        return self.call("nxalg.node_connectivity", (source, target))

    def nxalg_node_expansion(self, s: List[Any]) -> DeclarativeBase:
        return self.call("nxalg.node_expansion", (s))

    def nxalg_non_randomness(self, k: Optional[int] = None) -> DeclarativeBase:
        return self.call("nxalg.non_randomness", (k))

    def nxalg_pagerank(
        self,
        alpha: float = 0.85,
        personalization: Optional[str] = None,
        max_iter: int = 100,
        tol: float = 1e-06,
        nstart: Optional[str] = None,
        weight: Optional[str] = "weight",
        dangling: Optional[str] = None,
    ) -> DeclarativeBase:
        return self.call("nxalg.pagerank", (alpha, personalization, max_iter, tol, nstart, weight, dangling))

    def nxalg_reciprocity(self, nodes: List[Any] = None) -> DeclarativeBase:
        return self.call("nxalg.reciprocity", (nodes))

    def nxalg_shortest_path(
        self,
        source: Optional[Any] = None,
        target: Optional[Any] = None,
        weight: Optional[str] = None,
        method: str = "dijkstra",
    ) -> DeclarativeBase:
        return self.call("nxalg.shortest_path", (source, target, weight, method))

    def nxalg_shortest_path_length(
        self,
        source: Optional[Any] = None,
        target: Optional[Any] = None,
        weight: Optional[str] = None,
        method: str = "dijkstra",
    ) -> DeclarativeBase:
        return self.call("nxalg.shortest_path_length", (source, target, weight, method))

    def nxalg_simple_cycles(self) -> DeclarativeBase:
        return self.call("nxalg.simple_cycles")

    def nxalg_strongly_connected_components(self) -> DeclarativeBase:
        return self.call("nxalg.strongly_connected_components")

    def nxalg_topological_sort(self) -> DeclarativeBase:
        return self.call("nxalg.topological_sort")

    def nxalg_triadic_census(self) -> DeclarativeBase:
        return self.call("nxalg.triadic_census")

    def nxalg_voronoi_cells(self, center_nodes: List[Any], weight: str = "weight") -> DeclarativeBase:
        return self.call("nxalg.voronoi_cells", (center_nodes, weight))

    def nxalg_wiener_index(self, weight: Optional[str] = None) -> DeclarativeBase:
        return self.call("nxalg.wiener_index", (weight))

    def py_example_procedure(self, required_arg: Optional[Any], optional_arg: Optional[Any] = None) -> DeclarativeBase:
        return self.call("py_example.procedure", (required_arg, optional_arg))

    def py_example_write_procedure(self, property_name: str, property_value: Optional[Any]) -> DeclarativeBase:
        return self.call("py_example.write_procedure", (property_name, property_value))

    def wcc_get_components(self, vertices: List[Any], edges: List[Any]) -> DeclarativeBase:
        return self.call("wcc.get_components", (vertices, edges))


class MageQueryBuilder(MemgraphQueryBuilder):
    """
    This query builder extends the Memgraph query builder with Memgraph MAGE graph algorithm Cypher options.
    User gets with this module autocomplete features of graph algorithms written in MAGE library.
    Documentation on the methods can be found on Memgraph's web page.
    """

    def __init__(self, connection: Optional[Union[Connection, Memgraph]] = None):
        super().__init__(connection)

    def algo_all_simple_paths(
        self, start_node: Any, end_node: Any, relationship_types: List[str], max_length: int
    ) -> DeclarativeBase:
        return self.call("algo.all_simple_paths", (start_node, end_node, relationship_types, max_length))

    def algo_astar(self, start: Any, target: Any, config: dict) -> DeclarativeBase:
        return self.call("algo.astar", (start, target, config))

    def algo_cover(self, nodes: List[Any]) -> DeclarativeBase:
        return self.call("algo.cover", (nodes))

    def betweenness_centrality_get(
        self, directed: bool = True, normalized: bool = True, threads: int = 8
    ) -> DeclarativeBase:
        return self.call("betweenness_centrality.get", (directed, normalized, threads))

    def betweenness_centrality_online_get(self, normalize: bool = True) -> DeclarativeBase:
        return self.call("betweenness_centrality_online.get", (normalize))

    def betweenness_centrality_online_reset(self) -> DeclarativeBase:
        return self.call("betweenness_centrality_online.reset")

    def betweenness_centrality_online_set(self, normalize: bool = True, threads: int = 8) -> DeclarativeBase:
        return self.call("betweenness_centrality_online.set", (normalize, threads))

    def betweenness_centrality_online_update(
        self,
        created_vertices: List[Any] = [],
        created_edges: List[Any] = [],
        deleted_vertices: List[Any] = [],
        deleted_edges: List[Any] = [],
        normalize: bool = True,
        threads: int = 8,
    ) -> DeclarativeBase:
        return self.call(
            "betweenness_centrality_online.update",
            (created_vertices, created_edges, deleted_vertices, deleted_edges, normalize, threads),
        )

    def biconnected_components_get(self) -> DeclarativeBase:
        return self.call("biconnected_components.get")

    def bipartite_matching_max(self) -> DeclarativeBase:
        return self.call("bipartite_matching.max")

    def bridges_get(self) -> DeclarativeBase:
        return self.call("bridges.get")

    def collections_partition(self, list: List[Any], partition_size: int) -> DeclarativeBase:
        return self.call("collections.partition", (list, partition_size))

    def collections_split(self, coll: List[Any], delimiter: Any) -> DeclarativeBase:
        return self.call("collections.split", (coll, delimiter))

    def community_detection_get(
        self,
        weight: str = "weight",
        coloring: bool = False,
        min_graph_shrink: int = 100000,
        community_alg_threshold: float = 1e-06,
        coloring_alg_threshold: float = 0.01,
    ) -> DeclarativeBase:
        return self.call(
            "community_detection.get",
            (weight, coloring, min_graph_shrink, community_alg_threshold, coloring_alg_threshold),
        )

    def community_detection_get_subgraph(
        self,
        subgraph_nodes: List[Any],
        subgraph_relationships: List[Any],
        weight: str,
        coloring: bool,
        min_graph_shrink: int,
        community_alg_threshold: float,
        coloring_alg_threshold: float,
    ) -> DeclarativeBase:
        return self.call(
            "community_detection.get_subgraph",
            (
                subgraph_nodes,
                subgraph_relationships,
                weight,
                coloring,
                min_graph_shrink,
                community_alg_threshold,
                coloring_alg_threshold,
            ),
        )

    def community_detection_online_get(self) -> DeclarativeBase:
        return self.call("community_detection_online.get")

    def community_detection_online_reset(self) -> DeclarativeBase:
        return self.call("community_detection_online.reset")

    def community_detection_online_set(
        self,
        directed: bool = False,
        weighted: bool = False,
        similarity_threshold: float = 0.7,
        exponent: float = 4,
        min_value: float = 0.1,
        weight_property: str = "weight",
        w_selfloop: float = 1.0,
        max_iterations: int = 100,
        max_updates: int = 5,
    ) -> DeclarativeBase:
        return self.call(
            "community_detection_online.set",
            (
                directed,
                weighted,
                similarity_threshold,
                exponent,
                min_value,
                weight_property,
                w_selfloop,
                max_iterations,
                max_updates,
            ),
        )

    def community_detection_online_update(
        self,
        createdVertices: List[Any] = [],
        createdEdges: List[Any] = [],
        updatedVertices: List[Any] = [],
        updatedEdges: List[Any] = [],
        deletedVertices: List[Any] = [],
        deletedEdges: List[Any] = [],
    ) -> DeclarativeBase:
        return self.call(
            "community_detection_online.update",
            (createdVertices, createdEdges, updatedVertices, updatedEdges, deletedVertices, deletedEdges),
        )

    def create_node(self, label: List[str], props: dict) -> DeclarativeBase:
        return self.call("create.node", (label, props))

    def create_nodes(self, label: List[str], props: List[dict]) -> DeclarativeBase:
        return self.call("create.nodes", (label, props))

    def create_relationship(self, from_: Any, relationshipType: str, properties: dict, to: Any) -> DeclarativeBase:
        return self.call("create.relationship", (from_, relationshipType, properties, to))

    def create_remove_labels(self, nodes: Any, label: List[str]) -> DeclarativeBase:
        return self.call("create.remove_labels", (nodes, label))

    def create_remove_properties(self, nodes: Any, keys: List[str]) -> DeclarativeBase:
        return self.call("create.remove_properties", (nodes, keys))

    def create_remove_rel_properties(self, relationships: Any, keys: List[str]) -> DeclarativeBase:
        return self.call("create.remove_rel_properties", (relationships, keys))

    def create_set_properties(
        self, input_nodes: Any, input_keys: List[str], input_values: List[Any]
    ) -> DeclarativeBase:
        return self.call("create.set_properties", (input_nodes, input_keys, input_values))

    def create_set_property(self, nodes: Any, key: str, value: Any) -> DeclarativeBase:
        return self.call("create.set_property", (nodes, key, value))

    def create_set_rel_properties(self, relationships: Any, keys: List[str], values: List[Any]) -> DeclarativeBase:
        return self.call("create.set_rel_properties", (relationships, keys, values))

    def create_set_rel_property(self, input_rel: Any, input_key: str, input_value: Any) -> DeclarativeBase:
        return self.call("create.set_rel_property", (input_rel, input_key, input_value))

    def csv_utils_create_csv_file(self, filepath: str, content: str, is_append: bool) -> DeclarativeBase:
        return self.call("csv_utils.create_csv_file", (filepath, content, is_append))

    def csv_utils_delete_csv_file(self, filepath: str) -> DeclarativeBase:
        return self.call("csv_utils.delete_csv_file", (filepath))

    def cycles_get(self) -> DeclarativeBase:
        return self.call("cycles.get")

    def date_format(self, time: int, unit: str, format: str, timezone: str) -> DeclarativeBase:
        return self.call("date.format", (time, unit, format, timezone))

    def date_parse(self, time: str, unit: str, format: str, timezone: str) -> DeclarativeBase:
        return self.call("date.parse", (time, unit, format, timezone))

    def degree_centrality_get(self, type: str) -> DeclarativeBase:
        return self.call("degree_centrality.get", (type))

    def degree_centrality_get_subgraph(
        self, subgraph_nodes: List[Any], subgraph_relationships: List[Any], type: Optional[str]
    ) -> DeclarativeBase:
        return self.call("degree_centrality.get_subgraph", (subgraph_nodes, subgraph_relationships, type))

    def distance_calculator_multiple(
        self, start_points: List[Any], end_points: List[Any], metrics: str = "m"
    ) -> DeclarativeBase:
        return self.call("distance_calculator.multiple", (start_points, end_points, metrics))

    def distance_calculator_single(
        self, start: Optional[Any], end: Optional[Any], metrics: str = "m"
    ) -> DeclarativeBase:
        return self.call("distance_calculator.single", (start, end, metrics))

    def do_case(self, conditionals: List[Any], else_query: str, params: dict) -> DeclarativeBase:
        return self.call("do.case", (conditionals, else_query, params))

    def do_when(self, condition: bool, if_query: str, else_query: str, params: dict) -> DeclarativeBase:
        return self.call("do.when", (condition, if_query, else_query, params))

    def elastic_search_serialization_connect(
        self, elastic_url: str, ca_certs: str, elastic_user: str, elastic_password: Optional[Any]
    ) -> DeclarativeBase:
        return self.call(
            "elastic_search_serialization.connect", (elastic_url, ca_certs, elastic_user, elastic_password)
        )

    def elastic_search_serialization_create_index(
        self, index_name: str, schema_path: str, schema_parameters: dict
    ) -> DeclarativeBase:
        return self.call("elastic_search_serialization.create_index", (index_name, schema_path, schema_parameters))

    def elastic_search_serialization_index(
        self,
        createdObjects: List[dict],
        node_index: str,
        edge_index: str,
        thread_count: int,
        chunk_size: int,
        max_chunk_bytes: int,
        raise_on_error: bool,
        raise_on_exception: bool,
        max_retries: int,
        initial_backoff: float,
        max_backoff: float,
        yield_ok: bool,
        queue_size: int,
    ) -> DeclarativeBase:
        return self.call(
            "elastic_search_serialization.index",
            (
                createdObjects,
                node_index,
                edge_index,
                thread_count,
                chunk_size,
                max_chunk_bytes,
                raise_on_error,
                raise_on_exception,
                max_retries,
                initial_backoff,
                max_backoff,
                yield_ok,
                queue_size,
            ),
        )

    def elastic_search_serialization_index_db(
        self,
        node_index: str,
        edge_index: str,
        thread_count: int,
        chunk_size: int,
        max_chunk_bytes: int,
        raise_on_error: bool,
        raise_on_exception: bool,
        max_retries: int,
        initial_backoff: float,
        max_backoff: float,
        yield_ok: bool,
        queue_size: int,
    ) -> DeclarativeBase:
        return self.call(
            "elastic_search_serialization.index_db",
            (
                node_index,
                edge_index,
                thread_count,
                chunk_size,
                max_chunk_bytes,
                raise_on_error,
                raise_on_exception,
                max_retries,
                initial_backoff,
                max_backoff,
                yield_ok,
                queue_size,
            ),
        )

    def elastic_search_serialization_reindex(
        self, source_index: Any, target_index: str, query: str, chunk_size: int, scroll: str, op_type: Optional[str]
    ) -> DeclarativeBase:
        return self.call(
            "elastic_search_serialization.reindex", (source_index, target_index, query, chunk_size, scroll, op_type)
        )

    def elastic_search_serialization_scan(
        self,
        index_name: str,
        query: str,
        scroll: str,
        raise_on_error: bool,
        preserve_order: bool,
        size: int,
        from_: int,
        request_timeout: Optional[float],
        clear_scroll: bool,
    ) -> DeclarativeBase:
        return self.call(
            "elastic_search_serialization.scan",
            (index_name, query, scroll, raise_on_error, preserve_order, size, from_, request_timeout, clear_scroll),
        )

    def elastic_search_serialization_search(
        self, index_name: str, query: str, size: int, from_: int, aggregations: Optional[dict], aggs: Optional[dict]
    ) -> DeclarativeBase:
        return self.call("elastic_search_serialization.search", (index_name, query, size, from_, aggregations, aggs))

    def example_c_procedure(self, required_arg: Optional[Any], optional_arg: Optional[Any]) -> DeclarativeBase:
        return self.call("example_c.procedure", (required_arg, optional_arg))

    def example_c_write_procedure(self, required_arg: str) -> DeclarativeBase:
        return self.call("example_c.write_procedure", (required_arg))

    def example_cpp_add_x_nodes(self, param_1: int) -> DeclarativeBase:
        return self.call("example_cpp.add_x_nodes", (param_1))

    def example_cpp_return_true(self, param_1: int, param_2: float) -> DeclarativeBase:
        return self.call("example_cpp.return_true", (param_1, param_2))

    def export_util_csv_graph(
        self, nodes_list: List[Any], relationships_list: List[Any], path: str, config: map
    ) -> DeclarativeBase:
        return self.call("export_util.csv_graph", (nodes_list, relationships_list, path, config))

    def export_util_csv_query(self, query: str, file_path: str, stream: bool) -> DeclarativeBase:
        return self.call("export_util.csv_query", (query, file_path, stream))

    def export_util_cypher_all(self, path: str, config: dict) -> DeclarativeBase:
        return self.call("export_util.cypher_all", (path, config))

    def export_util_graphml(self, path: str, config: Optional[dict]) -> DeclarativeBase:
        return self.call("export_util.graphml", (path, config))

    def export_util_json(self, path: str) -> DeclarativeBase:
        return self.call("export_util.json", (path))

    def export_util_json_graph(
        self, nodes: Optional[List[Any]], relationships: Optional[List[Any]], path: str, config: dict
    ) -> DeclarativeBase:
        return self.call("export_util.json_graph", (nodes, relationships, path, config))

    def graph_coloring_color_graph(
        self, parameters: Dict[str, Union[str, int]], edge_property: str = "weight"
    ) -> DeclarativeBase:
        return self.call("graph_coloring.color_graph", (parameters, edge_property))

    def graph_coloring_color_subgraph(
        self,
        vertices: List[Any],
        edges: List[Any],
        parameters: Dict[str, Union[str, int]],
        edge_property: str = "weight",
    ) -> DeclarativeBase:
        return self.call("graph_coloring.color_subgraph", (vertices, edges, parameters, edge_property))

    def graph_util_ancestors(self, node: Any) -> DeclarativeBase:
        return self.call("graph_util.ancestors", (node))

    def graph_util_chain_nodes(self, nodes: List[Any], edge_type: str) -> DeclarativeBase:
        return self.call("graph_util.chain_nodes", (nodes, edge_type))

    def graph_util_connect_nodes(self, nodes: List[Any]) -> DeclarativeBase:
        return self.call("graph_util.connect_nodes", (nodes))

    def graph_util_descendants(self, node: Any) -> DeclarativeBase:
        return self.call("graph_util.descendants", (node))

    def graph_util_topological_sort(self) -> DeclarativeBase:
        return self.call("graph_util.topological_sort")

    def igraphalg_all_shortest_path_lengths(self, weights: Optional[str], directed: bool) -> DeclarativeBase:
        return self.call("igraphalg.all_shortest_path_lengths", (weights, directed))

    def igraphalg_community_leiden(
        self,
        objective_function: str,
        weights: Optional[str],
        resolution_parameter: float,
        beta: float,
        initial_membership: Optional[List[int]],
        n_iterations: int,
        node_weights: Optional[List[float]],
    ) -> DeclarativeBase:
        return self.call(
            "igraphalg.community_leiden",
            (objective_function, weights, resolution_parameter, beta, initial_membership, n_iterations, node_weights),
        )

    def igraphalg_get_all_simple_paths(self, v: Any, to: Any, cutoff: int) -> DeclarativeBase:
        return self.call("igraphalg.get_all_simple_paths", (v, to, cutoff))

    def igraphalg_get_shortest_path(
        self, source: Any, target: Any, weights: Optional[str], directed: bool
    ) -> DeclarativeBase:
        return self.call("igraphalg.get_shortest_path", (source, target, weights, directed))

    def igraphalg_maxflow(self, source: Any, target: Any, capacity: str) -> DeclarativeBase:
        return self.call("igraphalg.maxflow", (source, target, capacity))

    def igraphalg_mincut(self, source: Any, target: Any, capacity: Optional[str], directed: bool) -> DeclarativeBase:
        return self.call("igraphalg.mincut", (source, target, capacity, directed))

    def igraphalg_pagerank(
        self, damping: float, weights: Optional[str], directed: bool, implementation: str
    ) -> DeclarativeBase:
        return self.call("igraphalg.pagerank", (damping, weights, directed, implementation))

    def igraphalg_shortest_path_length(
        self, source: Any, target: Any, weights: Optional[str], directed: bool
    ) -> DeclarativeBase:
        return self.call("igraphalg.shortest_path_length", (source, target, weights, directed))

    def igraphalg_spanning_tree(self, weights: Optional[str], directed: bool) -> DeclarativeBase:
        return self.call("igraphalg.spanning_tree", (weights, directed))

    def igraphalg_topological_sort(self, mode: str) -> DeclarativeBase:
        return self.call("igraphalg.topological_sort", (mode))

    def import_util_cypher(self, path: str) -> DeclarativeBase:
        return self.call("import_util.cypher", (path))

    def import_util_graphml(self, path: str, config: Optional[dict]) -> DeclarativeBase:
        return self.call("import_util.graphml", (path, config))

    def import_util_json(self, path: str) -> DeclarativeBase:
        return self.call("import_util.json", (path))

    def json_util_load_from_path(self, path: str) -> DeclarativeBase:
        return self.call("json_util.load_from_path", (path))

    def json_util_load_from_url(self, url: str) -> DeclarativeBase:
        return self.call("json_util.load_from_url", (url))

    def katz_centrality_get(self, alpha: float = 0.2, epsilon: float = 0.01) -> DeclarativeBase:
        return self.call("katz_centrality.get", (alpha, epsilon))

    def katz_centrality_online_get(self) -> DeclarativeBase:
        return self.call("katz_centrality_online.get")

    def katz_centrality_online_reset(self) -> DeclarativeBase:
        return self.call("katz_centrality_online.reset")

    def katz_centrality_online_set(self, alpha: float = 0.2, epsilon: float = 0.01) -> DeclarativeBase:
        return self.call("katz_centrality_online.set", (alpha, epsilon))

    def katz_centrality_online_update(
        self,
        created_vertices: List[Any] = [],
        created_edges: List[Any] = [],
        deleted_vertices: List[Any] = [],
        deleted_edges: List[Any] = [],
    ) -> DeclarativeBase:
        return self.call(
            "katz_centrality_online.update", (created_vertices, created_edges, deleted_vertices, deleted_edges)
        )

    def kmeans_get_clusters(
        self,
        n_clusters: int,
        embedding_property: str,
        init: str,
        n_init: int,
        max_iter: int,
        tol: float,
        algorithm: str,
        random_state: int,
    ) -> DeclarativeBase:
        return self.call(
            "kmeans.get_clusters",
            (n_clusters, embedding_property, init, n_init, max_iter, tol, algorithm, random_state),
        )

    def kmeans_set_clusters(
        self,
        n_clusters: int,
        embedding_property: str,
        cluster_property: Optional[Any],
        init: str,
        n_init: int,
        max_iter: int,
        tol: float,
        algorithm: str,
        random_state: Optional[int],
    ) -> DeclarativeBase:
        return self.call(
            "kmeans.set_clusters",
            (n_clusters, embedding_property, cluster_property, init, n_init, max_iter, tol, algorithm, random_state),
        )

    def leiden_community_detection_get(
        self, weight_property: str, gamma: float, theta: float, resolution_parameter: float, number_of_iterations: int
    ) -> DeclarativeBase:
        return self.call(
            "leiden_community_detection.get",
            (weight_property, gamma, theta, resolution_parameter, number_of_iterations),
        )

    def leiden_community_detection_get_subgraph(
        self,
        subgraph_nodes: List[Any],
        subgraph_relationships: List[Any],
        weight_property: str,
        gamma: float,
        theta: float,
        resolution_parameter: float,
        number_of_iterations: int,
    ) -> DeclarativeBase:
        return self.call(
            "leiden_community_detection.get_subgraph",
            (
                subgraph_nodes,
                subgraph_relationships,
                weight_property,
                gamma,
                theta,
                resolution_parameter,
                number_of_iterations,
            ),
        )

    def link_prediction_get_training_results(self) -> DeclarativeBase:
        return self.call("link_prediction.get_training_results")

    def link_prediction_load_model(self, path: str) -> DeclarativeBase:
        return self.call("link_prediction.load_model", (path))

    def link_prediction_predict(self, src_vertex: Any, dest_vertex: Any) -> DeclarativeBase:
        return self.call("link_prediction.predict", (src_vertex, dest_vertex))

    def link_prediction_recommend(self, src_vertex: Any, dest_vertices: List[Any], k: int) -> DeclarativeBase:
        return self.call("link_prediction.recommend", (src_vertex, dest_vertices, k))

    def link_prediction_reset_parameters(self) -> DeclarativeBase:
        return self.call("link_prediction.reset_parameters")

    def link_prediction_set_model_parameters(self, parameters: dict) -> DeclarativeBase:
        return self.call("link_prediction.set_model_parameters", (parameters))

    def link_prediction_train(self) -> DeclarativeBase:
        return self.call("link_prediction.train")

    def llm_util_schema(self, output_type: str) -> DeclarativeBase:
        return self.call("llm_util.schema", (output_type))

    def map_from_nodes(self, label: str, property: str) -> DeclarativeBase:
        return self.call("map.from_nodes", (label, property))

    def max_flow_get_flow(self, start_v: Any, end_v: Any, edge_property: str = "weight") -> DeclarativeBase:
        return self.call("max_flow.get_flow", (start_v, end_v, edge_property))

    def max_flow_get_paths(self, start_v: Any, end_v: Any, edge_property: str = "weight") -> DeclarativeBase:
        return self.call("max_flow.get_paths", (start_v, end_v, edge_property))

    def merge_node(self, labels: List[str], identProps: dict, createProps: dict, matchProps: dict) -> DeclarativeBase:
        return self.call("merge.node", (labels, identProps, createProps, matchProps))

    def merge_relationship(
        self, startNode: Any, relationshipType: str, identProps: dict, createProps: dict, endNode: Any, matchProps: dict
    ) -> DeclarativeBase:
        return self.call(
            "merge.relationship", (startNode, relationshipType, identProps, createProps, endNode, matchProps)
        )

    def meta_reset(self) -> DeclarativeBase:
        return self.call("meta.reset")

    def meta_stats_offline(self) -> DeclarativeBase:
        return self.call("meta.stats_offline")

    def meta_stats_online(self, update_stats: bool) -> DeclarativeBase:
        return self.call("meta.stats_online", (update_stats))

    def meta_update(
        self,
        createdObjects: List[dict],
        deletedObjects: List[dict],
        removedVertexProperties: List[dict],
        removedEdgeProperties: List[dict],
        setVertexLabels: List[dict],
        removedVertexLabels: List[dict],
    ) -> DeclarativeBase:
        return self.call(
            "meta.update",
            (
                createdObjects,
                deletedObjects,
                removedVertexProperties,
                removedEdgeProperties,
                setVertexLabels,
                removedVertexLabels,
            ),
        )

    def meta_util_schema(self, include_properties: bool) -> DeclarativeBase:
        return self.call("meta_util.schema", (include_properties))

    def mg_get_module_file(self, path: str) -> DeclarativeBase:
        return self.call("mg.get_module_file", (path))

    def mg_get_module_files(self) -> DeclarativeBase:
        return self.call("mg.get_module_files")

    def mg_kafka_set_stream_offset(self, stream_name: str, offset: int) -> DeclarativeBase:
        return self.call("mg.kafka_set_stream_offset", (stream_name, offset))

    def mg_kafka_stream_info(self, stream_name: str) -> DeclarativeBase:
        return self.call("mg.kafka_stream_info", (stream_name))

    def mg_load(self, module_name: str) -> DeclarativeBase:
        return self.call("mg.load", (module_name))

    def mg_load_all(self) -> DeclarativeBase:
        return self.call("mg.load_all")

    def mg_procedures(self) -> DeclarativeBase:
        return self.call("mg.procedures")

    def mg_pulsar_stream_info(self, stream_name: str) -> DeclarativeBase:
        return self.call("mg.pulsar_stream_info", (stream_name))

    def mg_transformations(self) -> DeclarativeBase:
        return self.call("mg.transformations")

    def mg_update_module_file(self, path: str, content: str) -> DeclarativeBase:
        return self.call("mg.update_module_file", (path, content))

    def mgps_components(self) -> DeclarativeBase:
        return self.call("mgps.components")

    def migrate_mysql(
        self, table_or_sql: str, config: dict, config_path: str, params: Optional[Any]
    ) -> DeclarativeBase:
        return self.call("migrate.mysql", (table_or_sql, config, config_path, params))

    def migrate_oracle_db(
        self, table_or_sql: str, config: dict, config_path: str, params: Optional[Any]
    ) -> DeclarativeBase:
        return self.call("migrate.oracle_db", (table_or_sql, config, config_path, params))

    def migrate_sql_server(
        self, table_or_sql: str, config: dict, config_path: str, params: Optional[Any]
    ) -> DeclarativeBase:
        return self.call("migrate.sql_server", (table_or_sql, config, config_path, params))

    def neighbors_at_hop(self, node: Any, rel_type: List[str], distance: int) -> DeclarativeBase:
        return self.call("neighbors.at_hop", (node, rel_type, distance))

    def neighbors_by_hop(self, node: Any, rel_type: List[str], distance: int) -> DeclarativeBase:
        return self.call("neighbors.by_hop", (node, rel_type, distance))

    def node_relationship_exists(self, node: Any, pattern: List[str]) -> DeclarativeBase:
        return self.call("node.relationship_exists", (node, pattern))

    def node_relationship_types(self, node: Any, types: List[str]) -> DeclarativeBase:
        return self.call("node.relationship_types", (node, types))

    def node_relationships_exist(self, node: Any, relationships: List[str]) -> DeclarativeBase:
        return self.call("node.relationships_exist", (node, relationships))

    def node2vec_get_embeddings(
        self,
        is_directed: bool = False,
        p: Optional[Any] = 2,
        q: Optional[Any] = 0.5,
        num_walks: Optional[Any] = 4,
        walk_length: Optional[Any] = 5,
        vector_size: Optional[Any] = 100,
        alpha: Optional[Any] = 0.025,
        window: Optional[Any] = 5,
        min_count: Optional[Any] = 1,
        seed: Optional[Any] = 1,
        workers: Optional[Any] = 1,
        min_alpha: Optional[Any] = 0.0001,
        sg: Optional[Any] = 1,
        hs: Optional[Any] = 0,
        negative: Optional[Any] = 5,
        epochs: Optional[Any] = 5,
        edge_weight_property: Optional[Any] = "weight",
    ) -> DeclarativeBase:
        return self.call(
            "node2vec.get_embeddings",
            (
                is_directed,
                p,
                q,
                num_walks,
                walk_length,
                vector_size,
                alpha,
                window,
                min_count,
                seed,
                workers,
                min_alpha,
                sg,
                hs,
                negative,
                epochs,
                edge_weight_property,
            ),
        )

    def node2vec_help(self) -> DeclarativeBase:
        return self.call("node2vec.help")

    def node2vec_set_embeddings(
        self,
        is_directed: bool = False,
        p: Optional[Any] = 2,
        q: Optional[Any] = 0.5,
        num_walks: Optional[Any] = 4,
        walk_length: Optional[Any] = 5,
        vector_size: Optional[Any] = 100,
        alpha: Optional[Any] = 0.025,
        window: Optional[Any] = 5,
        min_count: Optional[Any] = 1,
        seed: Optional[Any] = 1,
        workers: Optional[Any] = 1,
        min_alpha: Optional[Any] = 0.0001,
        sg: Optional[Any] = 1,
        hs: Optional[Any] = 0,
        negative: Optional[Any] = 5,
        epochs: Optional[Any] = 5,
        edge_weight_property: Optional[Any] = "weight",
    ) -> DeclarativeBase:
        return self.call(
            "node2vec.set_embeddings",
            (
                is_directed,
                p,
                q,
                num_walks,
                walk_length,
                vector_size,
                alpha,
                window,
                min_count,
                seed,
                workers,
                min_alpha,
                sg,
                hs,
                negative,
                epochs,
                edge_weight_property,
            ),
        )

    def node2vec_online_get(self) -> DeclarativeBase:
        return self.call("node2vec_online.get")

    def node2vec_online_help(self) -> DeclarativeBase:
        return self.call("node2vec_online.help")

    def node2vec_online_reset(self) -> DeclarativeBase:
        return self.call("node2vec_online.reset")

    def node2vec_online_set_streamwalk_updater(
        self,
        half_life: int = 7200,
        max_length: int = 3,
        beta: float = 0.9,
        cutoff: int = 604800,
        sampled_walks: int = 4,
        full_walks: bool = False,
    ) -> DeclarativeBase:
        return self.call(
            "node2vec_online.set_streamwalk_updater", (half_life, max_length, beta, cutoff, sampled_walks, full_walks)
        )

    def node2vec_online_set_word2vec_learner(
        self,
        embedding_dimension: int = 128,
        learning_rate: float = 0.01,
        skip_gram: bool = True,
        negative_rate: float = 10,
        threads: Optional[int] = None,
    ) -> DeclarativeBase:
        return self.call(
            "node2vec_online.set_word2vec_learner",
            (embedding_dimension, learning_rate, skip_gram, negative_rate, threads),
        )

    def node2vec_online_update(self, edges: List[Any]) -> DeclarativeBase:
        return self.call("node2vec_online.update", (edges))

    def node_classification_get_training_data(self) -> DeclarativeBase:
        return self.call("node_classification.get_training_data")

    def node_classification_load_model(self, num: int) -> DeclarativeBase:
        return self.call("node_classification.load_model", (num))

    def node_classification_predict(self, vertex: Any) -> DeclarativeBase:
        return self.call("node_classification.predict", (vertex))

    def node_classification_reset(self) -> DeclarativeBase:
        return self.call("node_classification.reset")

    def node_classification_save_model(self) -> DeclarativeBase:
        return self.call("node_classification.save_model")

    def node_classification_set_model_parameters(self, params: Any) -> DeclarativeBase:
        return self.call("node_classification.set_model_parameters", (params))

    def node_classification_train(self, num_epochs: int) -> DeclarativeBase:
        return self.call("node_classification.train", (num_epochs))

    def node_similarity_cosine(self, node1: Any, node2: Any, mode: str = "cartesian") -> DeclarativeBase:
        return self.call("node_similarity.cosine", (node1, node2, mode))

    def node_similarity_cosine_pairwise(
        self, property: str, src_nodes: List[Any], dst_nodes: List[Any]
    ) -> DeclarativeBase:
        return self.call("node_similarity.cosine_pairwise", (property, src_nodes, dst_nodes))

    def node_similarity_jaccard(self) -> DeclarativeBase:
        return self.call("node_similarity.jaccard")

    def node_similarity_jaccard_pairwise(self, src_nodes: List[Any], dst_nodes: List[Any]) -> DeclarativeBase:
        return self.call("node_similarity.jaccard_pairwise", (src_nodes, dst_nodes))

    def node_similarity_overlap(self) -> DeclarativeBase:
        return self.call("node_similarity.overlap")

    def node_similarity_overlap_pairwise(self, src_nodes: List[Any], dst_nodes: List[Any]) -> DeclarativeBase:
        return self.call("node_similarity.overlap_pairwise", (src_nodes, dst_nodes))

    def nodes_delete(self, nodes: Any) -> DeclarativeBase:
        return self.call("nodes.delete", (nodes))

    def nodes_link(self, nodes: List[Any], type: str) -> DeclarativeBase:
        return self.call("nodes.link", (nodes, type))

    def nodes_relationship_types(self, nodes: Any, types: List[str]) -> DeclarativeBase:
        return self.call("nodes.relationship_types", (nodes, types))

    def nodes_relationships_exist(self, nodes: List[Any], relationships: List[str]) -> DeclarativeBase:
        return self.call("nodes.relationships_exist", (nodes, relationships))

    def pagerank_get(
        self, max_iterations: int = 100, damping_factor: float = 0.85, stop_epsilon: float = 1e-05
    ) -> DeclarativeBase:
        return self.call("pagerank.get", (max_iterations, damping_factor, stop_epsilon))

    def pagerank_online_get(self) -> DeclarativeBase:
        return self.call("pagerank_online.get")

    def pagerank_online_reset(self) -> DeclarativeBase:
        return self.call("pagerank_online.reset")

    def pagerank_online_set(self, walks_per_node: int = 10, walk_stop_epsilon: float = 0.1) -> DeclarativeBase:
        return self.call("pagerank_online.set", (walks_per_node, walk_stop_epsilon))

    def pagerank_online_update(
        self,
        created_vertices: List[Any] = [],
        created_edges: List[Any] = [],
        deleted_vertices: List[Any] = [],
        deleted_edges: List[Any] = [],
    ) -> DeclarativeBase:
        return self.call("pagerank_online.update", (created_vertices, created_edges, deleted_vertices, deleted_edges))

    def path_create(self, start_node: Any, relationships: dict) -> DeclarativeBase:
        return self.call("path.create", (start_node, relationships))

    def path_expand(
        self, start: Any, relationships: List[str], labels: List[str], min_hops: int, max_hops: int
    ) -> DeclarativeBase:
        return self.call("path.expand", (start, relationships, labels, min_hops, max_hops))

    def path_subgraph_all(self, start_node: Any, config: dict) -> DeclarativeBase:
        return self.call("path.subgraph_all", (start_node, config))

    def path_subgraph_nodes(self, start_node: Any, config: dict) -> DeclarativeBase:
        return self.call("path.subgraph_nodes", (start_node, config))

    def periodic_delete(self, config: dict) -> DeclarativeBase:
        return self.call("periodic.delete", (config))

    def periodic_iterate(self, input_query: str, running_query: str, config: dict) -> DeclarativeBase:
        return self.call("periodic.iterate", (input_query, running_query, config))

    def py_example_procedure(self, required_arg: Any, optional_arg: Optional[Any]) -> DeclarativeBase:
        return self.call("py_example.procedure", (required_arg, optional_arg))

    def py_example_write_procedure(self, property_name: str, property_value: Optional[Any]) -> DeclarativeBase:
        return self.call("py_example.write_procedure", (property_name, property_value))

    def refactor_categorize(
        self,
        original_prop_key: str,
        rel_type: str,
        is_outgoing: bool,
        new_label: str,
        new_prop_name_key: str,
        copy_props_list: List[str],
    ) -> DeclarativeBase:
        return self.call(
            "refactor.categorize",
            (original_prop_key, rel_type, is_outgoing, new_label, new_prop_name_key, copy_props_list),
        )

    def refactor_clone_nodes(
        self, nodes: List[Any], withRelationships: bool, skipProperties: List[str]
    ) -> DeclarativeBase:
        return self.call("refactor.clone_nodes", (nodes, withRelationships, skipProperties))

    def refactor_clone_subgraph(self, nodes: List[Any], rels: List[Any], config: dict) -> DeclarativeBase:
        return self.call("refactor.clone_subgraph", (nodes, rels, config))

    def refactor_clone_subgraph_from_paths(self, paths: List[Any], config: map) -> DeclarativeBase:
        return self.call("refactor.clone_subgraph_from_paths", (paths, config))

    def refactor_collapse_node(self, nodes: Any, type: str) -> DeclarativeBase:
        return self.call("refactor.collapse_node", (nodes, type))

    def refactor_delete_and_reconnect(self, path: Any, nodes: List[Any], config: dict) -> DeclarativeBase:
        return self.call("refactor.delete_and_reconnect", (path, nodes, config))

    def refactor_extract_node(
        self, relationships: Any, labels: List[str], outType: str, inType: str
    ) -> DeclarativeBase:
        return self.call("refactor.extract_node", (relationships, labels, outType, inType))

    def refactor_from(self, relationship: Any, new_from: Any) -> DeclarativeBase:
        return self.call("refactor.from", (relationship, new_from))

    def refactor_invert(self, relationship: Any) -> DeclarativeBase:
        return self.call("refactor.invert", (relationship))

    def refactor_normalize_as_boolean(
        self, entity: Any, property_key: str, true_values: List[Any], false_values: List[Any]
    ) -> DeclarativeBase:
        return self.call("refactor.normalize_as_boolean", (entity, property_key, true_values, false_values))

    def refactor_rename_label(self, old_label: str, new_label: str, nodes: List[Any]) -> DeclarativeBase:
        return self.call("refactor.rename_label", (old_label, new_label, nodes))

    def refactor_rename_node_property(self, old_property: str, new_property: str, nodes: List[Any]) -> DeclarativeBase:
        return self.call("refactor.rename_node_property", (old_property, new_property, nodes))

    def refactor_rename_type(self, oldType: str, newType: str, rels: List[Any]) -> DeclarativeBase:
        return self.call("refactor.rename_type", (oldType, newType, rels))

    def refactor_rename_type_property(self, old_property: str, new_property: str, rels: List[Any]) -> DeclarativeBase:
        return self.call("refactor.rename_type_property", (old_property, new_property, rels))

    def refactor_to(self, relationship: Any, new_to: Any) -> DeclarativeBase:
        return self.call("refactor.to", (relationship, new_to))

    def rust_example_basic(self, input_string: str, optional_input_int: int = 0) -> DeclarativeBase:
        return self.call("rust_example.basic", (input_string, optional_input_int))

    def rust_example_test_procedure(self) -> DeclarativeBase:
        return self.call("rust_example.test_procedure")

    def schema_assert(
        self, indices: dict, unique_constraints: dict, existence_constraints: dict, drop_existing: bool
    ) -> DeclarativeBase:
        return self.call("schema.assert", (indices, unique_constraints, existence_constraints, drop_existing))

    def schema_node_type_properties(self) -> DeclarativeBase:
        return self.call("schema.node_type_properties")

    def schema_rel_type_properties(self) -> DeclarativeBase:
        return self.call("schema.rel_type_properties")

    def set_cover_cp_solve(self, element_vertexes: List[Any], set_vertexes: List[Any]) -> DeclarativeBase:
        return self.call("set_cover.cp_solve", (element_vertexes, set_vertexes))

    def set_cover_greedy(self, element_vertexes: List[Any], set_vertexes: List[Any]) -> DeclarativeBase:
        return self.call("set_cover.greedy", (element_vertexes, set_vertexes))

    def set_property_copyPropertyNode2Node(
        self, sourceNode: Any, sourceProperties: List[str], targetNode: Any, targetProperties: List[str]
    ) -> DeclarativeBase:
        return self.call(
            "set_property.copyPropertyNode2Node", (sourceNode, sourceProperties, targetNode, targetProperties)
        )

    def set_property_copyPropertyNode2Rel(
        self, sourceNode: Any, sourceProperties: List[str], targetRel: Any, targetProperties: List[str]
    ) -> DeclarativeBase:
        return self.call(
            "set_property.copyPropertyNode2Rel", (sourceNode, sourceProperties, targetRel, targetProperties)
        )

    def set_property_copyPropertyRel2Node(
        self, sourceRel: Any, sourceProperties: List[str], targetNode: Any, targetProperties: List[str]
    ) -> DeclarativeBase:
        return self.call(
            "set_property.copyPropertyRel2Node", (sourceRel, sourceProperties, targetNode, targetProperties)
        )

    def set_property_copyPropertyRel2Rel(
        self, sourceRel: Any, sourceProperties: List[str], targetRel: Any, targetProperties: List[str]
    ) -> DeclarativeBase:
        return self.call("set_property.copyPropertyRel2Rel", (sourceRel, sourceProperties, targetRel, targetProperties))

    def temporal_format(self, temporal: Any, format: str) -> DeclarativeBase:
        return self.call("temporal.format", (temporal, format))

    def text_format(self, text: str, params: List[Any]) -> DeclarativeBase:
        return self.call("text.format", (text, params))

    def text_join(self, strings: List[str], delimiter: str) -> DeclarativeBase:
        return self.call("text.join", (strings, delimiter))

    def text_regexGroups(self, input: str, regex: str) -> DeclarativeBase:
        return self.call("text.regexGroups", (input, regex))

    def text_search_aggregate(self, index_name: str, search_query: str, aggregation_query: str) -> DeclarativeBase:
        return self.call("text_search.aggregate", (index_name, search_query, aggregation_query))

    def text_search_regex_search(self, index_name: str, search_query: str) -> DeclarativeBase:
        return self.call("text_search.regex_search", (index_name, search_query))

    def text_search_search(self, index_name: str, search_query: str) -> DeclarativeBase:
        return self.call("text_search.search", (index_name, search_query))

    def text_search_search_all(self, index_name: str, search_query: str) -> DeclarativeBase:
        return self.call("text_search.search_all", (index_name, search_query))

    def tgn_get(self) -> DeclarativeBase:
        return self.call("tgn.get")

    def tgn_get_results(self) -> DeclarativeBase:
        return self.call("tgn.get_results")

    def tgn_predict_link_score(self, src: Any, dest: Any) -> DeclarativeBase:
        return self.call("tgn.predict_link_score", (src, dest))

    def tgn_reset(self) -> DeclarativeBase:
        return self.call("tgn.reset")

    def tgn_revert_from_database(self) -> DeclarativeBase:
        return self.call("tgn.revert_from_database")

    def tgn_save_tgn_params(self) -> DeclarativeBase:
        return self.call("tgn.save_tgn_params")

    def tgn_set_eval(self) -> DeclarativeBase:
        return self.call("tgn.set_eval")

    def tgn_set_params(self, params: Dict[str, Union[int, str]]) -> DeclarativeBase:
        return self.call("tgn.set_params", (params))

    def tgn_train_and_eval(self, num_epochs: int) -> DeclarativeBase:
        return self.call("tgn.train_and_eval", (num_epochs))

    def tgn_update(self, edges: List[Any]) -> DeclarativeBase:
        return self.call("tgn.update", (edges))

    def tsp_solve(self, points: List[Any], method: str = "1.5_approx") -> DeclarativeBase:
        return self.call("tsp.solve", (points, method))

    def union_find_connected(
        self, nodes1: Optional[Any], nodes2: Optional[Any], mode: str = "pairwise", update: bool = True
    ) -> DeclarativeBase:
        return self.call("union_find.connected", (nodes1, nodes2, mode, update))

    def util_module_md5(self, values: Any) -> DeclarativeBase:
        return self.call("util_module.md5", (values))

    def uuid_generator_get(self) -> DeclarativeBase:
        return self.call("uuid_generator.get")

    def vector_search_search(self, index_name: str, result_set_size: int, query_vector: List[Any]) -> DeclarativeBase:
        return self.call("vector_search.search", (index_name, result_set_size, query_vector))

    def vector_search_show_index_info(self) -> DeclarativeBase:
        return self.call("vector_search.show_index_info")

    def vrp_route(self, depot_node: Any, number_of_vehicles: Optional[int] = None) -> DeclarativeBase:
        return self.call("vrp.route", (depot_node, number_of_vehicles))

    def weakly_connected_components_get(self) -> DeclarativeBase:
        return self.call("weakly_connected_components.get")

    def xml_module_load(self, xml_url: str, simple: bool, path: str, xpath: str, headers: dict) -> DeclarativeBase:
        return self.call("xml_module.load", (xml_url, simple, path, xpath, headers))
