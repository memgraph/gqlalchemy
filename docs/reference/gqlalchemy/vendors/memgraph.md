---
sidebar_label: memgraph
title: gqlalchemy.vendors.memgraph
---

#### create\_transaction

```python
def create_transaction(transaction_data) -> MemgraphTransaction
```

Create a MemgraphTransaction object from transaction data.

**Arguments**:

- `transaction_data` _dict_ - A dictionary containing transaction data.

**Returns**:

- `MemgraphTransaction` - A MemgraphTransaction object.

#### create\_terminated\_transaction

```python
def create_terminated_transaction(
        transaction_data) -> MemgraphTerminatedTransaction
```

Create a MemgraphTerminatedTransaction object from transaction data.

**Arguments**:

- `transaction_data` _dict_ - A dictionary containing transaction data.

**Returns**:

- `MemgraphTerminatedTransaction` - A MemgraphTerminatedTransaction object.

## Memgraph Objects

```python
class Memgraph(DatabaseClient)
```

#### get\_indexes

```python
def get_indexes() -> List[MemgraphIndex]
```

Returns a list of all database indexes (label and label-property types).

#### ensure\_indexes

```python
def ensure_indexes(indexes: List[MemgraphIndex]) -> None
```

Ensures that database indexes match input indexes.

#### get\_constraints

```python
def get_constraints(
) -> List[Union[MemgraphConstraintExists, MemgraphConstraintUnique]]
```

Returns a list of all database constraints (label and label-property types).

#### new\_connection

```python
def new_connection() -> Connection
```

Creates new Memgraph connection.

#### create\_stream

```python
def create_stream(stream: MemgraphStream) -> None
```

Create a stream.

#### start\_stream

```python
def start_stream(stream: MemgraphStream) -> None
```

Start a stream.

#### get\_streams

```python
def get_streams() -> List[str]
```

Returns a list of all streams.

#### drop\_stream

```python
def drop_stream(stream: MemgraphStream) -> None
```

Drop a stream.

#### create\_trigger

```python
def create_trigger(trigger: MemgraphTrigger) -> None
```

Creates a trigger.

#### get\_triggers

```python
def get_triggers() -> List[MemgraphTrigger]
```

Returns a list of all database triggers.

#### drop\_trigger

```python
def drop_trigger(trigger: MemgraphTrigger) -> None
```

Drop a trigger.

#### drop\_triggers

```python
def drop_triggers() -> None
```

Drops all triggers in the database.

#### init\_disk\_storage

```python
def init_disk_storage(on_disk_db: OnDiskPropertyDatabase) -> None
```

Adds and OnDiskPropertyDatabase to the database so that any property
that has a Field(on_disk=True) can be stored to and loaded from
an OnDiskPropertyDatabase.

#### remove\_on\_disk\_storage

```python
def remove_on_disk_storage() -> None
```

Removes the OnDiskPropertyDatabase from the database.

#### save\_node

```python
def save_node(node: Node) -> Node
```

Saves node to the database.
If the node._id is not None it fetches the node with the same id from
the database and updates it&#x27;s fields.
If the node has unique fields it fetches the nodes with the same unique
fields from the database and updates it&#x27;s fields.
Otherwise it creates a new node with the same properties.
Null properties are ignored.

#### load\_node

```python
def load_node(node: Node) -> Optional[Node]
```

Loads a node from the database.
If the node._id is not None it fetches the node from the database with that
internal id.
If the node has unique fields it fetches the node from the database with
those unique fields set.
Otherwise it tries to find any node in the database that has all properties
set to exactly the same values.
If no node is found or no properties are set it raises a GQLAlchemyError.

#### load\_relationship

```python
def load_relationship(relationship: Relationship) -> Optional[Relationship]
```

Returns a relationship loaded from the database.
If the relationship._id is not None it fetches the relationship from
the database that has the same internal id.
Otherwise it returns the relationship whose relationship._start_node_id
and relationship._end_node_id and all relationship properties that
are not None match the relationship in the database.
If there is no relationship like that in the database, or if there are
multiple relationships like that in the database, throws GQLAlchemyError.

#### save\_relationship

```python
def save_relationship(relationship: Relationship) -> Optional[Relationship]
```

Saves a relationship to the database.
If relationship._id is not None it finds the relationship in the database
and updates it&#x27;s properties with the values in `relationship`.
If relationship._id is None, it creates a new relationship.
If you want to set a relationship._id instead of creating a new
relationship, use `load_relationship` first.

#### get\_procedures

```python
def get_procedures(starts_with: Optional[str] = None,
                   update: bool = False) -> List["QueryModule"]
```

Return query procedures.

Maintains a list of query modules in the Memgraph object. If starts_with
is defined then return those modules that start with starts_with string.

**Arguments**:

- `starts_with` - Return those modules that start with this string.
  (Optional)
- `update` - Whether to update the list of modules in
  self.query_modules. (Optional)

#### add\_query\_module

```python
def add_query_module(file_path: str, module_name: str) -> "Memgraph"
```

Function for adding a query module in Python written language to Memgraph.
Example can be found in the functions below (with_kafka_stream, with_power_bi).

The module is synced dynamically then with the database to enable higher processing
capabilities.

**Arguments**:

- `file_name` _str_ - path to file containing module.
- `module_name` _str_ - name of the module.
  

**Returns**:

- `Memgraph` - Memgraph object.

#### with\_kafka\_stream

```python
def with_kafka_stream() -> "Memgraph"
```

Load kafka stream query module.

**Returns**:

- `Memgraph` - Memgraph instance

#### with\_power\_bi

```python
def with_power_bi() -> "Memgraph"
```

Load power_bi stream query module.

**Returns**:

- `Memgraph` - Memgraph instance

#### get\_storage\_mode

```python
def get_storage_mode() -> str
```

Returns the storage mode of the Memgraph instance.

#### set\_storage\_mode

```python
def set_storage_mode(storage_mode: MemgraphStorageMode) -> None
```

Sets the storage mode of the Memgraph instance.

#### get\_transactions

```python
def get_transactions() -> List[MemgraphTransaction]
```

Get all transactions in the database.

**Returns**:

- `List[MemgraphTransaction]` - A list of MemgraphTransaction objects.

#### terminate\_transactions

```python
def terminate_transactions(
        transaction_ids: List[str]) -> List[MemgraphTerminatedTransaction]
```

Terminate transactions in the database.

**Arguments**:

- `transaction_ids` _List[str]_ - A list of transaction ids to terminate.

**Returns**:

- `List[MemgraphTerminatedTransaction]` - A list of MemgraphTerminatedTransaction objects with info on their status.

