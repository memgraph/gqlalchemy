from abc import ABCMeta
from gqlalchemy.query_builder import CallPartialQuery, DeclarativeBase, PartialQuery, QueryBuilder
from gqlalchemy.memgraph import Connection, Memgraph

from typing import Any, List, Optional, Tuple, Union


class MemgraphQueryBuilder(QueryBuilder):
    def __init__(self, connection: Optional[Union[Connection, Memgraph]] = None):
        super().__init__(connection)

    def example_procedure(self, required_arg: Any, optional_arg=None) -> DeclarativeBase:
        return self.call("example.procedure", (required_arg, optional_arg))

    def example_write_procedure(self, required_arg: str) -> DeclarativeBase:
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

    def nxalg_bfs_sucessors(self, source: Any, depth_limit: Optional[int] = None) -> DeclarativeBase:
        return self.call("nxalg.bfs_sucessors", (source, depth_limit))

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

    def nxalg_dfs_sucessors(self, source: Any, depth_limit: Optional[int] = None) -> DeclarativeBase:
        return self.call("nxalg.dfs_sucessors", (source, depth_limit))

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
        self, weight: str = "weight", algorithm: str = "kruskal", ignore_nan: bool = false
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
