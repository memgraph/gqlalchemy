# How to manage Pulsar streams

The stream functionality enables Memgraph to connect to a Kafka, Pulsar or
Redpanda cluster and run graph analytics on the data stream.

!!! info
    You can also use this feature with Neo4j:

    ```python
    db = Neo4j(host="localhost", port="7687", username="neo4j", password="test")
    ```


## 1. Create a Pulsar stream in Memgraph

To set up the streams, first, create a `MemgraphPulsarStream` object with all
the required arguments:

- `name: str` ➡ The name of the stream.
- `topics: List[str]` ➡ List of topic names.
- `transform: str` ➡ The transformation procedure for mapping incoming messages
  to Cypher queries.
- `batch_interval: str = None` ➡ Maximum wait time in milliseconds for consuming
  messages before calling the transform procedure.
- `batch_size: str = None` ➡ Maximum number of messages to wait for before
  calling the transform procedure.
- `service_url: str = None` ➡ URL to the running Pulsar cluster.

Now you just have to call the `create_stream()` method with the newly created
`MemgraphPulsarStream` object:

```python
from gqlalchemy import MemgraphPulsarStream

stream = MemgraphPulsarStream(name="ratings_stream", topics=["ratings"], transform="movielens.rating", service_url="localhost:6650")
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
