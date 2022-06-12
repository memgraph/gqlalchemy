from gqlalchemy import Memgraph
from gqlalchemy.graph_algorithms.query_builder import MemgraphQueryBuilder
from gqlalchemy.query_builder import QueryBuilder


def test_memgraph_query_builder_methods_exist(memgraph: Memgraph):
    """
    Tests functionality if all the procedures that are defined
    in the Memgraph extended query builder are present in the code.
    """

    mg_qb = MemgraphQueryBuilder()
    simple_qb = QueryBuilder()

    mg_qb_methods = set([method_name for method_name in dir(mg_qb) if callable(getattr(mg_qb, method_name))])

    simple_qb_methods = set(
        [method_name for method_name in dir(simple_qb) if callable(getattr(simple_qb, method_name))]
    )

    query_module_names = mg_qb_methods - simple_qb_methods
    actual_query_module_names = [procedure.name.replace(".", "_", 1) for procedure in memgraph.get_procedures()]

    print(f"Query module names: {query_module_names}\n\n")
    print(f"Actual: {actual_query_module_names}")

    for qm_name in query_module_names:
        assert qm_name in actual_query_module_names

    for qm_name in actual_query_module_names:
        assert qm_name in query_module_names
