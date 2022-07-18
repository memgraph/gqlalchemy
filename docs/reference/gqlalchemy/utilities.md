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
def to_cypher_properties(properties: Optional[Dict[str, Any]] = None, config=None) -> str
```

Converts properties to a Cypher key-value properties.

#### to\_cypher\_labels

```python
def to_cypher_labels(labels: Union[str, List[str], None]) -> str
```

Converts labels to a Cypher label definition.

#### to\_cypher\_qm\_arguments

```python
def to_cypher_qm_arguments(arguments: Optional[Union[str, Tuple[Union[str, int, float]]]]) -> str
```

Converts query module arguments to a valid Cypher string of query module arguments.

## PropertyVariable Objects

```python
class PropertyVariable()
```

Class for support of using a variable as a node or edge property. Used
to avoid the quotes given to property values.

