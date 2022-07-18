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

Obtain data from the database by matching it to a given pattern.

**Arguments**:

- `optional` - A bool indicating if missing parts of the pattern will be
  filled with null values.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### merge

```python
def merge() -> "DeclarativeBase"
```

Ensure that a pattern you are looking for exists in the database.
This means that if the pattern is not found, it will be created. In a
way, this clause is like a combination of MATCH and CREATE.

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### create

```python
def create() -> "DeclarativeBase"
```

Create nodes and relationships in a graph.

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### call

```python
def call(procedure: str, arguments: Optional[str] = None) -> "DeclarativeBase"
```

Call a query module procedure.

**Arguments**:

- `procedure` - A string representing the name of the procedure in the
  format `query_module.procedure`.
- `arguments` - A string representing the arguments of the procedure in
  text format.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### node

```python
def node(labels: Union[str, List[str], None] = "", variable: Optional[str] = None, node: Optional["Node"] = None, **kwargs, ,) -> "DeclarativeBase"
```

Add a node pattern to the query.

**Arguments**:

- `labels` - A string or list of strings representing the labels of the
  node.
- `variable` - A string representing the name of the variable for storing
  results of the node pattern.
- `node` - A `Node` object to construct the pattern from.
- `**kwargs` - Arguments representing the properties of the node.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### to

```python
def to(edge_label: Optional[str] = "", directed: Optional[bool] = True, variable: Optional[str] = None, relationship: Optional["Relationship"] = None, **kwargs, ,) -> "DeclarativeBase"
```

Add a relationship pattern to the query.

**Arguments**:

- `edge_label` - A string representing the type of the relationship.
- `directed` - A bool indicating if the relationship is directed.
- `variable` - A string representing the name of the variable for storing
  results of the relationship pattern.
- `relationship` - A `Relationship` object to construct the pattern from.
- `**kwargs` - Arguments representing the properties of the relationship.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### from\_

```python
def from_(edge_label: Optional[str] = "", directed: Optional[bool] = True, variable: Optional[str] = None, relationship: Optional["Relationship"] = None, **kwargs, ,) -> "Match"
```

Add a relationship pattern to the query.

**Arguments**:

- `edge_label` - A string representing the type of the relationship.
- `directed` - A bool indicating if the relationship is directed.
- `variable` - A string representing the name of the variable for storing
  results of the relationship pattern.
- `relationship` - A `Relationship` object to construct the pattern from.
- `**kwargs` - Arguments representing the properties of the relationship.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### where

```python
def where(item: str, operator: str, value: Any) -> "DeclarativeBase"
```

Creates a WHERE statement Cypher partial query.

#### and\_where

```python
def and_where(item: str, operator: str, value: Any) -> "DeclarativeBase"
```

Creates a AND (expression) statement Cypher partial query.

#### or\_where

```python
def or_where(item: str, operator: str, value: Any) -> "DeclarativeBase"
```

Creates a OR (expression) statement Cypher partial query.

#### xor\_where

```python
def xor_where(item: str, operator: str, value: Any) -> "DeclarativeBase"
```

Creates a XOR (expression) statement Cypher partial query.

#### unwind

```python
def unwind(list_expression: str, variable: str) -> "DeclarativeBase"
```

Unwind a list of values as individual rows.

**Arguments**:

- `list_expression` - A list of strings representing the list of values.
- `variable` - A string representing the variable name for unwinding results.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### with\_

```python
def with_(results: Optional[Dict[str, str]] = {}) -> "DeclarativeBase"
```

Chain together parts of a query, piping the results from one to be
used as starting points or criteria in the next.

**Arguments**:

- `results` - A dictionary mapping variables in the first query with
  aliases in the second query.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### union

```python
def union(include_duplicates: Optional[bool] = True) -> "DeclarativeBase"
```

Combine the result of multiple queries.

**Arguments**:

- `include_duplicates` - A bool indicating if duplicates should be
  included.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### delete

```python
def delete(variable_expressions: List[str], detach: Optional[bool] = False) -> "DeclarativeBase"
```

Delete nodes and relationships from the database.

**Arguments**:

- `variable_expressions` - A list of strings indicating which nodes
  and/or relationships should be removed.
- `detach` - A bool indicating if relationships should be deleted along
  with a node.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### remove

```python
def remove(items: List[str]) -> "DeclarativeBase"
```

Remove labels and properties from nodes and relationships.

**Arguments**:

- `items` - A list of strings indicating which labels and/or properties
  should be removed.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### yield\_

```python
def yield_(results: Optional[Dict[str, str]] = {}) -> "DeclarativeBase"
```

Yield data from the query.

**Arguments**:

- `results` - A dictionary mapping items that are returned with alias
  names.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### return\_

```python
def return_(results: Optional[Dict[str, str]] = {}) -> "DeclarativeBase"
```

Return data from the query.

**Arguments**:

- `results` - A dictionary mapping items that are returned with alias
  names.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### order\_by

```python
def order_by(properties: str) -> "DeclarativeBase"
```

Order the results of the query.

**Arguments**:

- `properties` - A string representing how to order the results.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### limit

```python
def limit(integer_expression: str) -> "DeclarativeBase"
```

Limit the number of records when returning results.

**Arguments**:

- `integer_expression` - An integer indicating how many records to limit
  the results to.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### skip

```python
def skip(integer_expression: str) -> "DeclarativeBase"
```

Skip a number of records when returning results.

**Arguments**:

- `integer_expression` - An integer indicating how many records to skip
  in the results.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### add\_custom\_cypher

```python
def add_custom_cypher(custom_cypher: str) -> "DeclarativeBase"
```

Inject custom Cypher code into the query.

**Arguments**:

- `custom_cypher` - A string representing the Cypher code to be injected
  into the query.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### load\_csv

```python
def load_csv(path: str, header: bool, row: str) -> "DeclarativeBase"
```

Load data from a CSV file by executing a Cypher query for each row.

**Arguments**:

- `path` - A string representing the path to the CSV file.
- `header` - A bool indicating if the CSV file starts with a header row.
- `row` - A string representing the name of the variable for iterating
  over each row.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.

#### get\_single

```python
def get_single(retrieve: str) -> Any
```

Returns a single result with a `retrieve` variable name.

**Arguments**:

- `retrieve` - A string representing the results variable to be returned.
  

**Returns**:

  An iterator of dictionaries containing the results of the query.

#### execute

```python
def execute() -> Iterator[Dict[str, Any]]
```

Executes the Cypher query and returns the results.

**Returns**:

  An iterator of dictionaries containing the results of the query.

