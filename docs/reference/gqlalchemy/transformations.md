---
sidebar_label: transformations
title: gqlalchemy.transformations
---

#### nx\_to\_cypher

```python
def nx_to_cypher(graph: nx.Graph, config: NetworkXCypherConfig = None) -> Iterator[str]
```

Generates a Cypher queries for creating graph.

#### nx\_graph\_to\_memgraph\_parallel

```python
def nx_graph_to_memgraph_parallel(graph: nx.Graph, host: str = "127.0.0.1", port: int = 7687, username: str = "", password: str = "", encrypted: bool = False, config: NetworkXCypherConfig = None) -> None
```

Generates a Cypher queries and inserts data into Memgraph in parallel.


## NetworkXCypherBuilder Objects

```python
class NetworkXCypherBuilder()
```

#### yield\_queries

```python
def yield_queries(graph: nx.Graph) -> Iterator[str]
```

Generates a Cypher queries for creating graph.


#### yield\_query\_groups

```python
def yield_query_groups(graph: nx.Graph) -> List[Iterator[str]]
```

Generates a Cypher queries for creating graph by query groups.

