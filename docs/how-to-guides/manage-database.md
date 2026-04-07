# How to manage Memgraph database

Through this guide, you will learn how to use GQLAlchemy to manage your Memgraph database instance:

- [How to manage Memgraph database](#how-to-manage-memgraph-database)
  - [Get storage information](#get-storage-information)
  - [Get build information](#get-build-information)
  - [Analyze graph statistics](#analyze-graph-statistics)
    - [Analyze all labels](#analyze-all-labels)
    - [Analyze specific labels](#analyze-specific-labels)
    - [Delete graph statistics](#delete-graph-statistics)
    - [Delete statistics for specific labels](#delete-statistics-for-specific-labels)

>If you have any more questions, join our community and ping us on [Discord](https://discord.gg/memgraph).

!!! info 
    To use the features below, you must [install GQLAlchemy](../installation.md) and have a running Memgraph instance. If you're unsure how to run Memgraph, check out the Memgraph [Quick start](https://memgraph.com/docs/getting-started)).

## Get storage information

To retrieve **detailed storage information** about your Memgraph instance, use the [`get_storage_info()`](../reference/gqlalchemy/vendors/memgraph.md#get_storage_info) method. It returns information such as vertex count, edge count, memory usage, and disk usage.

```python
from gqlalchemy import Memgraph

db = Memgraph()

storage_info = db.get_storage_info()
for item in storage_info:
    print(item)
```

## Get build information

To retrieve **build information** about the running Memgraph instance, use the [`get_build_info()`](../reference/gqlalchemy/vendors/memgraph.md#get_build_info) method. It returns information such as the build type (optimization level).

```python
from gqlalchemy import Memgraph

db = Memgraph()

build_info = db.get_build_info()
for item in build_info:
    print(item)
```

## Analyze graph statistics

Memgraph can analyze the graph to calculate statistics that help it select more optimal indexes and speed up `MERGE` operations. Use the [`analyze_graph()`](../reference/gqlalchemy/vendors/memgraph.md#analyze_graph) and [`delete_graph_statistics()`](../reference/gqlalchemy/vendors/memgraph.md#delete_graph_statistics) methods to manage these statistics.

### Analyze all labels

To **analyze statistics for all labels** in the graph:

```python
from gqlalchemy import Memgraph

db = Memgraph()

results = db.analyze_graph()
for result in results:
    print(result)
```

The result includes information about each indexed label-property pair: label, property, number of estimation nodes, number of groups, average group size, chi-squared value, and average degree.

### Analyze specific labels

To **analyze statistics only for specific labels**:

```python
from gqlalchemy import Memgraph

db = Memgraph()

results = db.analyze_graph(labels=["Person", "City"])
for result in results:
    print(result)
```

### Delete graph statistics

To **delete all previously calculated graph statistics**:

```python
from gqlalchemy import Memgraph

db = Memgraph()

deleted = db.delete_graph_statistics()
for item in deleted:
    print(item)
```

### Delete statistics for specific labels

To **delete statistics for specific labels only**:

```python
from gqlalchemy import Memgraph

db = Memgraph()

deleted = db.delete_graph_statistics(labels=["Person"])
for item in deleted:
    print(item)
```

>Hopefully, this guide has taught you how to manage your Memgraph database using GQLAlchemy. If you
>have any more questions, join our community and ping us on [Discord](https://discord.gg/memgraph).
