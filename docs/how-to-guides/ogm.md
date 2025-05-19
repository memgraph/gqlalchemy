# How to use object graph mapper

!!! info 
    You can also use this feature with Neo4j:

    ```python
    db = Neo4j(host="localhost", port="7687", username="neo4j", password="test")
    ```

Through this guide, you will learn how to use the GQLAlchemy object graph mapper to:

- [**Map nodes and relationships**](#map-nodes-and-relationships)
- [**Save nodes and relationships**](#save-nodes-and-relationships)
- [**Load nodes and relationships**](#load-nodes-and-relationships)
    - [**Find node properties**](#find-node-properties)
    - [**Create relationship between existing nodes**](#create-relationship-between-existing-nodes)
    - [**Merge nodes and relationships**](#merge-nodes-and-relationships)
- [**Create indexes**](#create-indexes)
- [**Create constraints**](#create-constraints)

>Hopefully, this guide will teach you how to properly use GQLAlchemy object graph mapper. If you
>have any more questions, join our community and ping us on [Discord](https://discord.gg/memgraph).

!!! info 
    To test the above features, you must [install GQLAlchemy](../installation.md) and have a running Memgraph instance. If you're unsure how to run Memgraph, check out the Memgraph [Quick start](https://memgraph.com/docs/getting-started)).

## Map nodes and relationships

First, we need to import all the necessary classes from GQLAlchemy:

```python
from gqlalchemy import Memgraph, Node, Relationship
```

After that, instantiate Memgraph and **create classes representing nodes**.

```python
db = Memgraph()

class User(Node):
    id: str
    username: str

class Streamer(User):
    id: str
    username: str
    followers: int

class Language(Node):
    name: str
```

<Neo4jOption/>

`Node` is a Python class which maps to a graph object in Memgraph. `User`, `Streamer` and `Language` are classes which inherit from `Node` and they map to a label in a graph database. Class `User` maps to a single `:User` label with properties `id` and `username`, class `Streamer` maps to multiple labels `:Streamer:User` with properties `id`, `username` and `followers`, and class Language maps to a single `:Language` label with `name` property.

In a similar way, you can **create relationship classes**:

```python
class ChatsWith(Relationship, type="CHATS_WITH"):
    last_chatted: str

class Speaks(Relationship):
    since: str
```

The code above maps to a relationship of type `CHATS_WITH` with the string property `last_chatted` and to a relationship of type `SPEAKS` with the string property since. There was no need to add type argument to `Speaks` class, since the label it maps to will automatically be set to uppercase class name in a graph database. 

If you want to **create a node class without any properties**, use `pass` statement:

```python
class User(Node):
    pass
```

For **relationships without any properties** also use `pass` statement:

```python
class ChatsWith(Relationship, type="CHATS_WITH"):
    pass
```

!!! info 
    Objects are modeled using GQLAlchemy’s Object Graph Mapper (OGM) which provides schema validation, so you can be sure that the data inside Memgraph is accurate. If you tried saving data that is not following the defined schema, you will get a `ValidationError`. 

To use the above classes, you need to [save](#save-nodes-and-relationships) or [load](#load-nodes-and-relationships) data first. 

## Save nodes and relationships

In order to save a node using the object graph mapper, first define node classes:

```python
from gqlalchemy import Memgraph, Node, Relationship

db = Memgraph()

class User(Node):
    id: str 
    username: str

class Language(Node):
    name: str
```

The above classes map to `User` and `Language` nodes in the database. `User` nodes have properties `id` and `username` and `Language` nodes have property `name`. 

<Neo4jOption/>

To **create and save node objects** use the following code:

```python
john = User(id="1", username="John").save(db)
jane = Streamer(id="2", username="janedoe", followers=111).save(db)
language = Language(name="en").save(db)
```

There is **another way of creating and saving node objects**:

```python
john = User(id="1", username="John")
db.save_node(john)

jane = Streamer(id="2", username="janedoe", followers=111)
db.save_node(jane)

language = Language(name="en")
db.save_node(language)
```

!!! danger 
    The `save()` and `save_node()` procedures will save nodes in Memgraph even if they already exist. This means that if you run the above code twice, you will have duplicate nodes in the database. To avoid that, [add constraints](#create-constraints) for properties or first [load](#load-nodes-and-relationships) the node from the database to check if it already exists.

To **save relationships** using the object graph mapper, first define relationship classes:

```python
class ChatsWith(Relationship, type="CHATS_WITH"):
    last_chatted: str

class Speaks(Relationship):
    since: str
```

The code above maps to a relationship of type `CHATS_WITH` with the string property `last_chatted` and to a relationship of type `SPEAKS` with the string property since. There was no need to add type argument to `Speaks` class, since the label it maps to will automatically be set to uppercase class name in a graph database. 

To save relationships, create them with appropriate start and end nodes and then use the `save()` procedure:

```python
ChatsWith(
    _start_node_id=john._id, _end_node_id=jane._id, last_chatted="2023-02-14"
).save(db)

Speaks(_start_node_id=john._id, _end_node_id=language._id, since="2023-02-14").save(db)
```

The property `_id` is an **internal Memgraph id** - an id given to each node upon saving to the database. This means that you have to first load nodes from the database or save them to variables in order to create a relationship between them.

!!! info 
    Objects are modeled using GQLAlchemy’s Object Graph Mapper (OGM) which provides schema validation, so you can be sure that the data inside Memgraph is accurate. If you tried saving data that is not following the defined schema, you will get `ValidationError`. 

**Another way of saving relationships** is by using the `save_relationship()` procedure:

```python
db.save_relationship(
    ChatsWith(_start_node_id=john._id, _end_node_id=jane._id, last_chatted="2023-02-14")
)

db.save_relationship(
    Speaks(_start_node_id=user._id, _end_node_id=language._id, since="2023-02-14")
)
```

!!! danger 
    The `save()` and `save_relationship()` procedures will save relationships in Memgraph even if they already exist. This means that if you run the above code twice, you will have duplicate relationships in the database. To avoid that, first [load](#load-nodes-and-relationships) the relationship from the database to check if it already exists.

## Load nodes and relationships

Let's continue with the previously defined classes:

```python
class User(Node):
    id: str
    username: str


class Streamer(User):
    id: str
    username: str
    followers: int


class Language(Node):
    name: str


class ChatsWith(Relationship, type="CHATS_WITH"):
    last_chatted: str


class Speaks(Relationship, type="SPEAKS"):
    since: str
```

For this example, we will also use previously saved nodes:

```python
jane = Streamer(id="2", username="janedoe", followers=111).save(db)
language = Language(name="en").save(db)
```

There are many examples of when **loading a node** from the database may come in
handy, but let's cover the two most common. 

### Find node properties

Suppose you just have the `id` of the streamer and you want to know the
streamer's name. You have to load that node from the database to check its
`name` property. If you try running the following code: 

```python
loaded_streamer = Streamer(id="2").load(db=db)
```

you will get a `ValidationError`. This happens because the schema you defined expects `username` and `followers` properties for the `Streamer` instance. To avoid that, define Streamer class like this:

```python
class Streamer(User):
    id: str
    username: Optional[str]
    followers: Optional[str]
```

The above class definition is not ideal, since it is not enforcing schema as before. To do that, [add constraints](#create-constraints).

If you try loading the node again, the following code:

```python
loaded_streamer = Streamer(id="2").load(db=db)
```

will print out the username of the streamer whose `id` equals `"2"`, that is, `"janedoe"`. 

### Create relationship between existing nodes

To create a new relationship of type `SPEAKS`, between already saved streamer and language you need to first load those nodes:

```python
loaded_streamer = Streamer(id="2").load(db=db)
loaded_language = Language(name="en").load(db=db)
```

The load() method returns one result above, since it matches unique database objects. When the matching object is not unique, the `load()` method will return a list of matching results. 

To **create a relationship** between `loaded_streamer` and `loaded_language` nodes run:

```python
Speaks(
    _start_node_id=loaded_streamer._id,
    _end_node_id=loaded_language._id,
    since="2023-02-15",
).save(db)
```

In the above example, the relationship will be created even if it existed before. To avoid that, check [merging nodes and relationships section](#merging-nodes-and-relationships).

To **load a relationship** from the database based on its start and end node, first mark its property as optional:

```python
class Speaks(Relationship, type="SPEAKS"):
    since: Optional[str]
```

The above class definition is not ideal, since it is not enforcing schema as before. To do that, [add constraints](#create-constraints).

To load the relationship, run the following: 

```python
loaded_speaks = Speaks(
        _start_node_id=streamer._id,
        _end_node_id=language._id
    ).load(db)
```

It's easy to get its `since` property:

```python
print(loaded_speaks.since)
```
The output of the above print is `2023-02-15`.

### Merge nodes and relationships

To **merge nodes**, first try loading them from the database to see if they exist, and if not, save them:

```python
try:
    streamer = Streamer(id="3").load(db=db)
except:
    print("Creating new Streamer node in the database.")
    streamer = Streamer(id="3", username="anne", followers=222).save(db=db)
```

To **merge relationships** first try loading them from the database to see if they exist, and if not, save them:

```python
try:
    speaks = Speaks(_start_node_id=streamer._id, _end_node_id=language._id).load(db)
except:
    print("Creating new Speaks relationship in the database.")
    speaks = Speaks(
        _start_node_id=streamer._id,
        _end_node_id=language._id,
        since="2023-02-20",
    ).save(db)
```

## Create indexes

To create indexes you need to do one additional import:

```python
from gqlalchemy import Field
```

The `Field` class originates from `pydantic`, a Python library data validation and settings management. Here is the example of how `Field` class helps in creating label and label-property indexes:

```python
class User(Node):
    id: str = Field(index=True, db=db)
    username: str

class Language(Node, index=True, db=db):
    name: str
```

The indexes will be set on class definition, before instantiation. This ensures that the index creation is run only once for each index type. To check which indexes were created, run:

```python
print(db.get_indexes())
```

The other way to create indexes is by creating an instance of `MemgraphIndex` class. For example, to create label index `NodeOne` and label-property index `NodeOne(name)`, run the following code:

```python
from gqlalchemy import Memgraph
from gqlalchemy.models import MemgraphIndex

db = Memgraph()

index1 = MemgraphIndex("NodeOne")
index2 = MemgraphIndex("NodeOne", "name")

db.create_index(index1)
db.create_index(index2)
```

Besides label and label-property indexes, Memgraph supports label-property composite, edge-type, edge-type property, global edge property and point indexes. 
Here is an example of how to create each:

```python
label_index = MemgraphIndex("Person")
label_prop_index = MemgraphIndex("Person", "name")
label_composite_index = MemgraphIndex("Person", ("name", "age"))
edge_type_index = MemgraphIndex("REL", None, index_type="EDGE_INDEX_TYPE")
edge_type_property_index = MemgraphIndex("REL", "name", index_type="EDGE_INDEX_TYPE")
global_edge_index = MemgraphIndex(None, "name", index_type="EDGE_GLOBAL_INDEX_TYPE")
point_index = MemgraphIndex("Person", "year", index_type="POINT_INDEX_TYPE")

memgraph.create_index(label_index)
memgraph.create_index(label_prop_index)
memgraph.create_index(label_composite_index)
memgraph.create_index(edge_type_index)
memgraph.create_index(edge_type_property_index)
memgraph.create_index(global_edge_index)
memgraph.create_index(point_index)
```

The `get_indexes()`, `drop_index()`, `ensure_indexes()` and `drop_indexes()` methods will work for all index types. 

The exception here is the vector index, which is currently treated a bit differently in Memgraph.

To learn more about indexes, head over to the [indexing reference guide](https://memgraph.com/docs/fundamentals/indexes).

## Create constraints 

Uniqueness constraint enforces that each `label`, `property_set` pair is unique. Here is how you can **enforce uniqueness constraint** with GQLAlchemy's OGM:

```python
class Language(Node):
    name: str = Field(unique=True, db=db)
```

The above is the same as running the Cypher query:

```cypher
CREATE CONSTRAINT ON (n:Language) ASSERT n.name IS UNIQUE;
```

Read more about it at [uniqueness constraint how-to guide](https://memgraph.com/docs/fundamentals/constraints).

Existence constraint enforces that each vertex that has a specific label also must have the specified property.  Here is how you can **enforce existence constraint** with GQLAlchemy's OGM:

```python
class Streamer(User):
    id: str
    username: Optional[str] = Field(exists=True, db=db)
    followers: Optional[str]
```

The above is the same as running the Cypher query:

```cypher
CREATE CONSTRAINT ON (n:Streamer) ASSERT EXISTS (n.username);
```

Read more about it at [existence constraint how-to guide](https://memgraph.com/docs/fundamentals/constraints).

To check which constraints have been created, run: 

```python
print(db.get_constraints())
```

## Full code example

The above mentioned examples can be merged into a working code example which you can run. Here is the code:

```python
from gqlalchemy import Memgraph, Node, Relationship, Field
from typing import Optional

db = Memgraph()

class User(Node):
    id: str = Field(index=True, db=db)
    username: str = Field(exists=True, db=db)

class Streamer(User):
    id: str
    username: Optional[str] = Field(exists=True, db=db)
    followers: Optional[str]

class Language(Node, index=True, db=db):
    name: str = Field(unique=True, db=db)

class ChatsWith(Relationship, type="CHATS_WITH"):
    last_chatted: str

class Speaks(Relationship, type="SPEAKS"):
    since: Optional[str]

john = User(id="1", username="John").save(db)
jane = Streamer(id="2", username="janedoe", followers=111).save(db)
language = Language(name="en").save(db)

ChatsWith(
    _start_node_id=john._id, _end_node_id=jane._id, last_chatted="2023-02-14"
).save(db)

Speaks(_start_node_id=john._id, _end_node_id=language._id, since="2023-02-14").save(db)

streamer = Streamer(id="2").load(db=db)
language = Language(name="en").load(db=db)

speaks = Speaks(
    _start_node_id=streamer._id,
    _end_node_id=language._id,
    since="2023-02-20",
).save(db)

speaks = Speaks(_start_node_id=streamer._id, _end_node_id=language._id).load(db)
print(speaks.since)

try:
    streamer = Streamer(id="3").load(db=db)
except:
    print("Creating new Streamer node in the database.")
    streamer = Streamer(id="3", username="anne", followers=222).save(db=db)

try:
    speaks = Speaks(_start_node_id=streamer._id, _end_node_id=language._id).load(db)
except:
    print("Creating new Speaks relationship in the database.")
    speaks = Speaks(
        _start_node_id=streamer._id,
        _end_node_id=language._id,
        since="2023-02-20",
    ).save(db)

print(db.get_indexes())
print(db.get_constraints())
```

>Hopefully, this guide has taught you how to properly use GQLAlchemy object graph mapper. If you
>have any more questions, join our community and ping us on [Discord](https://discord.gg/memgraph).
