---
sidebar_label: utilities
title: gqlalchemy.utilities
---

#### to\_cypher\_value

```python
def to_cypher_value(value: Any, config: NetworkXCypherConfig = None) -> str
```

Converts value to a valid Cypher type.

#### to\_cypher\_properties

```python
def to_cypher_properties(properties: Optional[Dict[str, Any]] = None,
                         config=None) -> str
```

Converts properties to a Cypher key-value properties.

#### to\_cypher\_labels

```python
def to_cypher_labels(labels: Union[str, List[str], None]) -> str
```

Converts labels to a Cypher label definition.

#### to\_cypher\_qm\_arguments

```python
def to_cypher_qm_arguments(
        arguments: Optional[Union[str, Tuple[Union[str, int, float]]]]) -> str
```

Converts query module arguments to a valid Cypher string of query module arguments.

## CypherObject Objects

```python
class CypherObject(ABC)
```

Abstract method representing an object in cypher syntax, such as nodes
and relationships.

## CypherNode Objects

```python
class CypherNode(CypherObject)
```

Represents a node in Cypher syntax.

## RelationshipDirection Objects

```python
class RelationshipDirection(Enum)
```

Defines the direction of CypherRelationship object.

## CypherRelationship Objects

```python
class CypherRelationship(CypherObject)
```

Represents a relationship in Cypher syntax. Multiple types can not be
set on a relationship, only queried.

## CypherVariable Objects

```python
class CypherVariable()
```

Class for support of using a variable as value in Cypher. Used
to avoid the quotes given to property values and query module arguments.

