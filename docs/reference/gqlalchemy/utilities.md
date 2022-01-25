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