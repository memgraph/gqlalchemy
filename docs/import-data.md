---
id: import-data
title: Import data
sidebar_label: Import data
slug: /import-data
---

You can import data in the following formats:
- [**CSV**](#csv)
- [**JSON**](#json)
- [**Parquet, ORC or IPC/Feather/Arrow**](#parquet-orc-or-ipcfeatherarrow)
- [**Python graphs - NetworkX, PyG or DGL graph**](#python-graphs---networkx-pyg-or-dgl-graph)
- [**Kafka, RedPanda or Pulsar data stream**](#kafka-redpanda-or-pulsar-data-stream)

Besides that, you can create data directly from code using the [**object graph mapper**](/gqlalchemy/how-to-guides/ogm) or [**query builder**](/gqlalchemy/how-to-guides/query-builder).


:::tip
The fastest way to import data into Memgraph is by using the [LOAD CSV clause](/memgraph/import-data/load-csv-clause). It's recommended to first [create indexes](/memgraph/next/how-to-guides/indexes) using the `CREATE INDEX` clause. You can create them by [executing the Cypher query](/memgraph/connect-to-memgraph/drivers/python) or using [object graph mapper](/gqlalchemy/how-to-guides/ogm#create-indexes).
:::

## CSV

To import CSV file into Memgraph via GQLAlchemy, you can use the [`LOAD CSV` clause](/memgraph/import-data/load-csv-clause). That clause can be used by [executing the Cypher query](/memgraph/connect-to-memgraph/drivers/python) or by [building the query with the query builder](/gqlalchemy/how-to-guides/query-builder#load-csv-file). Another way of importing CSV data into Memgraph is by [translating it into a graph](/gqlalchemy/how-to-guides/table-to-graph-importer).

## JSON

To import JSON files into Memgraph via GQLAlchemy, you can call procedures from the [`json_util` module](/mage/query-modules/python/json-util) available in MAGE library. If the JSON data is formatted in a particular style, you can call the [`import_util.json()` procedure](/mage/query-modules/python/import-util#jsonpath) from MAGE. The procedures can be called by [executing Cypher queries](/memgraph/connect-to-memgraph/drivers/python) or [using the query builder](/gqlalchemy/how-to-guides/query-builder#call-procedures).


## Parquet, ORC or IPC/Feather/Arrow 

To import Parquet, ORC or IPC/Feather/Arrow file into Memgraph via GQLAlchemy, [transform table data from a file into a graph](/gqlalchemy/how-to-guides/table-to-graph-importer). 

:::note
If you want to read from a file system not currently supported by GQLAlchemy, or use a file type currently not readable, you can implement your own by [making a custom file system importer](/gqlalchemy/how-to-guides/custom-file-system-importer).
:::


## Python graphs - NetworkX, PyG or DGL graph

To import NetworkX, PyG or DGL graph into Memgraph via GQLAlchemy, [transform the source graph into Memgraph graph](/gqlalchemy/how-to-guides/import-python-graphs).

## Kafka, RedPanda or Pulsar data stream

To consume Kafka, RedPanda or Pulsar data stream, you can write a [appropriate Cypher queries](/memgraph/import-data/data-streams/manage-streams) and [execute](/memgraph/connect-to-memgraph/drivers/python) them, or use GQLAlchemy stream manager for [Kafka, RedPanda](/gqlalchemy/how-to-guides/streams/manage-kafka-streams) or [Pulsar](/gqlalchemy/how-to-guides/streams/manage-pulsar-streams) streams.


## Learn more

To learn how to utilize the GQLAlchemy library with Memgraph, check out the [how-to guides](/gqlalchemy/how-to-guides) or sign up for the [Getting started with Memgraph and Python course](https://app.livestorm.co/memgraph/getting-started-with-memgraph-and-python-on-demand).


