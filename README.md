# GQLAlchemy

![Github Action build-and-test](https://github.com/memgraph/gqlalchemy/workflows/Build%20and%20Test/badge.svg)
[![GitHub license](https://img.shields.io/github/license/memgraph/gqlalchemy)](https://github.com/memgraph/gqlalchemy/master/LICENSE)
[![PyPi release version](https://img.shields.io/pypi/v/gqlalchemy)](https://pypi.org/project/gqlalchemy)

GQLAlchemy is a library developed to assist in writing and running queries on Memgraph. GQLAlchemy supports high-level connection to Memgraph as well as modular query builder.

GQLAlchemy is built on top of Memgraph's low-level client `pymgclient`
([pypi](https://pypi.org/project/pymgclient/) /
[documentation](https://memgraph.github.io/pymgclient/) /
[GitHub](https://github.com/memgraph/pymgclient)).

## Installation

To install `gqlalchemy`, simply run the following command:
```
pip install gqlalchemy
```

## Build & Test

The project uses [poetry](https://python-poetry.org/) to build the GQLAlchemy. To build and run tests execute the following commands:
`poetry install`

Before running tets make sure you have an active memgraph instance, then you can run:
`poetry run pytest .`

## GQLAlchemy example


When working with the `gqlalchemy`, Python developer can connect to database and execute `MATCH` cypher query with following syntax:

```python
from gqlalchemy import Memgraph

memgraph = Memgraph("127.0.0.1", 7687)
memgraph.execute_query("CREATE (:Node)-[:Connection]->(:Node)")
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

results = Match().node("Node",variable="from")
                 .to("Connection")
                 .node("Node",variable="to")
                 .execute()

for result in results:
    print(result['from'])
    print(result['to'])
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
