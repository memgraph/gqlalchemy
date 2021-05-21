GQLAlchemy
=================

GQLAlchemy is library developed with purpose of assisting writing and running
queries on Memgraph DB. GQL supports high-level connection to Memgraph as well
as modular query builder.

GQLAlchemy is built on top of Memgraph's low-level client pymgclient
([pypi](https://pypi.org/project/pymgclient/) /
[documentation](https://memgraph.github.io/pymgclient/) /
[GitHub](https://github.com/memgraph/pymgclient)).

Installation
------------
To install `gqlalchemy`, simply run the following command:
```
pip install gqlalchemy
```

Search Example
--------------

When working with the `pymgclient`, Python developer can connect to database
and execute `MATCH` cypher query with following syntax:

```python
    import mgclient

    conn = mgclient.connect(host='127.0.0.1', port=7687)

    cursor = conn.cursor()
    cursor.execute("""
    MATCH (from:Node)-[:Connection]->(to:Node)
    RETURN from, to
    """)
    result = cursor.fetchone()
    conn.commit()

    for result in results:
        print(result['from'])
        print(result['to'])
```

As we can see, example above can be error-prone, because we do not have
abstractions for creating a database connection and `MATCH` query.

Now, rewrite the exact same query by using the functionality of `gqlalchemy`.

```python

    from gqlalchemy import Memgraph
    from gqlalchemy.build import Match

    db = Memgraph()

    results = Match().node("Node",variable="from")
                     .to("Connection")
                     .node("Node",variable="to")
                     .execute()

    for result in results:
        print(result['from'])
        print(result['to'])
```

License
-------

Copyright (c) 2016-2021 [Memgraph Ltd.](https://memgraph.com)

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
