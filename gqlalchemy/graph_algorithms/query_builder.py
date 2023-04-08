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

    def cycles_get(self) -> DeclarativeBase:
        return self.call("cycles.get")

    def distance_calculator_multiple(
        self, start_points: List[Any], end_points: List[Any], metrics: str = "m"
    ) -> DeclarativeBase:
        return self.call("distance_calculator.multiple", (start_points, end_points, metrics))

    def distance_calculator_single(
        self, start: Optional[Any], end: Optional[Any], metrics: str = "m"
    ) -> DeclarativeBase:
        return self.call("distance_calculator.single", (start, end, metrics))

    def export_util_json(self, path: str) -> DeclarativeBase:
        return self.call("export_util.json", (path))

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

    def max_flow_get_flow(self, start_v: Any, end_v: Any, edge_property: str = "weight") -> DeclarativeBase:
        return self.call("max_flow.get_flow", (start_v, end_v, edge_property))

    def max_flow_get_paths(self, start_v: Any, end_v: Any, edge_property: str = "weight") -> DeclarativeBase:
        return self.call("max_flow.get_paths", (start_v, end_v, edge_property))

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

    def node_similarity_cosine(self, node1: Any, node2: Any, mode: str = "cartesian") -> DeclarativeBase:
        return self.call("node_similarity.cosine", (node1, node2, mode))

    def node_similarity_jaccard(self, node1: Any, node2: Any, mode: str = "cartesian") -> DeclarativeBase:
        return self.call("node_similarity.jaccard", (node1, node2, mode))

    def node_similarity_overlap(self, node1: Any, node2: Any, mode: str = "cartesian") -> DeclarativeBase:
        return self.call("node_similarity.overlap", (node1, node2, mode))

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

    def rust_example_basic(self, input_string: str, optional_input_int: int = 0) -> DeclarativeBase:
        return self.call("rust_example.basic", (input_string, optional_input_int))

    def rust_example_test_procedure(self) -> DeclarativeBase:
        return self.call("rust_example.test_procedure")

    def set_cover_cp_solve(self, element_vertexes: List[Any], set_vertexes: List[Any]) -> DeclarativeBase:
        return self.call("set_cover.cp_solve", (element_vertexes, set_vertexes))

    def set_cover_greedy(self, element_vertexes: List[Any], set_vertexes: List[Any]) -> DeclarativeBase:
        return self.call("set_cover.greedy", (element_vertexes, set_vertexes))

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

    def uuid_generator_get(self) -> DeclarativeBase:
        return self.call("uuid_generator.get")

    def vrp_route(self, depot_node: Any, number_of_vehicles: Optional[int] = None) -> DeclarativeBase:
        return self.call("vrp.route", (depot_node, number_of_vehicles))

    def weakly_connected_components_get(self) -> DeclarativeBase:
        return self.call("weakly_connected_components.get")
