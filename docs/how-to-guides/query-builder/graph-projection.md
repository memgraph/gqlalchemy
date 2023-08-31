# How to create a graph projection

[![Related -
How-to](https://img.shields.io/static/v1?label=Related&message=How-to&color=blue&style=for-the-badge)](https://memgraph.com/docs/advanced-algorithms/run-algorithms)
[![Related - Under the
Hood](https://img.shields.io/static/v1?label=Related&message=Under%20the%20hood&color=orange&style=for-the-badge)](https://memgraph.com/blog/how-we-designed-and-implemented-graph-projection-feature)

As subgraphs are mainly used with Memgraph's query modules (graph algorithms), 
`QueryBuilder`'s `call()` method enables specifying the subgraph to use with a certain algorithm.

To call a procedure named `test_query_module` with argument `"arg"`, and run
it on a subgraph containing only nodes with label `:LABEL` and their mutual 
relationships build the following query:

```Python
from gqlalchemy import QueryBuilder

label = "LABEL"

query_builder = QueryBuilder().call(procedure="test_query_module",
                                    arguments=("arg"), node_labels=label)

query_builder.execute()
```

The above code executes the following Cypher query:
```Cypher
MATCH p=(a)-->(b)
WHERE (a:LABEL)
AND (b:LABEL)
WITH project(p) AS graph
CALL test_query_module(graph, 'arg')
```

`WHERE` and `AND` clauses are used to allow for more generalization. To expand
on this code you can use multiple relationship types and node
labels. Node labels and relationship types can be passed as a single string, in
which case that string is used for all labels or types. To specify different
labels and types for entities on a path, you need to pass a list of lists,
containing a list of labels for every node on a path, and likewise for relationships. You can use this as following:

```Python
node_labels = [["COMP", "DEVICE"], ["USER"], ["SERVICE", "GATEWAY"]]
relationship_types = [["OWNER", "RENTEE"], ["USES", "MAKES"]]
relationship_directions = [RelationshipDirection.LEFT, RelationshipDirection.RIGHT]
arguments = ("arg0", 5)

query_builder = QueryBuilder().call(procedure="test_query_module",
                                    arguments = arguments,
                                    node_labels=node_labels,
                                    relationship_types=relationship_types,
                                    relationship_directions=relationship_directions)

query_builder.execute()
```

The above code executes the following Cypher query:
```Cypher
MATCH p=(a)<-[:OWNER | :RENTEE]-(b)-[:USES | :MAKES]->(c)
WHERE (a:COMP or a:DEVICE)
AND (b:USER)
AND (c:SERVICE or c:GATEWAY)
WITH project(p) AS graph
CALL test_query_module(graph, "arg0", 5)
```

This query calls `test_query_module` on a subgraph containing all nodes labeled
`USER` that have an outgoing relationship of types either `OWNER` or `RENTEE` towards nodes labeled `COMP` or `DEVICE` and also a relationship of type `USES` or `MAKES` towards nodes labeled `SERVICE` or `GATEWAY`.
