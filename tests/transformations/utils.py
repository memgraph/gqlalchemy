from gqlalchemy import Memgraph

def init_database():
    memgraph = Memgraph()
    memgraph.drop_database()
    return memgraph