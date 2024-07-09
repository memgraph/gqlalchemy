---
sidebar_label: models
title: gqlalchemy.models
---

## TriggerEventType Objects

```python
class TriggerEventType()
```

An enum representing types of trigger events.

## TriggerEventObject Objects

```python
class TriggerEventObject()
```

An enum representing types of trigger objects.

NODE -&gt; `()`
RELATIONSHIP -&gt; `--&gt;`

## TriggerExecutionPhase Objects

```python
class TriggerExecutionPhase()
```

An enum representing types of trigger objects.

Enum:
    BEFORE
    AFTER

## MemgraphKafkaStream Objects

```python
class MemgraphKafkaStream(MemgraphStream)
```

A class for creating and managing Kafka streams in Memgraph.

**Arguments**:

- `name` - A string representing the stream name.
- `topics` - A list of strings representing the stream topics.
- `transform` - A string representing the name of the transformation procedure.
- `consumer_group` - A string representing the consumer group.
- `name` - A string representing the batch interval.
- `name` - A string representing the batch size.
- `name` - A string or list of strings representing bootstrap server addresses.

#### to\_cypher

```python
def to_cypher() -> str
```

Converts Kafka stream to a Cypher clause.

## MemgraphPulsarStream Objects

```python
class MemgraphPulsarStream(MemgraphStream)
```

A class for creating and managing Pulsar streams in Memgraph.

**Arguments**:

- `name` - A string representing the stream name.
- `topics` - A list of strings representing the stream topics.
- `transform` - A string representing the name of the transformation procedure.
- `consumer_group` - A string representing the consumer group.
- `name` - A string representing the batch interval.
- `name` - A string representing the batch size.
- `name` - A string or list of strings representing bootstrap server addresses.

#### to\_cypher

```python
def to_cypher() -> str
```

Converts Pulsar stream to a Cypher clause.

## MemgraphTrigger Objects

```python
@dataclass(frozen=True, eq=True)
class MemgraphTrigger()
```

#### to\_cypher

```python
def to_cypher() -> str
```

Converts a Trigger to a cypher clause.

## GraphObject Objects

```python
class GraphObject(BaseModel)
```

#### \_\_init\_subclass\_\_

```python
def __init_subclass__(cls,
                      type=None,
                      label=None,
                      labels=None,
                      index=None,
                      db=None)
```

Stores the subclass by type if type is specified, or by class name
when instantiating a subclass.

#### \_convert\_to\_real\_type\_

```python
@classmethod
def _convert_to_real_type_(cls, data)
```

Converts the GraphObject class into the appropriate subclass.
This is used when deserialising a json representation of the class,
or the object returned from the GraphDatabase.

#### parse\_obj

```python
@classmethod
def parse_obj(cls, obj)
```

Used to convert a dictionary object into the appropriate
GraphObject.

## NodeMetaclass Objects

```python
class NodeMetaclass(BaseModel.__class__)
```

#### \_\_new\_\_

```python
def __new__(mcs, name, bases, namespace, **kwargs)
```

This creates the class `Node`. It also creates all subclasses
of `Node`. Whenever a class is defined as a subclass of `Node`,
`MyMeta.__new__` is called.

## Node Objects

```python
class Node(UniqueGraphObject, metaclass=NodeMetaclass)
```

#### has\_unique\_fields

```python
def has_unique_fields() -> bool
```

Returns True if the Node has any unique fields.

#### save

```python
def save(db: "Database") -> "Node"
```

Saves node to Memgraph.
If the node._id is not None it fetches the node with the same id from
Memgraph and updates it&#x27;s fields.
If the node has unique fields it fetches the nodes with the same unique
fields from Memgraph and updates it&#x27;s fields.
Otherwise it creates a new node with the same properties.
Null properties are ignored.

#### load

```python
def load(db: "Database") -> "Node"
```

Loads a node from Memgraph.
If the node._id is not None it fetches the node from Memgraph with that
internal id.
If the node has unique fields it fetches the node from Memgraph with
those unique fields set.
Otherwise it tries to find any node in Memgraph that has all properties
set to exactly the same values.
If no node is found or no properties are set it raises a GQLAlchemyError.

#### get\_or\_create

```python
def get_or_create(db: "Database") -> Tuple["Node", bool]
```

Return the node and a flag for whether it was created in the database.

**Arguments**:

- `db` - The database instance to operate on.
  

**Returns**:

  A tuple with the first component being the created graph node,
  and the second being a boolean that is True if the node
  was created in the database, and False if it was loaded instead.

## RelationshipMetaclass Objects

```python
class RelationshipMetaclass(BaseModel.__class__)
```

#### \_\_new\_\_

```python
def __new__(mcs, name, bases, namespace, **kwargs)
```

This creates the class `Relationship`. It also creates all
subclasses of `Relationship`. Whenever a class is defined as a
subclass of `Relationship`, `self.__new__` is called.

## Relationship Objects

```python
class Relationship(UniqueGraphObject, metaclass=RelationshipMetaclass)
```

#### save

```python
def save(db: "Database") -> "Relationship"
```

Saves a relationship to Memgraph.
If relationship._id is not None it finds the relationship in Memgraph
and updates it&#x27;s properties with the values in `relationship`.
If relationship._id is None, it creates a new relationship.
If you want to set a relationship._id instead of creating a new
relationship, use `load_relationship` first.

#### load

```python
def load(db: "Database") -> "Relationship"
```

Returns a relationship loaded from Memgraph.
If the relationship._id is not None it fetches the relationship from
Memgraph that has the same internal id.
Otherwise it returns the relationship whose relationship._start_node_id
and relationship._end_node_id and all relationship properties that
are not None match the relationship in Memgraph.
If there is no relationship like that in Memgraph, or if there are
multiple relationships like that in Memgraph, throws GQLAlchemyError.

#### get\_or\_create

```python
def get_or_create(db: "Database") -> Tuple["Relationship", bool]
```

Return the relationship and a flag for whether it was created in the database.

**Arguments**:

- `db` - The database instance to operate on.
  

**Returns**:

  A tuple with the first component being the created graph relationship,
  and the second being a boolean that is True if the relationship
  was created in the database, and False if it was loaded instead.

