# Getting started with GQLAlchemy

[![GQLAlchemy](https://img.shields.io/badge/source-GQLAlchemy-FB6E00?style=for-the-badge&logo=github&logoColor=white)](https://github.com/memgraph/gqlalchemy)

**GQLAlchemy** is an open-source Python library and an **Object Graph Mapper** (OGM) - a link between graph database objects and Python objects. GQLAlchemy supports **Memgraph** and **Neo4j**.

An Object Graph Mapper or OGM provides a developer-friendly workflow for writing object-oriented notation to communicate to a graph database. Instead of writing Cypher queries, you can write object-oriented code, which the OGM will automatically translate into Cypher queries.

## Quick start

### 1. Install GQLAlchemy

Either install GQLAlchemy through [pip](installation.md#pip) or [build it from
source](installation.md#source). If you are using [Conda](https://docs.conda.io/en/latest/) for Python environment management, you can install GQLAlchemy through [pip](installation.md#pip).

!!! danger
    Python 3.11 users: On Windows, GQLAlchemy is not yet compatible with this Python version. Linux users can install GQLAlchemy **without** the DGL extra (due to its dependencies not supporting Python 3.11 yet). If this is currently a blocker for you, please let us know by [opening an issue](https://github.com/memgraph/gqlalchemy/issues).

### 2. Connect to Memgraph

**Prerequisites**

To follow this guide, you will need:

- A **running Memgraph instance**. If you need to set up Memgraph, take a look
  at the [Installation guide](https://memgraph.com/docs/getting-started/install-memgraph).

**Basic setup**

We'll be using a **Python program** to demonstrate how to connect to a running
Memgraph database instance.<br />

Let's jump in and connect a simple program to Memgraph.

**1.** Create a new directory for your program, for example, `/memgraph_python`
and position yourself in it.<br /> 

**2.** Create a new Python script and name it `program.py` . Add the following
code to it:

```python
from gqlalchemy import Memgraph

# Make a connection to the database
memgraph = Memgraph(host='127.0.0.1', port=7687)

# Delete all nodes and relationships
query = "MATCH (n) DETACH DELETE n"

# Execute the query
memgraph.execute(query)

# Create a node with the label FirstNode and message property with the value "Hello, World!"
query = """CREATE (n:FirstNode)
           SET n.message = '{message}'
           RETURN 'Node '  + id(n) + ': ' + n.message AS result""".format(message="Hello, World!")

# Execute the query
results = memgraph.execute_and_fetch(query)

# Print the first member
print(list(results)[0]['result'])
```

!!! note 
    If the program fails to connect to a Memgraph instance that was started with Docker, you may need to use a different IP address (not the default `localhost` / `127.0.0.1` ) to connect to the instance. You can find the **`CONTAINER_ID`** with `docker ps` and use it in the following command to retrieve the address:
    ```
    docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' CONTAINER_ID
    ```


**3.** Now, you can run the application with the following command:

```
python ./program.py
```

You should see an output similar to the following:

```
Node 1: Hello, World!
```



### 3. Learn how to use GQLAlchemy

With the help of the [How-to guides](how-to-guides/overview.md) you can learn how to use GQLAlchemy's features, such as object graph mapper and query builder. 

### 3. Check the reference guide

Don't forget to check the [Reference guide](reference/gqlalchemy/overview.md) if you want to find out which methods GQLAlchemy has and how to use it. If the reference guide is not clear enough, head over to the [GQLAlchemy repository](https://github.com/memgraph/gqlalchemy) and inspect the source code. While you're there, feel free to give us a star or contribute to this open-source Python library.
