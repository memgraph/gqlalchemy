---
sidebar_label: nx_translator
title: gqlalchemy.transformations.translators.nx_translator
---

## NetworkXCypherBuilder Objects

```python
class NetworkXCypherBuilder()
```

#### yield\_queries

```python
def yield_queries(graph: nx.Graph) -> Iterator[str]
```

Generates Cypher queries for creating a graph.

#### yield\_query\_groups

```python
def yield_query_groups(graph: nx.Graph) -> List[Iterator[str]]
```

Generates Cypher queries for creating a graph by query groups.

## NxTranslator Objects

```python
class NxTranslator(Translator)
```

Uses original ids from Memgraph. Labels are encoded as properties. Since NetworkX allows
that nodes have properties of different dimensionality, this modules makes use of it and stores properties
as dictionary entries. All properties are saved to NetworkX data structure.

#### to\_cypher\_queries

```python
def to_cypher_queries(graph: nx.Graph,
                      config: NetworkXCypherConfig = None) -> Iterator[str]
```

Generates a Cypher query for creating a graph.

#### nx\_graph\_to\_memgraph\_parallel

```python
def nx_graph_to_memgraph_parallel(graph: nx.Graph,
                                  config: NetworkXCypherConfig = None) -> None
```

Generates Cypher queries and inserts data into Memgraph in parallel.

#### get\_instance

```python
def get_instance()
```

Creates NetworkX instance of the graph from the data residing inside Memgraph. Since NetworkX doesn&#x27;t support labels in a way Memgraph does, labels
are encoded as a node and edge properties.

