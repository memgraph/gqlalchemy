from distutils.util import execute
from gqlalchemy import Memgraph, memgraph
from gqlalchemy.query_builder import QueryBuilder


if __name__ == "__main__":
    mg = Memgraph()

    qb = QueryBuilder()
    qb = QueryBuilder()

    file_text = open('gqlalchemy/query_modules/push_streams/kafka.py','r').read()
    query = "mg.create_module_file", "'gov.py', '{file_text}'".format(file_text = file_text)
    print(query)
    query = qb.call(query).yield_().construct_query()
    result = list(mg.execute_and_fetch(query))
    result = list(mg.execute_and_fetch("CALL mg.procedures() YIELD *"))

    pass