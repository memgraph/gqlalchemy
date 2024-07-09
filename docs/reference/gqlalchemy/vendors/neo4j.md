---
sidebar_label: neo4j
title: gqlalchemy.vendors.neo4j
---

## Neo4j Objects

```python
class Neo4j(DatabaseClient)
```

#### get\_indexes

```python
def get_indexes() -> List[Neo4jIndex]
```

Returns a list of all database indexes (label and label-property types).

#### ensure\_indexes

```python
def ensure_indexes(indexes: List[Neo4jIndex]) -> None
```

Ensures that database indexes match input indexes.

#### get\_constraints

```python
def get_constraints(
) -> List[Union[Neo4jConstraintExists, Neo4jConstraintUnique]]
```

Returns a list of all database constraints (label and label-property types).

#### new\_connection

```python
def new_connection() -> Connection
```

Creates new Neo4j connection.

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

