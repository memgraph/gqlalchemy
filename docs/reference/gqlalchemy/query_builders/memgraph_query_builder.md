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

- `path` - A string representing the path to the CSV file.
- `header` - A bool indicating if the CSV file starts with a header row.
- `row` - A string representing the name of the variable for iterating
  over each row.
  

**Returns**:

  A `DeclarativeBase` instance for constructing queries.
  

**Examples**:

  Load CSV with header:
  
- `Python` - `load_csv(path=&quot;path/to/my/file.csv&quot;, header=True, row=&quot;row&quot;).return_().execute()`
- `Cypher` - `LOAD CSV FROM &#x27;path/to/my/file.csv&#x27; WITH HEADER AS row RETURN *;`
  
  Load CSV without header:
  
- `Python` - `load_csv(path=&#x27;path/to/my/file.csv&#x27;, header=False, row=&#x27;row&#x27;).return_().execute()`
- `Cypher` - `LOAD CSV FROM &#x27;path/to/my/file.csv&#x27; NO HEADER AS row RETURN *;`

