# Import data

You can import data in the following formats:

- [**CSV**](#csv)
- [**JSON**](#json)
- [**Parquet, ORC or IPC/Feather/Arrow**](#parquet-orc-or-ipcfeatherarrow)
- [**Python graphs - NetworkX, PyG or DGL graph**](#python-graphs---networkx-pyg-or-dgl-graph)
- [**Kafka, RedPanda or Pulsar data stream**](#kafka-redpanda-or-pulsar-data-stream)

Besides that, you can create data directly from code using the [**object graph mapper**](how-to-guides/ogm.md) or [**query builder**](how-to-guides/query-builder.md).


!!! tip 
    The fastest way to import data into Memgraph is by using the [LOAD CSV clause](https://memgraph.com/docs/data-migration/csv). It's recommended to first [create indexes](https://memgraph.com/docs/fundamentals/indexes) using the `CREATE INDEX` clause. You can create them by [executing the Cypher query](https://memgraph.com/docs/client-libraries/python) or using [object graph mapper](how-to-guides/ogm.md#create-indexes).

## CSV

To import CSV file into Memgraph via GQLAlchemy, you can use the [`LOAD CSV` clause](https://memgraph.com/docs/data-migration/csv). That clause can be used by [executing the Cypher query](https://memgraph.com/docs/client-libraries/python) or by [building the query with the query builder](how-to-guides/query-builder.md#load-csv-file). Another way of importing CSV data into Memgraph is by [translating it into a graph](how-to-guides/loaders/import-table-data-to-graph-database.md).

## JSON

To import JSON files into Memgraph via GQLAlchemy, you can call procedures from the [`json_util` module](https://memgraph.com/docs/advanced-algorithms/available-algorithms/json_util) available in MAGE library. If the JSON data is formatted in a particular style, you can call the [`import_util.json()` procedure](https://memgraph.com/docs/advanced-algorithms/available-algorithms/json_util#jsonpath) from MAGE. The procedures can be called by [executing Cypher queries](https://memgraph.com/docs/client-libraries/python) or [using the query builder](how-to-guides/query-builder.md#call-procedures).


## Parquet, ORC or IPC/Feather/Arrow 

To import Parquet, ORC or IPC/Feather/Arrow file into Memgraph via GQLAlchemy, [transform table data from a file into a graph](how-to-guides/loaders/import-table-data-to-graph-database.md). 

!!! note 
    If you want to read from a file system not currently supported by GQLAlchemy, or use a file type currently not readable, you can implement your own by [making a custom file system importer](how-to-guides/loaders/make-a-custom-file-system-importer.md).

## Python graphs - NetworkX, PyG or DGL graph

To import NetworkX, PyG or DGL graph into Memgraph via GQLAlchemy, [transform the source graph into Memgraph graph](how-to-guides/translators/import-python-graphs.md).

## Kafka, RedPanda or Pulsar data stream

To consume Kafka, RedPanda or Pulsar data stream, you can write a [appropriate Cypher queries](https://memgraph.com/docs/data-streams/manage-streams-query) and [execute](https://memgraph.com/docs/client-libraries/python) them, or use GQLAlchemy stream manager for [Kafka, RedPanda](how-to-guides/streams/kafka-streams.md) or [Pulsar](how-to-guides/streams/pulsar-streams.md) streams.


## Learn more

To learn how to utilize the GQLAlchemy library with Memgraph, check out the [how-to guides](how-to-guides/overview.md) or sign up for the [Getting started with Memgraph and Python course](https://app.livestorm.co/memgraph/getting-started-with-memgraph-and-python-on-demand).


