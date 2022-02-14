---
sidebar_label: models
title: gqlalchemy.models
---

## MemgraphKafkaStream Objects

```python
@dataclass(frozen=True, eq=True)
class MemgraphKafkaStream(MemgraphStream)
```

#### to\_cypher

```python
def to_cypher() -> str
```

Converts Kafka stream to a cypher clause.

## MemgraphPulsarStream Objects

```python
@dataclass(frozen=True, eq=True)
class MemgraphPulsarStream(MemgraphStream)
```

#### to\_cypher

```python
def to_cypher() -> str
```

Converts Pulsar stream to a cypher clause.

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
def __init_subclass__(cls, type=None, label=None, labels=None)
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
def save(db: "Memgraph") -> "Node"
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
def load(db: "Memgraph") -> "Node"
```

Loads a node from Memgraph.
If the node._id is not None it fetches the node from Memgraph with that
internal id.
If the node has unique fields it fetches the node from Memgraph with
those unique fields set.
Otherwise it tries to find any node in Memgraph that has all properties
set to exactly the same values.
If no node is found or no properties are set it raises a GQLAlchemyError.

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
def save(db: "Memgraph") -> "Relationship"
```

Saves a relationship to Memgraph.
If relationship._id is not None it finds the relationship in Memgraph
and updates it&#x27;s properties with the values in `relationship`.
If relationship._id is None, it creates a new relationship.
If you want to set a relationship._id instead of creating a new
relationship, use `load_relationship` first.

#### load

```python
def load(db: "Memgraph") -> "Relationship"
```

Returns a relationship loaded from Memgraph.
If the relationship._id is not None it fetches the relationship from
Memgraph that has the same internal id.
Otherwise it returns the relationship whose relationship._start_node_id
and relationship._end_node_id and all relationship properties that
are not None match the relationship in Memgraph.
If there is no relationship like that in Memgraph, or if there are
multiple relationships like that in Memgraph, throws GQLAlchemyError.

