---
sidebar_label: declarative_base
title: gqlalchemy.query_builders.declarative_base
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

## RelationshipPartialQuery Objects

```python
class RelationshipPartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Constructs a relationship partial query.

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

## \_ResultPartialQuery Objects

```python
class _ResultPartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Creates a RETURN/YIELD/WITH statement Cypher partial query.

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

## ForeachPartialQuery Objects

```python
class ForeachPartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Creates a FOREACH statement Cypher partial query.

## SetPartialQuery Objects

```python
class SetPartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Constructs a set partial query.

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
  

**Examples**:

  Get all nodes with a certain label:
  
- `Python` - `match().node(labels=&#x27;Country&#x27;, variable=&#x27;c&#x27;).return_(results=&#x27;c&#x27;).execute()`
- `Cypher` - `MATCH (c:Country) RETURN c;`
  
  Get a relationship of a certain type that connects two nodes with certain label:
  
- `Python` - `match().node(labels=&#x27;Town&#x27;, variable=&#x27;t&#x27;).to(relationship_type=&#x27;BELONGS_TO&#x27;, variable=&#x27;b&#x27;).node(labels=&#x27;Country&#x27;, variable=&#x27;c&#x27;).return_(results=&#x27;b&#x27;).execute()`
- `Cypher` - `MATCH (t:Town)-[b:BELONGS_TO]-&gt;(c:Country) RETURN b;`

#### merge

```python
def merge() -> "DeclarativeBase"
```

Ensure that a pattern you are looking for exists in the database.
This means that if the pattern is not found, it will be created. In a
way, this clause is like a combination of MATCH and CREATE.

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Example**:

  Merge node with properties:
  
- `Python` - `merge().node(variable=&#x27;city&#x27;).where(item=&#x27;city.name&#x27;, operator=Operator.EQUAL, literal=&#x27;London&#x27;).return_(results=&#x27;city&#x27;).execute()`
- `Cypher` - `MERGE (city) WHERE city.name = &#x27;London&#x27; RETURN city;`

#### create

```python
def create() -> "DeclarativeBase"
```

Create nodes and relationships in a graph.

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Example**:

  Create a single node:
  
- `Python` - `create().node(labels=&#x27;Person&#x27;, variable=&#x27;p&#x27;).return_(results=&#x27;p&#x27;).execute()`
- `Cypher` - `CREATE (p:Person) RETURN p;`

#### call

```python
def call(
    procedure: str,
    arguments: Optional[Union[str, Tuple[Union[str, int, float]]]] = None
) -> "DeclarativeBase"
```

Call a query module procedure.

**Arguments**:

- `procedure` - A string representing the name of the procedure in the
  format `query_module.procedure`.
- `arguments` - A string representing the arguments of the procedure in
  text format.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Examples**:

  Call procedure with no arguments:
  
- `Python` - `call(&#x27;pagerank.get&#x27;).yield_().return_().execute()`
- `Cypher` - `CALL pagerank.get() YIELD * RETURN *;`
  
  Call procedure with arguments:
  
- `Python` - `call(&#x27;json_util.load_from_url&#x27;, &quot;&#x27;https://some-url.com&#x27;&quot;).yield_(&#x27;objects&#x27;).return_(results=&#x27;objects&#x27;).execute()
- `Cypher` - `CALL json_util.load_from_url(https://some-url.com) YIELD objects RETURN objects;`

#### node

```python
def node(labels: Union[str, List[str], None] = "",
         variable: Optional[str] = None,
         node: Optional["Node"] = None,
         **kwargs) -> "DeclarativeBase"
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
  

**Example**:

  Create a node and return it:
  
- `Python` - `create().node(labels=&#x27;Person&#x27;, variable=&#x27;n&#x27;, first_name=&#x27;Kate&#x27;).return_(results=&#x27;n&#x27;).execute()`
- `Cypher` - `CREATE (n:Person {first_name: &#x27;Kate&#x27;}) RETURN n;`

#### to

```python
def to(relationship_type: Optional[str] = "",
       directed: Optional[bool] = True,
       variable: Optional[str] = None,
       relationship: Optional["Relationship"] = None,
       algorithm: Optional[IntegratedAlgorithm] = None,
       **kwargs) -> "DeclarativeBase"
```

Add a relationship pattern to the query.

**Arguments**:

- `relationship_type` - A string representing the type of the relationship.
- `directed` - A bool indicating if the relationship is directed.
- `variable` - A string representing the name of the variable for storing
  results of the relationship pattern.
- `relationship` - A `Relationship` object to construct the pattern from.
- `algorithm` - algorithm object to use over graph data.
- `**kwargs` - Arguments representing the properties of the relationship.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Example**:

  Match and return a relationship:
  
- `Python` - `match().node(labels=&#x27;Town&#x27;, variable=&#x27;t&#x27;).to(relationship_type=&#x27;BELONGS_TO&#x27;, variable=&#x27;b&#x27;).node(labels=&#x27;Country&#x27;, variable=&#x27;c&#x27;).return_(results=&#x27;b&#x27;).execute()`
- `Cypher` - `MATCH (t:Town)-[b:BELONGS_TO]-&gt;(c:Country) RETURN b;`

#### from\_

```python
def from_(relationship_type: Optional[str] = "",
          directed: Optional[bool] = True,
          variable: Optional[str] = None,
          relationship: Optional["Relationship"] = None,
          algorithm: Optional[IntegratedAlgorithm] = None,
          **kwargs) -> "Match"
```

Add a relationship pattern to the query.

**Arguments**:

- `relationship_type` - A string representing the type of the relationship.
- `directed` - A bool indicating if the relationship is directed.
- `variable` - A string representing the name of the variable for storing
  results of the relationship pattern.
- `relationship` - A `Relationship` object to construct the pattern from.
- `**kwargs` - Arguments representing the properties of the relationship.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Example**:

  Match and return a relationship:
  
- `Python` - `match().node(labels=&#x27;Country&#x27;, variable=&#x27;c&#x27;).from_(relationship_type=&#x27;BELONGS_TO&#x27;, variable=&#x27;b&#x27;).node(labels=&#x27;Town&#x27;, variable=&#x27;t&#x27;).return_(results=&#x27;b&#x27;).execute()`
- `Cypher` - `MATCH (c:Country)&lt;-[b:BELONGS_TO]-(t:Town) RETURN b;`

#### where

```python
def where(item: str, operator: Operator, **kwargs) -> "DeclarativeBase"
```

Creates a WHERE statement Cypher partial query.

**Arguments**:

- `item` - A string representing variable or property.
- `operator` - A string representing the operator.
  
  Kwargs:
- `literal` - A value that will be converted to Cypher value, such as int, float, string, etc.
- `expression` - A node label or property that won&#x27;t be converted to Cypher value (no additional quotes will be added).
  

**Raises**:

- `GQLAlchemyLiteralAndExpressionMissingInWhere` - Raises an error when neither literal nor expression keyword arguments were provided.
- `GQLAlchemyExtraKeywordArgumentsInWhere` - Raises an error when both literal and expression keyword arguments were provided.
  

**Returns**:

- `self` - A partial Cypher query built from the given parameters.
  

**Examples**:

  Filtering query results by the equality of `name` properties of two connected nodes.
  
- `Python` - `match().node(variable=&#x27;n&#x27;).to().node(variable=&#x27;m&#x27;).where(item=&#x27;n.name&#x27;, operator=Operator.EQUAL, expression=&#x27;m.name&#x27;).return_()`
- `Cypher` - `MATCH (n)-[]-&gt;(m) WHERE n.name = m.name RETURN *;`
  
  Filtering query results by the node label.
  
- `Python` - `match().node(variable=&#x27;n&#x27;).where(item=&#x27;n&#x27;, operator=Operator.LABEL_FILTER, expression=&#x27;User&#x27;).return_()`
- `Cypher` - `MATCH (n) WHERE n:User RETURN *;`
  
  Filtering query results by the comparison of node property and literal.
  
- `Python` - `match().node(variable=&#x27;n&#x27;).where(item=&#x27;n.age&#x27;, operator=Operator.GREATER_THAN, literal=18).return_()`
- `Cypher` - `MATCH (n) WHERE n.age &gt; 18 RETURN *;`

#### where\_not

```python
def where_not(item: str, operator: Operator, **kwargs) -> "DeclarativeBase"
```

Creates a WHERE NOT statement Cypher partial query.

**Arguments**:

- `item` - A string representing variable or property.
- `operator` - A string representing the operator.
  
  Kwargs:
- `literal` - A value that will be converted to Cypher value, such as int, float, string, etc.
- `expression` - A node label or property that won&#x27;t be converted to Cypher value (no additional quotes will be added).
  

**Raises**:

- `GQLAlchemyLiteralAndExpressionMissingInWhere` - Raises an error when neither literal nor expression keyword arguments were provided.
- `GQLAlchemyExtraKeywordArgumentsInWhere` - Raises an error when both literal and expression keyword arguments were provided.
  

**Returns**:

- `self` - A partial Cypher query built from the given parameters.
  

**Examples**:

  Filtering query results by the equality of `name` properties of two connected nodes.
  
- `Python` - `match().node(variable=&#x27;n&#x27;).to().node(variable=&#x27;m&#x27;).where_not(item=&#x27;n.name&#x27;, operator=&#x27;=&#x27;, expression=&#x27;m.name&#x27;).return_()`
- `Cypher` - `MATCH (n)-[]-&gt;(m) WHERE NOT n.name = m.name RETURN *;`

#### and\_where

```python
def and_where(item: str, operator: Operator, **kwargs) -> "DeclarativeBase"
```

Creates an AND statement as a part of WHERE Cypher partial query.

**Arguments**:

- `item` - A string representing variable or property.
- `operator` - A string representing the operator.
  
  Kwargs:
- `literal` - A value that will be converted to Cypher value, such as int, float, string, etc.
- `expression` - A node label or property that won&#x27;t be converted to Cypher value (no additional quotes will be added).
  

**Returns**:

- `self` - A partial Cypher query built from the given parameters.
  

**Examples**:

  Filtering query results by node label or the comparison of node property and literal.
  
- `Python` - `match().node(variable=&#x27;n&#x27;).where(item=&#x27;n&#x27;, operator=Operator.LABEL_FILTER, expression=&#x27;User&#x27;).and_where(item=&#x27;n.age&#x27;, operator=Operator.GREATER_THAN, literal=18).return_()`
- `Cypher` - `MATCH (n) WHERE n:User AND n.age &gt; 18 RETURN *;`

#### and\_not\_where

```python
def and_not_where(item: str, operator: Operator,
                  **kwargs) -> "DeclarativeBase"
```

Creates an AND NOT statement as a part of WHERE Cypher partial query.

**Arguments**:

- `item` - A string representing variable or property.
- `operator` - A string representing the operator.
  
  Kwargs:
- `literal` - A value that will be converted to Cypher value, such as int, float, string, etc.
- `expression` - A node label or property that won&#x27;t be converted to Cypher value (no additional quotes will be added).
  

**Returns**:

- `self` - A partial Cypher query built from the given parameters.
  

**Examples**:

  Filtering query results by node label or the comparison of node property and literal.
  
- `Python` - `match().node(variable=&#x27;n&#x27;).where(item=&#x27;n&#x27;, operator=Operator.LABEL_FILTER, expression=&#x27;User&#x27;).and_not_where(item=&#x27;n.age&#x27;, operator=Operator.GREATER_THAN, literal=18).return_()`
- `Cypher` - `MATCH (n) WHERE n:User AND NOT n.age &gt; 18 RETURN *;`

#### or\_where

```python
def or_where(item: str, operator: Operator, **kwargs) -> "DeclarativeBase"
```

Creates an OR statement as a part of WHERE Cypher partial query.

**Arguments**:

- `item` - A string representing variable or property.
- `operator` - A string representing the operator.
  
  Kwargs:
- `literal` - A value that will be converted to Cypher value, such as int, float, string, etc.
- `expression` - A node label or property that won&#x27;t be converted to Cypher value (no additional quotes will be added).
  

**Returns**:

- `self` - A partial Cypher query built from the given parameters.
  

**Examples**:

  Filtering query results by node label or the comparison of node property and literal.
  
- `Python` - `match().node(variable=&#x27;n&#x27;).where(item=&#x27;n&#x27;, operator=Operator.LABEL_FILTER, expression=&#x27;User&#x27;).or_where(item=&#x27;n.age&#x27;, operator=Operator.GREATER_THAN, literal=18).return_()`
- `Cypher` - `MATCH (n) WHERE n:User OR n.age &gt; 18 RETURN *;`

#### or\_not\_where

```python
def or_not_where(item: str, operator: Operator, **kwargs) -> "DeclarativeBase"
```

Creates an OR NOT statement as a part of WHERE Cypher partial query.

**Arguments**:

- `item` - A string representing variable or property.
- `operator` - A string representing the operator.
  
  Kwargs:
- `literal` - A value that will be converted to Cypher value, such as int, float, string, etc.
- `expression` - A node label or property that won&#x27;t be converted to Cypher value (no additional quotes will be added).
  

**Returns**:

- `self` - A partial Cypher query built from the given parameters.
  

**Examples**:

  Filtering query results by node label or the comparison of node property and literal.
  
- `Python` - `match().node(variable=&#x27;n&#x27;).where(item=&#x27;n&#x27;, operator=Operator.LABEL_FILTER, expression=&#x27;User&#x27;).or_not_where(item=&#x27;n.age&#x27;, operator=Operator.GREATER_THAN, literal=18).return_()`
- `Cypher` - `MATCH (n) WHERE n:User OR NOT n.age &gt; 18 RETURN *;`

#### xor\_where

```python
def xor_where(item: str, operator: Operator, **kwargs) -> "DeclarativeBase"
```

Creates an XOR statement as a part of WHERE Cypher partial query.

**Arguments**:

- `item` - A string representing variable or property.
- `operator` - A string representing the operator.
  
  Kwargs:
- `literal` - A value that will be converted to Cypher value, such as int, float, string, etc.
- `expression` - A node label or property that won&#x27;t be converted to Cypher value (no additional quotes will be added).
  

**Returns**:

- `self` - A partial Cypher query built from the given parameters.
  

**Examples**:

  Filtering query results by node label or the comparison of node property and literal.
  
- `Python` - `match().node(variable=&#x27;n&#x27;).where(item=&#x27;n&#x27;, operator=Operator.LABEL_FILTER, expression=&#x27;User&#x27;).xor_where(item=&#x27;n.age&#x27;, operator=Operator.GREATER_THAN, literal=18).return_()`
- `Cypher` - `MATCH (n) WHERE n:User XOR n.age &gt; 18 RETURN *;`

#### xor\_not\_where

```python
def xor_not_where(item: str, operator: Operator,
                  **kwargs) -> "DeclarativeBase"
```

Creates an XOR NOT statement as a part of WHERE Cypher partial query.

**Arguments**:

- `item` - A string representing variable or property.
- `operator` - A string representing the operator.
  
  Kwargs:
- `literal` - A value that will be converted to Cypher value, such as int, float, string, etc.
- `expression` - A node label or property that won&#x27;t be converted to Cypher value (no additional quotes will be added).
  

**Returns**:

- `self` - A partial Cypher query built from the given parameters.
  

**Examples**:

  Filtering query results by node label or the comparison of node property and literal.
  
- `Python` - `match().node(variable=&#x27;n&#x27;).where(item=&#x27;n&#x27;, operator=Operator.LABEL_FILTER, expression=&#x27;User&#x27;).xor_not_where(item=&#x27;n.age&#x27;, operator=Operator.GREATER_THAN, literal=18).return_()`
- `Cypher` - `MATCH (n) WHERE n:User XOR NOT n.age &gt; 18 RETURN *;`

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
  

**Example**:

- `Python` - `unwind(list_expression=&quot;[1, 2, 3, null]&quot;, variable=&quot;x&quot;).return_(results=[&quot;x&quot;, (&quot;&#x27;val&#x27;&quot;, &quot;y&quot;)]).execute()`
- `Cypher` - `UNWIND [1, 2, 3, null] AS x RETURN x, &#x27;val&#x27; AS y;`

#### with\_

```python
def with_(
    results: Optional[Union[str, Tuple[str, str], Dict[str, str],
                            List[Union[str, Tuple[str, str]]],
                            Set[Union[str, Tuple[str, str]]], ]] = None
) -> "DeclarativeBase"
```

Chain together parts of a query, piping the results from one to be
used as starting points or criteria in the next.

**Arguments**:

- `results` - A dictionary mapping variables in the first query with
  aliases in the second query.
  

**Raises**:

- `GQLAlchemyResultQueryTypeError` - Raises an error when the provided argument is of wrong type.
- `GQLAlchemyTooLargeTupleInResultQuery` - Raises an error when the given tuple has length larger than 2.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Example**:

  Pipe the result from first part of the query for the further use:
  
- `Python` - `match().node(variable=&#x27;n&#x27;).with(&#x27;n&#x27;).execute()`
- `Cypher` - `MATCH (n) WITH n;

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
  

**Examples**:

  Combine queries and retain duplicates:
  
- `Python` - `match().node(variable=&quot;c&quot;, labels=&quot;Country&quot;).return_(results=(&quot;c.name&quot;, &quot;columnName&quot;)).union().match().node(variable=&quot;p&quot;, labels=&quot;Person&quot;).return_(results=(&quot;p.name&quot;, &quot;columnName&quot;)).execute()`
- `Cypher` - `MATCH (c:Country) RETURN c.name AS columnName UNION ALL MATCH (p:Person) RETURN p.name AS columnName;`
  
  Combine queries and remove duplicates:
  
- `Python` - `match().node(variable=&quot;c&quot;, labels=&quot;Country&quot;).return_(results=(&quot;c.name&quot;, &quot;columnName&quot;)).union(include_duplicates=False).match().node(variable=&quot;p&quot;, labels=&quot;Person&quot;).return_(results=(&quot;p.name&quot;, &quot;columnName&quot;)).execute()`
- `Cypher` - `MATCH (c:Country) RETURN c.name AS columnName UNION MATCH (p:Person) RETURN p.name AS columnName;`

#### delete

```python
def delete(variable_expressions: Union[str, List[str]],
           detach: Optional[bool] = False) -> "DeclarativeBase"
```

Delete nodes and relationships from the database.

**Arguments**:

- `variable_expressions` - A string or list of strings indicating which node(s)
  and/or relationship(s) should be removed.
- `detach` - A bool indicating if relationships should be deleted along
  with a node.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Example**:

  Delete a node:
  
- `Python` - `match().node(labels=&#x27;Node1&#x27;, variable=&#x27;n1&#x27;).delete(variable_expressions=&#x27;n1&#x27;).execute()`
- `Cypher` - `MATCH (n1:Node1) DELETE n1;`

#### remove

```python
def remove(items: Union[str, List[str]]) -> "DeclarativeBase"
```

Remove labels and properties from nodes and relationships.

**Arguments**:

- `items` - A string or list of strings indicating which label(s) and/or properties
  should be removed.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Example**:

  Remove a property from a node:
  
- `Python` - `match().node(labels=&#x27;Country&#x27;, variable=&#x27;n&#x27;, name=&#x27;United Kingdom&#x27;).remove(items=&#x27;n.name&#x27;).return_(results=&#x27;n&#x27;).execute()`
- `Cypher` - `MATCH (n:Country {name: &#x27;United Kingdom&#x27;}) REMOVE n.name RETURN n;`

#### yield\_

```python
def yield_(
    results: Optional[Union[str, Tuple[str, str], Dict[str, str],
                            List[Union[str, Tuple[str, str]]],
                            Set[Union[str, Tuple[str, str]]], ]] = None
) -> "DeclarativeBase"
```

Yield data from the query.

**Arguments**:

- `results` - A dictionary mapping items that are returned with alias names.
  

**Raises**:

- `GQLAlchemyResultQueryTypeError` - Raises an error when the provided argument is of wrong type.
- `GQLAlchemyTooLargeTupleInResultQuery` - Raises an error when the given tuple has length larger than 2.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Examples**:

  Yield all data from a query:
  
- `Python` - `call(procedure=&#x27;pagerank.get&#x27;).yield_().return_().execute()`
- `Cypher` - `CALL pagerank.get() YIELD * RETURN *;`
  
  Yield some data from a query:
  
- `Python` - `.call(procedure=&#x27;pagerank.get&#x27;).yield_(results=[&#x27;node&#x27;, &#x27;rank&#x27;]).return_(results=[&#x27;node&#x27;,&#x27;rank&#x27;]).execute()`
- `Cypher` - `CALL pagerank.get() YIELD node, rank RETURN node, rank;`

#### return\_

```python
def return_(
    results: Optional[Union[str, Tuple[str, str], Dict[str, str],
                            List[Union[str, Tuple[str, str]]],
                            Set[Union[str, Tuple[str, str]]], ]] = None
) -> "DeclarativeBase"
```

Return data from the query.

**Arguments**:

- `results` - An optional string, tuple or iterable of strings and tuples for alias names.
  

**Raises**:

- `GQLAlchemyResultQueryTypeError` - Raises an error when the provided argument is of wrong type.
- `GQLAlchemyTooLargeTupleInResultQuery` - Raises an error when the given tuple has length larger than 2.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Examples**:

  Return all variables from a query:
  
- `Python` - `match().node(labels=&#x27;Person&#x27;, variable=&#x27;p&#x27;).return_().execute()`
- `Cypher` - `MATCH (p:Person) RETURN *;`
  
  Return specific variables from a query:
  
- `Python` - `match().node(labels=&#x27;Person&#x27;, variable=&#x27;p1&#x27;).to().node(labels=&#x27;Person&#x27;, variable=&#x27;p2&#x27;).return_(results=[(&#x27;p1&#x27;,&#x27;first&#x27;), &#x27;p2&#x27;]).execute()`
- `Cypher` - `MATCH (p1:Person)-[]-&gt;(p2:Person) RETURN p1 AS first, p2;`

#### order\_by

```python
def order_by(
    properties: Union[str, Tuple[str, Order], List[Union[str, Tuple[str,
                                                                    Order]]]]
) -> "DeclarativeBase"
```

Creates an ORDER BY statement Cypher partial query.

**Arguments**:

- `properties` - Properties and order (DESC/DESCENDING/ASC/ASCENDING) by which the query results will be ordered.
  

**Raises**:

- `GQLAlchemyOrderByTypeError` - Raises an error when the given ordering is of the wrong type.
- `GQLAlchemyMissingOrder` - Raises an error when the given property is neither string nor tuple.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Examples**:

  Ordering query results by the property `n.name` in ascending order
  and by the property `n.last_name` in descending order:
  
- `Python` - `match().node(variable=&#x27;n&#x27;).return_().order_by(properties=[&#x27;n.name&#x27;, (&#x27;n.last_name&#x27;, Order.DESC)]).execute()`
- `Cypher` - `MATCH (n) RETURN * ORDER BY n.name, n.last_name DESC;`

#### limit

```python
def limit(integer_expression: Union[str, int]) -> "DeclarativeBase"
```

Limit the number of records when returning results.

**Arguments**:

- `integer_expression` - An integer indicating how many records to limit
  the results to.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Example**:

  Limit the number of returned results:
  
- `Python` - `match().node(labels=&#x27;Person&#x27;, variable=&#x27;p&#x27;).return_().limit(integer_expression=&#x27;10&#x27;).execute()`
- `Cypher` - `MATCH (p:Person) RETURN * LIMIT 10;`

#### skip

```python
def skip(integer_expression: Union[str, int]) -> "DeclarativeBase"
```

Skip a number of records when returning results.

**Arguments**:

- `integer_expression` - An integer indicating how many records to skip
  in the results.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Example**:

  Skip the first result:
  
- `Python` - `match().node(variable=&#x27;n&#x27;).return_(results=&#x27;n&#x27;).skip(integer_expression=&#x27;1&#x27;).execute()`
- `Cypher` - `MATCH (n) RETURN n SKIP 1;`

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

#### get\_single

```python
def get_single(retrieve: str) -> Any
```

Returns a single result with a `retrieve` variable name.

**Arguments**:

- `retrieve` - A string representing the results variable to be returned.
  

**Returns**:

  An iterator of dictionaries containing the results of the query.

#### foreach

```python
def foreach(
        variable: str, expression: str,
        update_clause: Union[str, List[str], Set[str]]) -> "DeclarativeBase"
```

Iterate over a list of elements and for every iteration run every update clause.

**Arguments**:

- `variable` - The variable name that stores each element.
- `expression` - Any expression that results in a list.
- `update_clauses` - One or more Cypher update clauses:
  SET, REMOVE, CREATE, MERGE, DELETE, FOREACH.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Example**:

  For each number in a list, create a node:
  
- `Python` - `update_clause = QueryBuilder().create().node(variable=&quot;n&quot;, id=PropertyVariable(&quot;i&quot;))`
  `query_builder = QueryBuilder().foreach(&quot;i&quot;, &quot;[1, 2, 3]&quot;, update_clause.construct_query())`
- `Cypher` - `FOREACH ( i IN [1, 2, 3] | CREATE (n {id: i}) )`

#### set\_

```python
def set_(item: str, operator: Operator, **kwargs)
```

Creates a SET statement Cypher partial query.

**Arguments**:

- `item` - A string representing variable or property.
- `operator` - An assignment, increment or label filter operator.
  
  Kwargs:
- `literal` - A value that will be converted to Cypher value, such as int, float, string, etc.
- `expression` - A node label or property that won&#x27;t be converted to Cypher value (no additional quotes will be added).
  

**Raises**:

- `GQLAlchemyLiteralAndExpressionMissingInWhere` - Raises an error when neither literal nor expression keyword arguments were provided.
- `GQLAlchemyExtraKeywordArgumentsInWhere` - Raises an error when both literal and expression keyword arguments were provided.
  

**Returns**:

- `self` - A partial Cypher query built from the given parameters.
  

**Examples**:

  Set or update a property.
  
- `Python` - `match().node(variable=&#x27;n&#x27;).where(item=&#x27;n.name&#x27;, operator=Operator.EQUAL, literal=&#x27;Germany&#x27;).set_(item=&#x27;n.population&#x27;, operator=Operator.ASSIGNMENT, literal=83000001).return_().execute()`
- `Cypher` - `MATCH (n) WHERE n.name = &#x27;Germany&#x27; SET n.population = 83000001 RETURN *;`
  
  Set or update multiple properties.
  
- `Python` - `match().node(variable=&#x27;n&#x27;).where(item=&#x27;n.name&#x27;, operator=Operator.EQUAL, literal=&#x27;Germany&#x27;).set_(item=&#x27;n.population&#x27;, operator=Operator.ASSIGNMENT, literal=83000001).set_(item=&#x27;n.capital&#x27;, operator=Operator.ASSIGNMENT, literal=&#x27;Berlin&#x27;).return_().execute()`
- `Cypher` - `MATCH (n) WHERE n.name = &#x27;Germany&#x27; SET n.population = 83000001 SET n.capital = &#x27;Berlin&#x27; RETURN *;`
  
  Set node label.
  
- `Python` - `match().node(variable=&#x27;n&#x27;).where(item=&#x27;n.name&#x27;, operator=Operator.EQUAL, literal=&#x27;Germany&#x27;).set_(item=&#x27;n&#x27;, operator=Operator.LABEL_FILTER, expression=&#x27;Land&#x27;).return_().execute()`
- `Cypher` - `MATCH (n) WHERE n.name = &#x27;Germany&#x27; SET n:Land RETURN *;`
  
  Replace all properties using map.
  
- `Python` - `match().node(variable=&#x27;c&#x27;, labels=&#x27;Country&#x27;).where(item=&#x27;c.name&#x27;, operator=Operator.EQUAL, literal=&#x27;Germany&#x27;).set_(item=&#x27;c&#x27;, operator=Operator.ASSIGNMENT, literal={&#x27;name&#x27;: &#x27;Germany&#x27;, &#x27;population&#x27;: &#x27;85000000&#x27;}).return_().execute()`
- `Cypher` - `MATCH (c:Country) WHERE c.name = &#x27;Germany&#x27; SET c = {name: &#x27;Germany&#x27;, population: &#x27;85000000&#x27;} RETURN *;`
  
  Update all properties using map.
  
- `Python` - `match().node(variable=&#x27;c&#x27;, labels=&#x27;Country&#x27;).where(item=&#x27;c.name&#x27;, operator=Operator.EQUAL, literal=&#x27;Germany&#x27;).set_(item=&#x27;c&#x27;, operator=Operator.INCREMENT, literal={&#x27;name&#x27;: &#x27;Germany&#x27;, &#x27;population&#x27;: &#x27;85000000&#x27;}).return_().execute()`
- `Cypher` - `MATCH (c:Country) WHERE c.name = &#x27;Germany&#x27; SET c += {name: &#x27;Germany&#x27;, population: &#x27;85000000&#x27;} RETURN *;`

#### execute

```python
def execute() -> Iterator[Dict[str, Any]]
```

Executes the Cypher query and returns the results.

**Returns**:

  An iterator of dictionaries containing the results of the query.

