# How to manage Memgraph binary instances in Python

Through this guide, you will learn how to start, stop, connect to and monitor
Memgraph instances with GQLAlchemy.

!!! info
    You can also use this feature with Neo4j:

    ```python
    db = Neo4j(host="localhost", port="7687", username="neo4j", password="test")
    ```

First, perform all the necessary imports:

```python
from gqlalchemy.instance_runner import MemgraphInstanceBinary
```

## Start the Memgraph instance

!!! warning
    In order to start a Memgraph instance that you installed using `dpkg`, you need
    to run the binary file as user `memgraph`. Otherwise, the process won't have the
    right access rights to the needed directories and files.

The following code will create a Memgraph instance, start it and return a
connection object:

```python
memgraph_instance = MemgraphInstanceBinary(
    host="0.0.0.0", port=7698, binary_path="/usr/lib/memgraph/memgraph", user="memgraph"
)
memgraph = memgraph_instance.start_and_connect(restart=False)
```

We used the default values for the arguments:

- `host="0.0.0.0"`: This is the wildcard address which indicates that the
  instance should accept connections from all interfaces.
- `port=7687`: This is the default port Memgraph listens to.
- `binary_path="/usr/lib/memgraph/memgraph"`: The default location of the
  Memgraph binary file on Ubuntu.
- `user="memgraph"`: The user that will start the Memgraph process.
- `restart=False`: If the instance is already running, it won't be stopped and
  started again.

After we have created the connection, we can start querying the database:

```python
memgraph.execute_and_fetch("RETURN 'Memgraph is running' AS result"))[0]["result"]
```

## Pass configuration flags

You can pass [configuration flags](htps://memgraph.com/docs/configuration/configuration-settings)
using a dictionary:

```python
config={"--log-level": "TRACE"}
memgraph_instance = MemgraphInstanceBinary(config=config)
```

## Stop the Memgraph instance

To stop a Memgraph instance, call the `stop()` method:

```python
memgraph_instance.stop()
```

## Check if a Memgraph instance is running

To check if a Memgraph instance is running, call the `is_running()` method:

```python
memgraph_instance.is_running()
```

## Where to next?

Hopefully, this guide has taught you how to manage Memgraph binary instances. If
you have any more questions, join our community and ping us on
[Discord](https://discord.gg/memgraph).
