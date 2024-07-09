---
sidebar_label: query_builder
title: gqlalchemy.graph_algorithms.query_builder
---

## MemgraphQueryBuilder Objects

```python
class MemgraphQueryBuilder(QueryBuilder)
```

This query builder extends the usual Cypher query builder capabilities with Memgraph&#x27;s query modules.
User gets with this module autocomplete features of graph algorithms.
Documentation on the methods can be found on Memgraph&#x27;s web page.

## MageQueryBuilder Objects

```python
class MageQueryBuilder(MemgraphQueryBuilder)
```

This query builder extends the Memgraph query builder with Memgraph MAGE graph algorithm Cypher options.
User gets with this module autocomplete features of graph algorithms written in MAGE library.
Documentation on the methods can be found on Memgraph&#x27;s web page.

