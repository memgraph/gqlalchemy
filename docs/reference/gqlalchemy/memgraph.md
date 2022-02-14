---
sidebar_label: memgraph
title: gqlalchemy.memgraph
---

## Memgraph Objects

```python
class Memgraph()
```

#### execute\_and\_fetch

```python
def execute_and_fetch(query: str, connection: Connection = None) -> Iterator[Dict[str, Any]]
```

Executes Cypher query and returns iterator of results.

#### execute

```python
def execute(query: str, connection: Connection = None) -> None
```

Executes Cypher query without returning any results.

#### create\_index

```python
def create_index(index: MemgraphIndex) -> None
```

Creates an index (label or label-property type) in the database

#### drop\_index

```python
def drop_index(index: MemgraphIndex) -> None
```

Drops an index (label or label-property type) in the database

#### get\_indexes

```python
def get_indexes() -> List[MemgraphIndex]
```

Returns a list of all database indexes (label and label-property types)

#### ensure\_indexes

```python
def ensure_indexes(indexes: List[MemgraphIndex]) -> None
```

Ensures that database indexes match input indexes

#### create\_constraint

```python
def create_constraint(index: MemgraphConstraint) -> None
```

Creates a constraint (label or label-property type) in the database

#### drop\_constraint

```python
def drop_constraint(index: MemgraphConstraint) -> None
```

Drops a constraint (label or label-property type) in the database

#### get\_constraints

```python
def get_constraints() -> List[Union[MemgraphConstraintExists, MemgraphConstraintUnique]]
```

Returns a list of all database constraints (label and label-property types)

#### ensure\_constraints

```python
def ensure_constraints(constraints: List[Union[MemgraphConstraintExists, MemgraphConstraintUnique]]) -> None
```

Ensures that database constraints match input constraints

#### create\_stream

```python
def create_stream(stream: MemgraphStream) -> None
```

Create a stream

#### get\_streams

```python
def get_streams() -> List[str]
```

Returns a list of all streams

#### drop\_stream

```python
def drop_stream(stream: MemgraphStream) -> None
```

Drop a stream

#### drop\_database

```python
def drop_database()
```

Drops database by removing all nodes and edges

#### create\_trigger

```python
def create_trigger(trigger: MemgraphTrigger) -> None
```

Creates a trigger

#### get\_triggers

```python
def get_triggers() -> List[str]
```

Creates a trigger

#### drop\_trigger

```python
def drop_trigger(trigger) -> None
```

Drop a trigger

#### new\_connection

```python
def new_connection() -> Connection
```

Creates new Memgraph connection

#### init\_disk\_storage

```python
def init_disk_storage(on_disk_db: OnDiskPropertyDatabase) -> None
```

Adds and OnDiskPropertyDatabase to Memgraph so that any property
that has a Field(on_disk=True) can be stored to and loaded from
an OnDiskPropertyDatabase.

#### remove\_on\_disk\_storage

```python
def remove_on_disk_storage() -> None
```

Removes the OnDiskPropertyDatabase from Memgraph

#### get\_variable\_assume\_one

```python
def get_variable_assume_one(query_result: Iterator[Dict[str, Any]], variable_name: str) -> Any
```

Returns a single result from the query_result (usually gotten from
the execute_and_fetch function).
If there is more than one result, raises a GQLAlchemyError.

#### create\_node

```python
def create_node(node: Node) -> Optional[Node]
```

Creates a node in Memgraph from the `node` object.

#### save\_node

```python
def save_node(node: Node) -> Node
```

Saves node to Memgraph.
If the node._id is not None it fetches the node with the same id from
Memgraph and updates it&#x27;s fields.
If the node has unique fields it fetches the nodes with the same unique
fields from Memgraph and updates it&#x27;s fields.
Otherwise it creates a new node with the same properties.
Null properties are ignored.

#### save\_node\_with\_id

```python
def save_node_with_id(node: Node) -> Optional[Node]
```

Saves a node in Memgraph using the internal Memgraph id.

#### load\_node

```python
def load_node(node: Node) -> Optional[Node]
```

Loads a node from Memgraph.
If the node._id is not None it fetches the node from Memgraph with that
internal id.
If the node has unique fields it fetches the node from Memgraph with
those unique fields set.
Otherwise it tries to find any node in Memgraph that has all properties
set to exactly the same values.
If no node is found or no properties are set it raises a GQLAlchemyError.

#### load\_node\_with\_all\_properties

```python
def load_node_with_all_properties(node: Node) -> Optional[Node]
```

Loads a node from Memgraph with all equal property values.

#### load\_node\_with\_id

```python
def load_node_with_id(node: Node) -> Optional[Node]
```

Loads a node with the same internal Memgraph id.

#### load\_relationship

```python
def load_relationship(relationship: Relationship) -> Optional[Relationship]
```

Returns a relationship loaded from Memgraph.
If the relationship._id is not None it fetches the relationship from
Memgraph that has the same internal id.
Otherwise it returns the relationship whose relationship._start_node_id
and relationship._end_node_id and all relationship properties that
are not None match the relationship in Memgraph.
If there is no relationship like that in Memgraph, or if there are
multiple relationships like that in Memgraph, throws GQLAlchemyError.

#### load\_relationship\_with\_id

```python
def load_relationship_with_id(relationship: Relationship) -> Optional[Relationship]
```

Loads a relationship from Memgraph using the internal id.

#### load\_relationship\_with\_start\_node\_id\_and\_end\_node\_id

```python
def load_relationship_with_start_node_id_and_end_node_id(relationship: Relationship) -> Optional[Relationship]
```

Loads a relationship from Memgraph using start node and end node id
for which all properties of the relationship that are not None match.

#### save\_relationship

```python
def save_relationship(relationship: Relationship) -> Optional[Relationship]
```

Saves a relationship to Memgraph.
If relationship._id is not None it finds the relationship in Memgraph
and updates it&#x27;s properties with the values in `relationship`.
If relationship._id is None, it creates a new relationship.
If you want to set a relationship._id instead of creating a new
relationship, use `load_relationship` first.

#### save\_relationship\_with\_id

```python
def save_relationship_with_id(relationship: Relationship) -> Optional[Relationship]
```

Saves a relationship in Memgraph using the relationship._id.

#### create\_relationship

```python
def create_relationship(relationship: Relationship) -> Optional[Relationship]
```

Creates a new relationship in Memgraph.

