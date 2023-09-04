# How to use on-disk storage

Since Memgraph is an in-memory graph database, the GQLAlchemy library provides
an on-disk storage solution for large properties not used in graph algorithms.
This is useful when nodes or relationships have metadata that doesn’t need to be
used in any of the graph algorithms that need to be carried out in Memgraph, but
can be fetched after. In this how-to guide, you'll learn how to use an SQL
database to store node properties seamlessly as if they were being stored in
Memgraph.

!!! info
    You can also use this feature with Neo4j:

    ```python
    db = Neo4j(host="localhost", port="7687", username="neo4j", password="test")
    ```


## Connect to Memgraph and an SQL database

First you need to do all necessary imports and connect to the running Memgraph
and SQL database instance:

```python
from gqlalchemy import Memgraph, SQLitePropertyDatabase, Node, Field
from typing import Optional

graphdb = Memgraph()
SQLitePropertyDatabase('path-to-my-db.db', graphdb)
```

The `graphdb` creates a connection to an in-memory graph database and
`SQLitePropertyDatabase` attaches to `graphdb` in its constructor.

## Define schema

For example, you can create the class `User` which maps to a node object in the
graph database.

```python
class User(Node):
    id: int = Field(unique=True, exists=True, index=True, db=graphdb)
    huge_string: Optional[str] = Field(on_disk=True)
```

Here the property `id` is a required `int` that creates uniqueness and existence
constraints inside Memgraph. You can notice that the property `id` is also
indexed on label `User`. The `huge_string` property is optional, and because the
`on_disk` argument is set to `True`, it will be saved into the SQLite database.

## Create data

Next, you can create some huge string, which won't be saved into the graph
database, but rather into the SQLite databse.

```python
my_secret = "I LOVE DUCKS" * 1000
john = User(id=5, huge_string=my_secret).save(db)
john2 = User(id=5).load(db)
print(john2.huge_string)  # prints I LOVE DUCKS, a 1000 times
```

Hopefully this guide has taught you how to use on-disk storage along with the
in-memory graph database. If you have any more questions, join our community and
ping us on [Discord](https://discord.gg/memgraph).
