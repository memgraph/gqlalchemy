---
sidebar_label: translator
title: gqlalchemy.transformations.translators.translator
---

## Translator Objects

```python
class Translator(ABC)
```

#### to\_cypher\_queries

```python
@abstractmethod
def to_cypher_queries(graph)
```

Abstract method which doesn&#x27;t know how to produce cypher queries for a specific graph type and thus needs to be overridden.

**Arguments**:

- `graph` - Can be of any type supported by the derived Translator object.
  

**Raises**:

- `NotImplementedError` - The method must be override by a specific translator.

#### get\_instance

```python
@abstractmethod
def get_instance()
```

Abstract method which doesn&#x27;t know how to create the concrete instance so it needs to be overridden.

**Raises**:

- `NotImplementedError` - The method must be override by a specific translator.

#### validate\_features

```python
@classmethod
def validate_features(cls, features: List, expected_num: int)
```

Return true if features are okay to be set on all nodes/features.

**Arguments**:

- `features` - To be set on all nodes. It can be anything that can be converted to torch tensor.
- `expected_num` - This can be number of nodes or number of edges depending on whether features will be set on nodes or edges.

**Returns**:

  None if features cannot be set or tensor of same features.

#### get\_all\_edges\_from\_db

```python
def get_all_edges_from_db()
```

Returns all edges from the database.

**Returns**:

  Query results when finding all edges.

#### get\_all\_isolated\_nodes\_from\_db

```python
def get_all_isolated_nodes_from_db()
```

Returns all isolated nodes from the database.

**Returns**:

  Query results for finding all isolated nodes.

