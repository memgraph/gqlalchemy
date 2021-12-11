# GQLAlchemy


<p>
    <a href="https://github.com/memgraph/gqlalchemy/actions"><img src="https://github.com/memgraph/gqlalchemy/workflows/Build%20and%20Test/badge.svg" /></a>
    <a href="https://github.com/memgraph/gqlalchemy/blob/main/LICENSE"><img src="https://img.shields.io/github/license/memgraph/gqlalchemy" /></a>
    <a href="https://pypi.org/project/gqlalchemy"><img src="https://img.shields.io/pypi/v/gqlalchemy" /></a>
    <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
    <a href="https://github.com/memgraph/gqlalchemy/stargazers" alt="Stargazers"><img src="https://img.shields.io/github/stars/memgraph/gqlalchemy?style=social" /></a>
</p>


[![release](https://progress-bar.dev/10/?width=800&title=release%201.1&color=f0ad4e)](https://github.com/memgraph/gqlalchemy/milestone/1)

GQLAlchemy is a library developed to assist in writing and running queries on Memgraph. GQLAlchemy supports high-level connection to Memgraph as well as modular query builder.

GQLAlchemy is built on top of Memgraph's low-level client `pymgclient`
([pypi](https://pypi.org/project/pymgclient/) /
[documentation](https://memgraph.github.io/pymgclient/) /
[GitHub](https://github.com/memgraph/pymgclient)).

## Installation

Before you install `gqlalchemy` make sure that you have `cmake` installed by running:
```
cmake --version
```
You can install `cmake` by following the [official instructions](https://cgold.readthedocs.io/en/latest/first-step/installation.html#).

To install `gqlalchemy`, simply run the following command:
```
pip install gqlalchemy
```

## Build & Test

The project uses [poetry](https://python-poetry.org/) to build the GQLAlchemy. To build and run tests execute the following commands:
`poetry install`

Before running tests make sure you have an active memgraph instance, then you can run:
`poetry run pytest .`

## GQLAlchemy example


When working with the `gqlalchemy`, Python developer can connect to database and execute `MATCH` cypher query with following syntax:

```python
from gqlalchemy import Memgraph

memgraph = Memgraph("127.0.0.1", 7687)
memgraph.execute("CREATE (:Node)-[:Connection]->(:Node)")
results = memgraph.execute_and_fetch("""
    MATCH (from:Node)-[:Connection]->(to:Node)
    RETURN from, to;
""")

for result in results:
    print(result['from'])
    print(result['to'])
```

## Query builder example

As we can see, the example above can be error-prone, because we do not have abstractions for creating a database connection and `MATCH` query.

Now, rewrite the exact same query by using the functionality of gqlalchemys query builder..

```python
from gqlalchemy import Match, Memgraph

memgraph = Memgraph()

results = Match().node("Node",variable="from")\
                 .to("Connection")\
                 .node("Node",variable="to")\
                 .execute()

for result in results:
    print(result['from'])
    print(result['to'])
```

An example using the Node and Relationship classes:
```python
from gqlalchemy import Memgraph, Node, Relationship, Match

memgraph = Memgraph("127.0.0.1", 7687)

memgraph.execute("CREATE (:Node {id: 1})-[:RELATED_TO {id: 1}]->(:Node {id: 2})")

# the first argument should be set by Memgraph
a = Node(1, ["Node"], {'id': 1})
b = Node(2, ["Node"], {'id': 2})
r = Relationship(1, "RELATED_TO", 1, 2, {'id': 1})

result = list(
    Match(memgraph.new_connection())
    .node(variable="a", node=a)
    .to(variable="r", relationship=r)
    .node(variable="b", node=b)
    .execute()
)[0]

print(result['a'])
print(result['b'])
print(result['r'])
```

## License

Copyright (c) 2016-2021 [Memgraph Ltd.](https://memgraph.com)

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
