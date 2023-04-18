---
sidebar_label: database_client
title: gqlalchemy.vendors.database_client
---

## DatabaseClient Objects

```python
class DatabaseClient(ABC)
```

#### execute\_and\_fetch

```python
def execute_and_fetch(
        query: str,
        parameters: Dict[str, Any] = {},
        connection: Connection = None) -> Iterator[Dict[str, Any]]
```

Executes Cypher query and returns iterator of results.

#### execute

```python
def execute(query: str,
            parameters: Dict[str, Any] = {},
            connection: Connection = None) -> None
```

Executes Cypher query without returning any results.

#### create\_index

```python
def create_index(index: Index) -> None
```

Creates an index (label or label-property type) in the database.

#### drop\_index

```python
def drop_index(index: Index) -> None
```

Drops an index (label or label-property type) in the database.

#### get\_indexes

```python
@abstractmethod
def get_indexes() -> List[Index]
```

Returns a list of all database indexes (label and label-property types).

#### ensure\_indexes

```python
@abstractmethod
def ensure_indexes(indexes: List[Index]) -> None
```

Ensures that database indexes match input indexes.

#### drop\_indexes

```python
def drop_indexes() -> None
```

Drops all indexes in the database

#### create\_constraint

```python
def create_constraint(index: Constraint) -> None
```

Creates a constraint (label or label-property type) in the database.

#### drop\_constraint

```python
def drop_constraint(index: Constraint) -> None
```

Drops a constraint (label or label-property type) in the database.

#### get\_constraints

```python
@abstractmethod
def get_constraints() -> List[Constraint]
```

Returns a list of all database constraints (label and label-property types).

#### ensure\_constraints

```python
def ensure_constraints(constraints: List[Constraint]) -> None
```

Ensures that database constraints match input constraints.

#### drop\_database

```python
def drop_database()
```

Drops database by removing all nodes and edges.

#### new\_connection

```python
@abstractmethod
def new_connection() -> Connection
```

Creates new database connection.

#### get\_variable\_assume\_one

```python
def get_variable_assume_one(query_result: Iterator[Dict[str, Any]],
                            variable_name: str) -> Any
```

Returns a single result from the query_result (usually gotten from
the execute_and_fetch function).
If there is more than one result, raises a GQLAlchemyError.

#### create\_node

```python
def create_node(node: Node) -> Optional[Node]
```

Creates a node in database from the `node` object.

#### save\_node

```python
@abstractmethod
def save_node(node: Node) -> Node
```

Saves node to database.
If the node._id is not None, it fetches the node with the same id from
the database and updates it&#x27;s fields.
If the node has unique fields it fetches the nodes with the same unique
fields from the database and updates it&#x27;s fields.
Otherwise it creates a new node with the same properties.
Null properties are ignored.

#### save\_nodes

```python
def save_nodes(nodes: List[Node]) -> None
```

Saves a list of nodes to the database.

#### save\_node\_with\_id

```python
def save_node_with_id(node: Node) -> Optional[Node]
```

Saves a node to the database using the internal id.

#### load\_node

```python
@abstractmethod
def load_node(node: Node) -> Optional[Node]
```

Loads a node from the database.
If the node._id is not None, it fetches the node from the database with that
internal id.
If the node has unique fields it fetches the node from the database with
those unique fields set.
Otherwise it tries to find any node in the database that has all properties
set to exactly the same values.
If no node is found or no properties are set it raises a GQLAlchemyError.

#### load\_node\_with\_all\_properties

```python
def load_node_with_all_properties(node: Node) -> Optional[Node]
```

Loads a node from the database with all equal property values.

#### load\_node\_with\_id

```python
def load_node_with_id(node: Node) -> Optional[Node]
```

Loads a node with the same internal database id.

#### load\_relationship

```python
@abstractmethod
def load_relationship(relationship: Relationship) -> Optional[Relationship]
```

Returns a relationship loaded from the database.
If the relationship._id is not None, it fetches the relationship from
the database that has the same internal id.
Otherwise it returns the relationship whose relationship._start_node_id
and relationship._end_node_id and all relationship properties that
are not None match the relationship in the database.
If there is no relationship like that in database, or if there are
multiple relationships like that in database, throws GQLAlchemyError.

#### load\_relationship\_with\_id

```python
def load_relationship_with_id(
        relationship: Relationship) -> Optional[Relationship]
```

Loads a relationship from the database using the internal id.

#### load\_relationship\_with\_start\_node\_id\_and\_end\_node\_id

```python
def load_relationship_with_start_node_id_and_end_node_id(
        relationship: Relationship) -> Optional[Relationship]
```

Loads a relationship from the database using start node and end node id
for which all properties of the relationship that are not None match.

#### save\_relationship

```python
@abstractmethod
def save_relationship(relationship: Relationship) -> Optional[Relationship]
```

Saves a relationship to the database.
If relationship._id is not None it finds the relationship in the database
and updates it&#x27;s properties with the values in `relationship`.
If relationship._id is None, it creates a new relationship.
If you want to set a relationship._id instead of creating a new
relationship, use `load_relationship` first.

#### save\_relationships

```python
def save_relationships(relationships: List[Relationship]) -> None
```

Saves a list of relationships to the database.

#### save\_relationship\_with\_id

```python
def save_relationship_with_id(
        relationship: Relationship) -> Optional[Relationship]
```

Saves a relationship to the database using the relationship._id.

#### create\_relationship

```python
def create_relationship(relationship: Relationship) -> Optional[Relationship]
```

Creates a new relationship in the database.

