# GQLAlchemy


<p>
    <a href="https://github.com/memgraph/gqlalchemy/actions"><img src="https://github.com/memgraph/gqlalchemy/workflows/Build%20and%20Test/badge.svg" /></a>
    <a href="https://github.com/memgraph/gqlalchemy/blob/main/LICENSE"><img src="https://img.shields.io/github/license/memgraph/gqlalchemy" /></a>
    <a href="https://pypi.org/project/gqlalchemy"><img src="https://img.shields.io/pypi/v/gqlalchemy" /></a>
    <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
    <a href="https://memgraph.com/docs/gqlalchemy" alt="Documentation"><img src="https://img.shields.io/badge/documentation-GQLAlchemy-orange" /></a>
    <a href="https://github.com/memgraph/gqlalchemy/stargazers" alt="Stargazers"><img src="https://img.shields.io/github/stars/memgraph/gqlalchemy?style=social" /></a>
</p>

**GQLAlchemy** is a fully open-source Python library and **Object Graph Mapper** (OGM) - a link between graph database objects and Python objects.

An Object Graph Mapper or OGM provides a developer-friendly workflow that allows for writing object-oriented notation to communicate with graph databases. Instead of writing Cypher queries, you will be able to write object-oriented code, which the OGM will automatically translate into Cypher queries.

GQLAlchemy is built on top of Memgraph's low-level Python client `pymgclient`
([PyPI](https://pypi.org/project/pymgclient/) /
[Documentation](https://memgraph.github.io/pymgclient/) /
[GitHub](https://github.com/memgraph/pymgclient)).

## Installation

Before you install `gqlalchemy`, make sure that you have `cmake` installed by running:
```
cmake --version
```
You can install `cmake` by following the [official instructions](https://cgold.readthedocs.io/en/latest/first-step/installation.html#).

To install `gqlalchemy`, simply run the following command:
```
pip install gqlalchemy
```

If you are using [Conda](https://docs.conda.io/en/latest/) for Python environment management, you can install GQLAlchemy through pip.

## Build & Test

The project uses [Poetry](https://python-poetry.org/) to build the GQLAlchemy Python library. To build and run tests, execute the following command:
`poetry install`

Before starting the tests, make sure you have an active Memgraph instance running. Execute the following command:
`poetry run pytest .`

## GQLAlchemy capabilities

<details>
<summary>🗺️ Object graph mapper</summary>
<br>

Below you can see an example of how to create `User` and `Language` node classes, and a relationship class of type `SPEAKS`. Along with that, you can see how to create a new node and relationship and how to save them in the database. After that, you can load those nodes and relationship from the database.
<br>
<br>

```python
from gqlalchemy import Memgraph, Node, Relationship, Field
from typing import Optional

db = Memgraph()

class User(Node, index=True, db=db):
    id: str = Field(index=True, exist=True, unique=True, db=db)

class Language(Node):
    name: str = Field(unique=True, db=db)

class Speaks(Relationship, type="SPEAKS"):
    pass

user = User(id="3", username="John").save(db)
language = Language(name="en").save(db)
speaks_rel = Speaks(
    _start_node_id = user._id,
    _end_node_id = language._id
).save(db)

loaded_user = User(id="3").load(db=db)
print(loaded_user)
loaded_speaks = Speaks(
        _start_node_id=user._id,
        _end_node_id=language._id
    ).load(db)
print(loaded_speaks)
```
</details>

<details>
<summary>🔨 Query builder</summary>
<br>
When building a Cypher query, you can use a set of methods that are wrappers around Cypher clauses. 
<br>
<br>

```python
from gqlalchemy import create, match
from gqlalchemy.query_builder import Operator

query_create = create()
        .node(labels="Person", name="Leslie")
        .to(relationship_type="FRIENDS_WITH")
        .node(labels="Person", name="Ron")
        .execute()

query_match = match()
        .node(labels="Person", variable="p1")
        .to()
        .node(labels="Person", variable="p2")
        .where(item="p1.name", operator=Operator.EQUAL, literal="Leslie")
        .return_(results=["p1", ("p2", "second")])
        .execute()
```
</details>

<details>
<summary>🚰 Manage streams</summary>
<br>

You can create and start Kafka or Pulsar stream using GQLAlchemy. 
<br>

**Kafka stream** 
```python
from gqlalchemy import MemgraphPulsarStream

stream = MemgraphPulsarStream(name="ratings_stream", topics=["ratings"], transform="movielens.rating", service_url="localhost:6650")
db.create_stream(stream)
db.start_stream(stream)
```

**Pulsar stream**
```python
from gqlalchemy import MemgraphKafkaStream

stream = MemgraphKafkaStream(name="ratings_stream", topics=["ratings"], transform="movielens.rating", bootstrap_servers="localhost:9093")
db.create_stream(stream)
db.start_stream(stream)
```
</details>

<details>
<summary>🗄️ Import table data from different sources</summary>
<br>

**Import table data to a graph database**

You can translate table data from a file to graph data and import it to Memgraph. Currently, we support reading of CSV, Parquet, ORC and IPC/Feather/Arrow file formats via the PyArrow package.

Read all about it in [table to graph importer how-to guide](https://memgraph.com/docs/gqlalchemy/how-to-guides/table-to-graph-importer).

**Make a custom file system importer**

If you want to read from a file system not currently supported by GQLAlchemy, or use a file type currently not readable, you can implement your own by extending abstract classes `FileSystemHandler` and `DataLoader`, respectively.

Read all about it in [custom file system importer how-to guide](https://memgraph.com/docs/gqlalchemy/how-to-guides/custom-file-system-importer).

</details>

<details>
<summary>⚙️ Manage Memgraph instances</summary>
<br>

You can start, stop, connect to and monitor Memgraph instances with GQLAlchemy.

**Manage Memgraph Docker instance**

```python
from gqlalchemy.instance_runner import (
    DockerImage,
    MemgraphInstanceDocker
)

memgraph_instance = MemgraphInstanceDocker(
    docker_image=DockerImage.MEMGRAPH, docker_image_tag="latest", host="0.0.0.0", port=7687
)
memgraph = memgraph_instance.start_and_connect(restart=False)

memgraph.execute_and_fetch("RETURN 'Memgraph is running' AS result"))[0]["result"]
```

**Manage Memgraph binary instance**

```python
from gqlalchemy.instance_runner import MemgraphInstanceBinary

memgraph_instance = MemgraphInstanceBinary(
    host="0.0.0.0", port=7698, binary_path="/usr/lib/memgraph/memgraph", user="memgraph"
)
memgraph = memgraph_instance.start_and_connect(restart=False)

memgraph.execute_and_fetch("RETURN 'Memgraph is running' AS result"))[0]["result"]
```
</details>

<details>
<summary>🔫 Manage database triggers</summary>
<br>

Because Memgraph supports database triggers on `CREATE`, `UPDATE` and `DELETE` operations, GQLAlchemy also implements a simple interface for maintaining these triggers.

```python
from gqlalchemy import Memgraph, MemgraphTrigger
from gqlalchemy.models import (
    TriggerEventType,
    TriggerEventObject,
    TriggerExecutionPhase,
)

db = Memgraph()

trigger = MemgraphTrigger(
    name="ratings_trigger",
    event_type=TriggerEventType.CREATE,
    event_object=TriggerEventObject.NODE,
    execution_phase=TriggerExecutionPhase.AFTER,
    statement="UNWIND createdVertices AS node SET node.created_at = LocalDateTime()",
)

db.create_trigger(trigger)
triggers = db.get_triggers()
print(triggers)
```
</details>

<details>
<summary>💽 On-disk storage</summary>
<br>

Since Memgraph is an in-memory graph database, the GQLAlchemy library provides an on-disk storage solution for large properties not used in graph algorithms. This is useful when nodes or relationships have metadata that doesn’t need to be used in any of the graph algorithms that need to be carried out in Memgraph, but can be fetched after. Learn all about it in the [on-disk storage how-to guide](https://memgraph.com/docs/gqlalchemy/how-to-guides/on-disk-storage).
</details>

<br>

If you want to learn more about OGM, query builder, managing streams, importing data from different source, managing Memgraph instances, managing database triggers and using on-disk storage, check out the GQLAlchemy [how-to guides](https://memgraph.com/docs/gqlalchemy/how-to-guides).

## Development (how to build)
```
poetry run flake8 .
poetry run black .
poetry run pytest . -k "not slow"
```

## Documentation

The GQLAlchemy documentation is available on [memgraph.com/docs/gqlalchemy](https://memgraph.com/docs/gqlalchemy/).

The documentation can be generated by executing:
```
pip3 install python-markdown
python-markdown
```

## License

Copyright (c) 2016-2022 [Memgraph Ltd.](https://memgraph.com)

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
