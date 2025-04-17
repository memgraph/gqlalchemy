---
sidebar_label: integrated_algorithms
title: gqlalchemy.graph_algorithms.integrated_algorithms
---

## IntegratedAlgorithm Objects

```python
class IntegratedAlgorithm(ABC)
```

Abstract class modeling Memgraph&#x27;s built-in graph algorithms.

These algorithms are integrated into Memgraph&#x27;s codebase and are called
within a relationship part of a query. For instance:
MATCH p = (:City {name: &quot;Paris&quot;})
      -[:Road * bfs (r, n | r.length &lt;= 200 AND n.name != &quot;Metz&quot;)]-&gt;
      (:City {name: &quot;Berlin&quot;})

#### \_\_str\_\_

```python
@abstractmethod
def __str__() -> str
```

Instance of IntegratedAlgorithm subclass is used as a string

#### to\_cypher\_lambda

```python
@staticmethod
def to_cypher_lambda(expression: str) -> str
```

Method for creating a general lambda expression.

Variables `r` and `n` stand for relationship and node. The expression is
used e.g. for a filter lambda, to use only relationships of length less
than 200:
expression=&quot;r.length &lt; 200&quot;
with the filter lambda being:
(r, n | r.length &lt; 200)

**Arguments**:

- `expression` - Lambda conditions or statements.

## BreadthFirstSearch Objects

```python
class BreadthFirstSearch(IntegratedAlgorithm)
```

Build a BFS call for a Cypher query.

The Breadth-first search can be called in Memgraph with Cypher queries such
as: `MATCH (a {id: 723})-[*BFS ..10 (r, n | r.x &gt; 12 AND n.y &lt; 3)]-() RETURN *;`
It is called inside the relationship clause, `*BFS` naming the algorithm,
`..10` specifying depth bounds, and `(r, n | &lt;expression&gt;)` is a filter
lambda.

#### \_\_init\_\_

```python
def __init__(lower_bound: int = None,
             upper_bound: int = None,
             condition: str = None) -> None
```

**Arguments**:

- `lower_bound` - Lower bound for path depth.
- `upper_bound` - Upper bound for path depth.
- `condition` - Filter through nodes and relationships that pass this
  condition.

#### \_\_str\_\_

```python
def __str__() -> str
```

Get a Cypher query string for this algorithm.

#### to\_cypher\_bounds

```python
def to_cypher_bounds() -> str
```

If bounds are specified, returns them in grammar-defined form.

## DepthFirstSearch Objects

```python
class DepthFirstSearch(IntegratedAlgorithm)
```

Build a DFS call for a Cypher query.
The Depth-First Search can be called in Memgraph with Cypher queries
such as:
MATCH (a {id: 723})-[* ..10 (r, n | r.x &gt; 12 AND n.y &lt; 3)]-() RETURN *;
It is called inside the relationship clause, &quot;*&quot; naming the algorithm
(&quot;*&quot; without &quot;DFS&quot; because it is defined like such in openCypher),
&quot;..10&quot; specifying depth bounds, and &quot;(r, n | &lt;expression&gt;)&quot; is a filter
lambda.

#### \_\_init\_\_

```python
def __init__(lower_bound: int = None,
             upper_bound: int = None,
             condition: str = None) -> None
```

**Arguments**:

- `lower_bound` - Lower bound for path depth.
- `upper_bound` - Upper bound for path depth.
- `condition` - Filter through nodes and relationships that pass this
  condition.

#### \_\_str\_\_

```python
def __str__() -> str
```

get Cypher query string for this algorithm.

#### to\_cypher\_bounds

```python
def to_cypher_bounds() -> str
```

If bounds are specified, returns them in grammar-defined form.

## WeightedShortestPath Objects

```python
class WeightedShortestPath(IntegratedAlgorithm)
```

Build a Dijkstra shortest path call for a Cypher query.

The weighted shortest path algorithm can be called in Memgraph with Cypher
queries such as:
&quot; MATCH (a {id: 723})-[r *WSHORTEST 10 (r, n | r.weight) weight_sum
        (r, n | r.x &gt; 12 AND r.y &lt; 3)]-(b {id: 882}) RETURN * &quot;
It is called inside the relationship clause, &quot;*WSHORTEST&quot; naming the
algorithm, &quot;10&quot; specifying search depth bounds, and &quot;(r, n | &lt;expression&gt;)&quot;
is a filter lambda, used to filter which relationships and nodes to use.

#### \_\_init\_\_

```python
def __init__(upper_bound: int = None,
             condition: str = None,
             total_weight_var: str = DEFAULT_TOTAL_WEIGHT,
             weight_property: str = DEFAULT_WEIGHT_PROPERTY) -> None
```

**Arguments**:

- `upper_bound` - Upper bound for path depth.
- `condition` - Filter through nodes and relationships that pass this
  condition.
- `total_weight_var` - Variable defined as the sum of all weights on
  path being returned.
- `weight_property` - property being used as weight.

## AllShortestPath Objects

```python
class AllShortestPath(IntegratedAlgorithm)
```

Build a Dijkstra shortest path call for a Cypher query.

The weighted shortest path algorithm can be called in Memgraph with Cypher
queries such as:
&quot; MATCH (a {id: 723})-[r *ALLSHORTEST 10 (r, n | r.weight) total_weight
        (r, n | r.x &gt; 12 AND r.y &lt; 3)]-(b {id: 882}) RETURN * &quot;
It is called inside the relationship clause, &quot;*ALLSHORTEST&quot; naming the
algorithm, &quot;10&quot; specifying search depth bounds, and &quot;(r, n | &lt;expression&gt;)&quot;
is a filter lambda, used to filter which relationships and nodes to use.

#### \_\_init\_\_

```python
def __init__(upper_bound: int = None,
             condition: str = None,
             total_weight_var: str = DEFAULT_TOTAL_WEIGHT,
             weight_property: str = DEFAULT_WEIGHT_PROPERTY) -> None
```

**Arguments**:

- `upper_bound` - Upper bound for path depth.
- `condition` - Filter through nodes and relationships that pass this
  condition.
- `total_weight_var` - Variable defined as the sum of all weights on
  path being returned.
- `weight_property` - Property being used as weight.

