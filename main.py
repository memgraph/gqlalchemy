from distutils.util import execute
from gqlalchemy import Memgraph, memgraph
from gqlalchemy.query_builder import QueryBuilder


if __name__ == "__main__":
    mg = Memgraph()

    qb = QueryBuilder()

    query = qb.call("mg.create_module_file", "'govnich.py', 'Hello soul sister!'").yield_().construct_query()
    result = list(mg.execute_and_fetch(query))
    pass