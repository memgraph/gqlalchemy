---
id: kafka-streams
title: How to manage Kafka streams
sidebar_label: Kafka streams
slug: /how-to-guides/streams/manage-kafka-streams
---

import Neo4jWarning from '../../templates/_neo4j_warning.mdx';

The stream functionality enables Memgraph to connect to a Kafka, Pulsar or
Redpanda cluster and run graph analytics on the data stream.

<Neo4jWarning/>

## 1. Create a Kafka stream in Memgraph

To set up the streams, first, create a `MemgraphKafkaStream` object with all the
required arguments:

- `name: str` ➡ The name of the stream.
- `topics: List[str]` ➡ List of topic names.
- `transform: str` ➡ The transformation procedure for mapping incoming messages
  to Cypher queries.
- `consumer_group: str` ➡ Name of the consumer group in Memgraph.
- `batch_interval: str = None` ➡ Maximum wait time in milliseconds for consuming
  messages before calling the transform procedure.
- `batch_size: str = None` ➡ Maximum number of messages to wait for before
  calling the transform procedure.
- `bootstrap_servers: str = None` ➡ Comma-separated list of bootstrap servers.

Now you just have to call the `create_stream()` method with the newly created
`MemgraphKafkaStream` object:

```python
from gqlalchemy import MemgraphKafkaStream

stream = MemgraphKafkaStream(name="ratings_stream", topics=["ratings"], transform="movielens.rating", bootstrap_servers="localhost:9093")
db.create_stream(stream)
```

## 2. Start the stream

To start the stream, just call the `start_stream()` method:

```python
db.start_stream(stream)
```

## 3. Check the status of the stream

To check the status of the stream in Memgraph, just run the following command:

```python
check = db.get_streams()
```

## 4. Delete the stream

You can use the `drop_stream()` method to delete a stream:

```python
check = db.drop_stream(stream)
```
