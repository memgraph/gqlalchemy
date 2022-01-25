---
sidebar_label: query_builder
title: gqlalchemy.query_builder
---

## WhereConditionPartialQuery Objects

```python
class WhereConditionPartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Constructs a where partial query.

## NodePartialQuery Objects

```python
class NodePartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Constructs a node partial query.

## EdgePartialQuery Objects

```python
class EdgePartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Constructs an edge partial query.

## UnwindPartialQuery Objects

```python
class UnwindPartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Constructs an unwind partial query.

#### dict\_to\_alias\_statement

```python
def dict_to_alias_statement(alias_dict: Dict[str, str]) -> str
```

Creates a string expression of alias statements from a dictionary of
expression, variable name dictionary.

## WithPartialQuery Objects

```python
class WithPartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Creates a WITH statement Cypher partial query.

## UnionPartialQuery Objects

```python
class UnionPartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Creates a UNION statement Cypher partial query.

## DeletePartialQuery Objects

```python
class DeletePartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Creates a DELETE statement Cypher partial query.

## RemovePartialQuery Objects

```python
class RemovePartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Creates a REMOVE statement Cypher partial query.

## YieldPartialQuery Objects

```python
class YieldPartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Creates a YIELD statement Cypher partial query.

## ReturnPartialQuery Objects

```python
class ReturnPartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Creates a RETURN statement Cypher partial query.

## OrderByPartialQuery Objects

```python
class OrderByPartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Creates a ORDER BY statement Cypher partial query.

## LimitPartialQuery Objects

```python
class LimitPartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Creates a LIMIT statement Cypher partial query.

## SkipPartialQuery Objects

```python
class SkipPartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Creates a SKIP statement Cypher partial query.

## DeclarativeBase Objects

```python
class DeclarativeBase(ABC)
```

#### match

```python
def match(optional: bool = False) -> "DeclarativeBase"
```

Creates a MATCH statement Cypher partial query.

#### merge

```python
def merge() -> "DeclarativeBase"
```

Creates a MERGE statement Cypher partial query.

#### create

```python
def create() -> "DeclarativeBase"
```

Creates a CREATE statement Cypher partial query.

#### call

```python
def call(procedure: str, arguments: Optional[str] = None) -> "DeclarativeBase"
```

Creates a CALL statement Cypher partial query.

#### node

```python
def node(labels: Union[str, List[str], None] = "", variable: Optional[str] = None, node: Optional["Node"] = None, **kwargs, ,) -> "DeclarativeBase"
```

Creates a node Cypher partial query.

#### to

```python
def to(edge_label: Optional[str] = "", directed: Optional[bool] = True, variable: Optional[str] = None, relationship: Optional["Relationship"] = None, **kwargs, ,) -> "DeclarativeBase"
```

Creates a relationship Cypher partial query with a &#x27;-&gt;&#x27; sign.

#### from\_

```python
def from_(edge_label: Optional[str] = "", directed: Optional[bool] = True, variable: Optional[str] = None, relationship: Optional["Relationship"] = None, **kwargs, ,) -> "Match"
```

Creates a relationship Cypher partial query with a &#x27;&lt;-&#x27; sign.

#### where

```python
def where(property: str, operator: str, value: Any) -> "DeclarativeBase"
```

Creates a WHERE statement Cypher partial query.

#### and\_where

```python
def and_where(property: str, operator: str, value: Any) -> "DeclarativeBase"
```

Creates a AND (expression) statement Cypher partial query.

#### or\_where

```python
def or_where(property: str, operator: str, value: Any) -> "DeclarativeBase"
```

Creates a OR (expression) statement Cypher partial query.

#### unwind

```python
def unwind(list_expression: str, variable: str) -> "DeclarativeBase"
```

Creates a UNWIND statement Cypher partial query.

#### with\_

```python
def with_(results: Optional[Dict[str, str]] = {}) -> "DeclarativeBase"
```

Creates a WITH statement Cypher partial query.

#### union

```python
def union(include_duplicates: Optional[bool] = True) -> "DeclarativeBase"
```

Creates a UNION statement Cypher partial query.

#### delete

```python
def delete(variable_expressions: List[str], detach: Optional[bool] = False) -> "DeclarativeBase"
```

Creates a DELETE statement Cypher partial query.

#### remove

```python
def remove(items: List[str]) -> "DeclarativeBase"
```

Creates a REMOVE statement Cypher partial query.

#### yield\_

```python
def yield_(results: Optional[Dict[str, str]] = {}) -> "DeclarativeBase"
```

Creates a YIELD statement Cypher partial query.

#### return\_

```python
def return_(results: Optional[Dict[str, str]] = {}) -> "DeclarativeBase"
```

Creates a RETURN statement Cypher partial query.

#### order\_by

```python
def order_by(properties: str) -> "DeclarativeBase"
```

Creates a ORDER BY statement Cypher partial query.

#### limit

```python
def limit(integer_expression: str) -> "DeclarativeBase"
```

Creates a LIMIT statement Cypher partial query.

#### skip

```python
def skip(integer_expression: str) -> "DeclarativeBase"
```

Creates a SKIP statement Cypher partial query.

#### get\_single

```python
def get_single(retrieve: str) -> Any
```

Returns a single result with a `retrieve` variable name.

#### execute

```python
def execute() -> Iterator[Dict[str, Any]]
```

Executes the Cypher query.

