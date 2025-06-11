---
sidebar_label: memgraph_query_builder
title: gqlalchemy.query_builders.memgraph_query_builder
---

## QueryBuilder Objects

```python
class QueryBuilder(DeclarativeBase)
```

#### load\_csv

```python
def load_csv(path: str, header: bool, row: str) -> "DeclarativeBase"
```

Load data from a CSV file by executing a Cypher query for each row.

**Arguments**:

- `path` - A string representing the path to the CSV file. If beginning with `http://`, `https://`, or `ftp://`, the CSV file will be fetched over the network.
- `header` - A bool indicating if the CSV file starts with a header row.
- `row` - A string representing the name of the variable for iterating
  over each row.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Examples**:

  Load CSV with header:
  
- `Python` - `load_csv(path="path/to/my/file.csv", header=True, row="row").return_().execute()`
- `Cypher` - `http://`0
  
  Load CSV without header:
  
- `Python` - `http://`2
- `Cypher` - `http://`4

#### call

```python
def call(procedure: str,
         arguments: Optional[Union[str, Tuple[Union[str, int, float]]]] = None,
         node_labels: Optional[Union[str, List[List[str]]]] = None,
         relationship_types: Optional[Union[str, List[List[str]]]] = None,
         relationship_directions: Optional[
             Union[RelationshipDirection,
                   List[RelationshipDirection]]] = RelationshipDirection.RIGHT,
         subgraph_path: str = None) -> "DeclarativeBase"
```

Override of base class method to support Memgraph&#x27;s subgraph functionality.

Method can be called with node labels and relationship types, both being optional, which are used to construct
a subgraph, or if neither is provided, a subgraph query is used, which can be passed as a string representing a
Cypher query defining the MATCH clause which selects the nodes and relationships to use.

**Arguments**:

- `procedure` - A string representing the name of the procedure in the
  format `query_module.procedure`.
- `arguments` - A string representing the arguments of the procedure in
  text format.
- `node_labels` - Either a string, which is then used as the label for all nodes, or
  a list of lists defining all labels for every node
- `relationship_types` - Types of relationships to be used in the subgraph. Either a
  single type or a list of lists defining all types for every relationship
- `relationship_directions` - Directions of the relationships.
- `subgraph_path` - Optional way to define the subgraph via a Cypher MATCH clause.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Examples**:

- `Python` - `call('export_util.json', '/home/user', "LABEL", ["TYPE1", "TYPE2"]).execute()
- `Cypher`query_module.procedure`0MATCH p=(a)-[:TYPE1 | :TYPE2]-&gt;(b) WHERE (a:LABEL) AND (b:LABEL)
  WITH project(p) AS graph CALL export_util.json(graph, &#x27;/home/user&#x27;)`
  
  or
  
- `Python` - `call(&#x27;export_util.json&#x27;, &#x27;/home/user&#x27;, subgraph_path=&quot;(:LABEL)-[:TYPE]-&gt;(:LABEL)&quot;).execute()
- `Cypher`query_module.procedure`0MATCH p=(:LABEL)-[:TYPE1]-&gt;(:LABEL) WITH project(p) AS graph
  CALL export_util.json(graph, &#x27;/home/user&#x27;)`

## ProjectPartialQuery Objects

```python
class ProjectPartialQuery(PartialQuery)
```

#### construct\_query

```python
def construct_query() -> str
```

Constructs a Project partial query.

Given path part of a query (e.g. (:LABEL)-[:TYPE]-&gt;(:LABEL2)),
adds MATCH, a path identifier and appends the WITH clause.

