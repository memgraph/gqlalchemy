---
sidebar_label: disk_storage
title: gqlalchemy.disk_storage
---

## OnDiskPropertyDatabase Objects

```python
class OnDiskPropertyDatabase(ABC)
```

An abstract class for implementing on-disk storage features with specific databases.

#### save\_node\_property

```python
def save_node_property(node_id: int, property_name: str,
                       property_value: str) -> None
```

Saves a node property to an on disk database.

#### load\_node\_property

```python
def load_node_property(node_id: int, property_name: str,
                       property_value: str) -> Optional[str]
```

Loads a node property from an on disk database.

#### delete\_node\_property

```python
def delete_node_property(node_id: int, property_name: str,
                         property_value: str) -> None
```

Deletes a node property from an on disk database.

#### save\_relationship\_property

```python
def save_relationship_property(relationship_id: int, property_name: str,
                               property_value: str) -> None
```

Saves a relationship property to an on disk database.

#### load\_relationship\_property

```python
def load_relationship_property(relationship_id: int, property_name: str,
                               property_value: str) -> Optional[str]
```

Loads a relationship property from an on disk database.

#### delete\_relationship\_property

```python
def delete_relationship_property(node_id: int, property_name: str,
                                 property_value: str) -> None
```

Deletes a node property from an on disk database.

#### drop\_database

```python
def drop_database() -> None
```

Deletes all entries from the on disk database.

## SQLitePropertyDatabase Objects

```python
class SQLitePropertyDatabase(OnDiskPropertyDatabase)
```

#### execute\_query

```python
def execute_query(query: str) -> List[str]
```

Executes an SQL query on the on disk property database.

**Arguments**:

- `query` - A string representing an SQL query.
  

**Returns**:

  A list of strings representing the results of the query.

#### drop\_database

```python
def drop_database() -> None
```

Deletes all properties in the database.

#### save\_node\_property

```python
def save_node_property(node_id: int, property_name: str,
                       property_value: str) -> None
```

Saves a node property to an on disk database.

**Arguments**:

- `node_id` - An integer representing the internal id of the node.
- `property_name` - A string representing the name of the property.
- `property_value` - A string representing the value of the property.

#### load\_node\_property

```python
def load_node_property(node_id: int, property_name: str) -> Optional[str]
```

Loads a node property from an on disk database.

**Arguments**:

- `node_id` - An integer representing the internal id of the node.
- `property_name` - A string representing the name of the property.
  

**Returns**:

  An optional string representing the property value.

#### delete\_node\_property

```python
def delete_node_property(node_id: int, property_name: str) -> None
```

Deletes a node property from an on disk database.

**Arguments**:

- `node_id` - An integer representing the internal id of the node.
- `property_name` - A string representing the name of the property.

#### save\_relationship\_property

```python
def save_relationship_property(relationship_id: int, property_name: str,
                               property_value: str) -> None
```

Saves a relationship property to an on disk database.

**Arguments**:

- `relationship_id` - An integer representing the internal id of the relationship.
- `property_name` - A string representing the name of the property.
- `property_value` - A string representing the value of the property.

#### load\_relationship\_property

```python
def load_relationship_property(relationship_id: int,
                               property_name: str) -> Optional[str]
```

Loads a relationship property from an on disk database.

**Arguments**:

- `relationship_id` - An integer representing the internal id of the relationship.
- `property_name` - A string representing the name of the property.
  

**Returns**:

  An optional string representing the property value.

#### delete\_relationship\_property

```python
def delete_relationship_property(relationship_id: int,
                                 property_name: str) -> None
```

Deletes a node property from an on disk database.

**Arguments**:

- `relationship_id` - An integer representing the internal id of the relationship.
- `property_name` - A string representing the name of the property.

