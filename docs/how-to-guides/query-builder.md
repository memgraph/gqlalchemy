# How to use query builder

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Through this guide, you will learn how to use the GQLAlchemy query builder to:

- [**Create nodes and relationships**](#create-nodes-and-relationships)
    - [**Create a node**](#create-a-node)
    - [**Create a relationship**](#create-a-relationship)
- [**Merge nodes and relationships**](#merge-nodes-and-relationships)
    - [**Merge a node**](#merge-a-node)
    - [**Merge a relationship**](#merge-a-relationship)
- [**Set or update properties and labels**](#set-or-update-properties-and-labels)
    - [**Set a property**](#set-a-property)
    - [**Set a label**](#set-a-label)
    - [**Replace all properties**](#replace-all-properties)
    - [**Update all properties**](#update-all-properties)
- [**Filter data**](#filter-data)
    - [**Filter data by property comparison**](#filter-data-by-property-comparison)
    - [**Filter data by property value**](#filter-data-by-property-value)
    - [**Filter data by label**](#filter-data-by-label)
- [**Return results**](#return-results)
    - [**Return all variables from a query**](#return-all-variables-from-a-query)
    - [**Return specific variables from a query**](#return-specific-variables-from-a-query)
    - [**Limit the number of returned results**](#limit-the-number-of-returned-results)
    - [**Order the returned results**](#order-the-returned-results)
    - [**Order by a list of values**](#order-by-a-list-of-values)
- [**Delete and remove objects**](#delete-and-remove-objects)
    - [**Delete a node**](#delete-a-node)
    - [**Delete a relationship**](#delete-a-relationship)
    - [**Remove properties**](#remove-properties)
- [**Call procedures**](#call-procedures)
    - [**Call procedure with no arguments**](#call-procedure-with-no-arguments)
    - [**Call procedure with arguments**](#call-procedure-with-arguments)
- [**Load CSV file**](#load-csv-file)

>Hopefully, this guide will teach you how to properly use GQLAlchemy query builder. If you
>have any more questions, join our community and ping us on [Discord](https://discord.gg/memgraph).

!!! info 
    To test the above features, you must install [GQLAlchemy](../installation.md) and have a running Memgraph instance. If you're unsure how to run Memgraph, check out the Memgraph [Quick start](https://memgraph.com/docs/getting-started)).


## Create nodes and relationships

Methods [`create()`](../reference/gqlalchemy/query_builders/declarative_base.md#create), [`merge()`](../reference/gqlalchemy/query_builders/declarative_base.md#merge), [`match()`](../reference/gqlalchemy/query_builders/declarative_base.md#match), [`node()`](../reference/gqlalchemy/query_builders/declarative_base.md#node), [`to()`](../reference/gqlalchemy/query_builders/declarative_base.md#to) and [`from_()`](../reference/gqlalchemy/query_builders/declarative_base.md#from_) are most often used when building a query to create or merge nodes and relationships.

### Create a node

To **create a node** with label `Person` and a property `name` of value "Ron", run the following code:

<Tabs
  defaultValue="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'}
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import create

query = create().node(labels="Person", name="Ron").execute()
```

  </TabItem>
  <TabItem value="cypher">

```cypher
CREATE (:Person {name: 'Ron'});
```

</TabItem>
</Tabs>

### Create a relationship

To **create a relationship** of type `FRIENDS_WITH` with property `since` from one `Person` node to another, run the following code:

<Tabs
  defaultValue="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'},
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import create

query = (
    create()
    .node(labels="Person", name="Leslie")
    .to(relationship_type="FRIENDS_WITH", since="2023-02-16")
    .node(labels="Person", name="Ron")
    .execute()
)
```
  </TabItem>
  <TabItem value="cypher">

```cypher
CREATE (:Person {name: 'Leslie'})-[:FRIENDS_WITH {since: '2023-02-16'}]->(:Person {name: 'Ron'});
```
  
</TabItem>
</Tabs>

Since you are creating a relationship between two nodes, without first matching the existing nodes or merging the relationships, the nodes will be created too.

To **create a relationship** of type `FRIENDS_WITH` from one `Person` node to another **in an opposite direction**, run the following code:

<Tabs
  defaultValue="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'},
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import create

query = (
    create()
    .node(labels="Person", name="Leslie")
    .from(relationship_type="FRIENDS_WITH")
    .node(labels="Person", name="Ron")
    .execute()
)
```
  </TabItem>
  <TabItem value="cypher">

```cypher
CREATE (:Person {name: 'Leslie'})<-[:FRIENDS_WITH]-(:Person {name: 'Ron'});
```
  
</TabItem>
</Tabs>

Again, since you are creating a relationship between two nodes, without first matching the existing nodes or merging the relationships, the nodes will be created too.

To **create a relationship between existing nodes**, first match the existing nodes and then create a relationship by running the following code:

<Tabs
  defaultValue="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'},
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import create, match

query = (
    match()
    .node(labels="Person", name="Leslie", variable="leslie")
    .match()
    .node(labels="Person", name="Ron", variable="ron")
    create()
    .node(variable="leslie")
    .to(relationship_type="FRIENDS_WITH")
    .node(variable="ron")
    .execute()
)
```
  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (leslie:Person {name: 'Leslie'})
MATCH (ron:Person {name: 'Ron'})
CREATE (leslie)-[:FRIENDS_WITH]->(ron);
```
  
</TabItem>
</Tabs>

Read more about `CREATE` clause in the [Cypher manual](https://memgraph.com/docs/querying/clauses/create).

## Merge nodes and relationships

### Merge a node

To **merge a node**, run the following code:

<Tabs
  defaultValue="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'},
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import merge

query = merge().node(labels="Person", name="Leslie").execute()
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MERGE (:Person {name: 'Leslie'});
```

</TabItem>
</Tabs>

### Merge a relationship

To **merge a relationship**, first match the existing nodes and then merge the relationship by running the following code:


<Tabs
  defaultValue="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'},
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import match, merge

query = (
    match()
    .node(labels="Person", name="Leslie", variable="leslie")
    .match()
    .node(labels="Person", name="Ron", variable="ron")
    .merge()
    .node(variable="leslie")
    .to(relationship_type="FRIENDS_WITH")
    .node(variable="ron")
    .execute()
)
```
  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (leslie:Person {name: 'Leslie'})
MATCH (ron:Person {name: 'Ron'})
MERGE (leslie)-[:FRIENDS_WITH]->(ron);
```
  
</TabItem>
</Tabs>

Read more about `MERGE` clause in the [Cypher manual](https://memgraph.com/docs/querying/clauses/merge).

## Set or update properties and labels

The [`set_()`](../reference/gqlalchemy/query_builders/declarative_base.md#set_) method is used to set labels on nodes, and properties on nodes and relationships. When being set, labels and properties can be updated or created, depending on the operator used as the argument of `set_()` method.

### Set a property

To **set a property** of a graph object use the **assignment operator** from the query builder or a simple equals sign as a string - `"="`.

<Tabs
  defaultValue="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'}
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import match
from gqlalchemy.query_builders.memgraph_query_builder import Operator

query = (
    create()
    .node(labels="Country", variable="c", name="Germany")
    .set_(item="c.population", operator=Operator.ASSIGNMENT, literal=83000001)
    .execute()
)
```

  </TabItem>
  <TabItem value="cypher">

```cypher
CREATE (c:Country {name: 'Germany'}) SET c.population = 83000001;
```

</TabItem>
</Tabs>

!!! info 
    `Operator` is an enumeration class defined in the
    [`declarative_base.py`](https://github.com/memgraph/gqlalchemy/blob/main/gqlalchemy/query_builders/declarative_base.py#L84-L94). It can be imported from `gqlalchemy.query_builders.memgraph_query_builder`. 

    If you don't want to import it, you can use strings `"="`, `">="`, `">"`, `"<>"`, `":"`, `"<"`, `"<="`, `"!="` or `"+="` instead.


To **set a property of already existing node**, first match the node and then set its property. 

<Tabs
  defaultValue="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'}
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import match
from gqlalchemy.query_builders.memgraph_query_builder import Operator

query = (
    match()
    .node(labels="Country", variable="c", name="Germany")
    .set_(item="c.population", operator=Operator.ASSIGNMENT, literal=10000)
    .execute()
)
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (c:Country {name: 'Germany'}) SET c.population = 10000;
```

</TabItem>
</Tabs>

To **set multiple properties of a node**, run the following code:

<Tabs
  defaultValue="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'}
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import match
from gqlalchemy.query_builders.memgraph_query_builder import Operator

query = (
    match()
    .node(variable="n")
    .where(item="n.name", operator="=", literal="Germany")
    .set_(item="n.population", operator=Operator.ASSIGNMENT, literal=83000001)
    .set_(item="n.capital", operator=Operator.ASSIGNMENT, literal="Berlin")
    .execute()
)
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (n) WHERE n.name = 'Germany' SET n.population = 83000001 SET n.capital = 'Berlin';
```

</TabItem>
</Tabs>

If a node already has the properties we are setting, they will be updated to a new value. Otherwise, the properties will be created and their value will be set.

### Set a label

To **set a label of a node**, run the following code:


<Tabs
  defaultValuße="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'}
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import Match
from gqlalchemy.query_builders.memgraph_query_builder import Operator

query = Match()
        .node(variable="c", name="Germany")
        .set_(item="c", operator=Operator.LABEL_FILTER, expression="Land")
        .return_()
        .execute()
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (c {name: 'Germany'}) SET c:Land RETURN *;
```

</TabItem>
</Tabs>

If a node already has a label, then it will have both old and new label. 

### Replace all properties 

With Cypher, it is possible to **replace all properties using a map** within a `SET` clause. Here is how to do it with query builder:

<Tabs
  defaultValue="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'}
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import match
from gqlalchemy.query_builders.memgraph_query_builder import Operator

query = (
    match()
    .node(variable="c", labels="Country")
    .where(item="c.name", operator="=", literal="Germany")
    .set_(
        item="c",
        operator=Operator.ASSIGNMENT,
        literal={"country_name": "Germany", "population": 85000000},
    )
    .execute()
)
```
  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (c:Country) WHERE c.name = 'Germany' SET c = {country_name: 'Germany', population: 85000000};
```

</TabItem>
</Tabs>

The properties that are not a part of the graph objects, but are in the map, will be set. The properties that are not in the map, but are a part of the graph objects, will be removed. If a property is both in map and a graph object property, it will be updated to a new value set in map.

### Update all properties

With Cypher, it is also possible to **update all properties using a map** within a `SET` clause by  using the **increment operator** (`+=`). Here is how to do it with query builder:

<Tabs
  defaultValue="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'}
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import match
from gqlalchemy.query_builders.memgraph_query_builder import Operator

query = (
    match()
    .node(variable="c", labels="Country")
    .where(item="c.country_name", operator="=", literal="Germany")
    .set_(
        item="c",
        operator=Operator.INCREMENT,
        literal={"population": "85000000"},
    )
    .execute()
)
```
  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (c:Country) WHERE c.country_name = 'Germany' SET c += {population: '85000000'};
```

</TabItem>
</Tabs>

All the properties in the map (value of the `literal` argument) that are on a graph object will be updated. The properties that are not on a graph object but are in the map will be added. Properties that are not present in the map will be left as is.

## Filter data

You can use the methods [`where()`](../reference/gqlalchemy/query_builders/declarative_base.md#where), [`where_not()`](../reference/gqlalchemy/query_builders/declarative_base.md#where_not), [`or_where()`](../reference/gqlalchemy/query_builders/declarative_base.md#or_where),
[`or_where_not()`](../reference/gqlalchemy/query_builders/declarative_base.md#or_where_node), [`and_where()`](../reference/gqlalchemy/query_builders/declarative_base.md#and_where), [`and_where_not()`](../reference/gqlalchemy/query_builders/declarative_base.md#and_where_not), [`xor_where()`](../reference/gqlalchemy/query_builders/declarative_base.md#xor_where) and
[`xor_where_not()`](../reference/gqlalchemy/query_builders/declarative_base.md#xor_where_not) to construct queries that will filter data.



### Filter data by property comparison

To **filter data by comparing properties** of two nodes, run the following code:

<Tabs
defaultValue="gqlalchemy"
values={[
{label: 'GQLAlchemy', value: 'gqlalchemy'},
{label: 'Cypher', value: 'cypher'}
]}>
<TabItem value="gqlalchemy">

```python
from gqlalchemy import match
from gqlalchemy.query_builders.memgraph_query_builder import Operator

results = list(
    match()
    .node(labels="Person", variable="p1")
    .to(relationship_type="FRIENDS_WITH")
    .node(labels="Person", variable="p2")
    .where(item="p1.name", operator=Operator.LESS_THAN, expression="p2.name")
    .return_()
    .execute()
)

print(results)
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (p1:Person)-[:FRIENDS_WITH]->(p2:Person) WHERE p1.name < p2.name RETURN *;
```

  </TabItem>
</Tabs>

Keyword arguments that can be used in filtering methods are `literal` and `expression`. Usually we use `literal` for property values and `expression` for property names and labels. That is because property names and labels shouldn't be quoted in Cypher statements. 

!!! info 
    You will probably see the `GQLAlchemySubclassNotFoundWarning` warning. This happens if you did not define a Python class which maps to a graph object in the database. To do that, check the [object graph mapper how-to guide](ogm.md). To ignore such warnings, you can do the following before query execution:

    ```python
    from gqlalchemy import models

    models.IGNORE_SUBCLASSNOTFOUNDWARNING = True
    ```

Standard boolean operators like `NOT`, `AND`, `OR` and `XOR` are used in the
Cypher query language. To have `NOT` within `WHERE` clause, you need to use
`where_not()` method.

<Tabs
defaultValue="gqlalchemy"
values={[
{label: 'GQLAlchemy', value: 'gqlalchemy'},
{label: 'Cypher', value: 'cypher'}
]}>
<TabItem value="gqlalchemy">

```python
from gqlalchemy import match
from gqlalchemy.query_builders.memgraph_query_builder import Operator

results = list(
    match()
    .node(labels="Person", variable="p1")
    .to(relationship_type="FRIENDS_WITH")
    .node(labels="Person", variable="p2")
    .where_not(item="p1.name", operator=Operator.LESS_THAN, expression="p2.name")
    .return_()
    .execute()
)

print(results)
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (p1:Person)-[:FRIENDS_WITH]->(p2:Person) WHERE NOT p1.name < p2.name RETURN *;
```

  </TabItem>
</Tabs>

In a similar way, you can use `AND` and `AND NOT` clauses which correspond to
the methods `and_where()` and `and_not_where()`. Using the query below you can
find all persons with the same `address` and `last_name`, but different
`name`.

<Tabs
defaultValue="gqlalchemy"
values={[
{label: 'GQLAlchemy', value: 'gqlalchemy'},
{label: 'Cypher', value: 'cypher'}
]}>
<TabItem value="gqlalchemy">

```python
from gqlalchemy import match
from gqlalchemy.query_builders.memgraph_query_builder import Operator

results = list(
    match()
    .node(labels="Person", variable="p1")
    .to(relationship_type="FRIENDS_WITH")
    .node(labels="Person", variable="p2")
    .where(item="p1.address", operator=Operator.EQUAL, expression="p2.address")
    .and_where(item="p1.last_name", operator=Operator.EQUAL, expression="p2.last_name")
    .and_not_where(item="p1.name", operator=Operator.EQUAL, expression="p2.name")
    .return_()
    .execute()
)

print(results)
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (p1:Person)-[:FRIENDS_WITH]->(p2:Person)
WHERE p1.address = p2.address
AND p1.last_name = p2.last_name
AND NOT p1.name = p2.name
RETURN *;
```

  </TabItem>
</Tabs>

The same goes for the `OR`, `OR NOT`, `XOR` and `XOR NOT` clauses, which
correspond to the methods `or_where()`, `or_not_where()`, `xor_where()` and
`xor_not_where()`.

### Filter data by property value

You can **filter data by comparing the property of a graph object to some value** (a
literal). Below you can see how to compare `age` property of a node to the
integer.

<Tabs
defaultValue="gqlalchemy"
values={[
{label: 'GQLAlchemy', value: 'gqlalchemy'},
{label: 'Cypher', value: 'cypher'}
]}>
<TabItem value="gqlalchemy">

```python
from gqlalchemy import match
from gqlalchemy.query_builders.memgraph_query_builder import Operator

results = list(
    match()
    .node(labels="Person", variable="p")
    .where(item="p.age", operator=Operator.GREATER_THAN, literal=18)
    .return_()
    .execute()
)
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (p:Person) WHERE p.age > 18 RETURN *;
```

  </TabItem>
</Tabs>

The third keyword argument is `literal` since we wanted the property `age` to be saved as an integer. If we used `expression` keyword argument instead of `literal`, then the `age` property would be a string (it would be quoted in Cypher query). Instead of `Operator.GREATER_THAN`, a simple string of value `">"` can be used.

Just like in [property comparison](#filter-data-by-property-comparison), it is possible to use different boolean operators to further filter the data.

<Tabs
defaultValue="gqlalchemy"
values={[
{label: 'GQLAlchemy', value: 'gqlalchemy'},
{label: 'Cypher', value: 'cypher'}
]}>
<TabItem value="gqlalchemy">

```python
from gqlalchemy import match
from gqlalchemy.query_builders.memgraph_query_builder import Operator

results = list(
    match()
    .node(labels="Person", variable="p")
    .where(item="p.age", operator=Operator.GREATER_THAN, literal=18)
    .or_where(item="p.name", operator=Operator.EQUAL, literal="John")
    .return_()
    .execute()
)
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (p:Person) WHERE p.age > 18 OR p.name = "John" RETURN *;
```

  </TabItem>
</Tabs>

The `literal` keyword is used again since you want `John` to be quoted in the
Cypher query (to be saved as a string in the database).

### Filter data by label

Nodes can be filtered by their label using the `WHERE` clause instead of
specifying it directly in the `MATCH` clause. You have to use `expression` as
the third keyword argument again since you don't want the quotes surrounding the
label in the Cypher clause.

To **filter data by label** use the following code:

<Tabs
defaultValue="gqlalchemy"
values={[
{label: 'GQLAlchemy', value: 'gqlalchemy'},
{label: 'Cypher', value: 'cypher'}
]}>
<TabItem value="gqlalchemy">

```python
from gqlalchemy import match
from gqlalchemy.query_builders.memgraph_query_builder import Operator

results = list(
    match()
    .node(variable="p")
    .where(item="p", operator=Operator.LABEL_FILTER, expression="Person")
    .return_()
    .execute()
)

print(results)
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (p) WHERE p:Person RETURN *;
```

  </TabItem>
</Tabs>

Just like in [property comparison](#filter-data-by-property-comparison), it is possible to use different boolean operators to further filter the data.

## Return results

You can use the methods [`return_()`](../reference/gqlalchemy/query_builders/declarative_base.md#return_), [`limit()`](../reference/gqlalchemy/query_builders/declarative_base.md#limit), [`skip()`](../reference/gqlalchemy/query_builders/declarative_base.md#skip) and [`order_by()`](../reference/gqlalchemy/query_builders/declarative_base.md#order_by) to
construct queries that will return data from the database.

### Return all variables from a query

To **return all the variables from a query**, use the `return_()` method at the
end of the query:

<Tabs
defaultValue="gqlalchemy"
values={[
{label: 'GQLAlchemy', value: 'gqlalchemy'},
{label: 'Cypher', value: 'cypher'}
]}>
<TabItem value="gqlalchemy">

```python
from gqlalchemy import match

results = list(match().node(labels="Person", variable="p").return_().execute())
print(results)
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (p:Person) RETURN *;
```

  </TabItem>
</Tabs>

### Return specific variables from a query

To **return only a subset of variables** from a query, specify them in the
`return_()` method:

<Tabs
defaultValue="gqlalchemy"
values={[
{label: 'GQLAlchemy', value: 'gqlalchemy'},
{label: 'Cypher', value: 'cypher'}
]}>
<TabItem value="gqlalchemy">

```python
from gqlalchemy import match

results = list(
    match()
    .node(labels="Person", variable="p1")
    .to()
    .node(labels="Person", variable="p2")
    .return_(results=[("p1", "first"), "p2"])
    .execute()
)

for result in results:
    print("Here is one pair:")
    print(result["first"])
    print(result["p2"])
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (p1:Person)-[]->(p2:Person) RETURN p1 AS first, p2;
```

</TabItem>
</Tabs>

### Limit the number of returned results

To **limit the number of returned results**, use the `limit()` method after the
`return_()` method:

<Tabs
defaultValue="gqlalchemy"
values={[
{label: 'GQLAlchemy', value: 'gqlalchemy'},
{label: 'Cypher', value: 'cypher'}
]}>
<TabItem value="gqlalchemy">

```python
from gqlalchemy import match

results = list(match().node(labels="Person", variable="p").return_().limit(3).execute())
print(results)
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (p:Person) RETURN * LIMIT 3;
```

  </TabItem>
</Tabs>

### Order the returned results

The default ordering in the Cypher query language is ascending (`ASC` or
`ASCENDING`), and if you want the descending order, you need to add the `DESC`
or `DESCENDING` keyword to the `ORDER BY` clause.

To **order the return results by one value**, use the `order_by(properties)` method,
where `properties` can be a string (a property) or a tuple of two strings (a
property and an order).

The following query will order the results in an ascending (default) order by
the property `name` of a node.

<Tabs
defaultValue="gqlalchemy"
values={[
{label: 'GQLAlchemy', value: 'gqlalchemy'},
{label: 'Cypher', value: 'cypher'}
]}>
<TabItem value="gqlalchemy">

```python
from gqlalchemy import match

results = list(
    match().node(variable="n").return_().order_by(properties="n.name").execute()
)
print(results)

```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (n) RETURN * ORDER BY n.name;
```

</TabItem>
</Tabs>

You can also emphasize that you want an ascending order:

<Tabs
defaultValue="gqlalchemy"
values={[
{label: 'GQLAlchemy', value: 'gqlalchemy'},
{label: 'Cypher', value: 'cypher'}
]}>
<TabItem value="gqlalchemy">

```python
from gqlalchemy import match
from gqlalchemy.query_builders.memgraph_query_builder import Order

results = list(
    match()
    .node(variable="n")
    .return_()
    .order_by(properties=("n.name", Order.ASC))
    .execute()
)
print(results)
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (n) RETURN * ORDER BY n.name ASC;
```

  </TabItem>
</Tabs>

The same can be done with the keyword `ASCENDING`:

<Tabs
defaultValue="gqlalchemy"
values={[
{label: 'GQLAlchemy', value: 'gqlalchemy'},
{label: 'Cypher', value: 'cypher'}
]}>
<TabItem value="gqlalchemy">

```python
from gqlalchemy import match
from gqlalchemy.query_builders.memgraph_query_builder import Order

results = list(
    match()
    .node(variable="n")
    .return_()
    .order_by(properties=("n.name", Order.ASCENDING))
    .execute()
)
print(results)
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (n) RETURN * ORDER BY n.name ASCENDING;
```

</TabItem>
</Tabs>

!!! info 
    `Order` is an enumeration class defined in the
    [`declarative_base.py`](https://github.com/memgraph/gqlalchemy/blob/main/gqlalchemy/query_builders/declarative_base.py#L97-L101). It can be imported from `gqlalchemy.query_builders.memgraph_query_builder`. 

    If you don't want to import it, you can use strings `"ASC"`, `"ASCENDING"`, `"DESC"` or `"DESCENDING"` instead.

To order the query results in descending order, you need to specify the `DESC`
or `DESCENDING` keyword. Hence, the argument of the `order_by()` method must be
a tuple.

<Tabs
defaultValue="gqlalchemy"
values={[
{label: 'GQLAlchemy', value: 'gqlalchemy'},
{label: 'Cypher', value: 'cypher'}
]}>
<TabItem value="gqlalchemy">

```python
from gqlalchemy import match
from gqlalchemy.query_builders.memgraph_query_builder import Order

results = list(
    match()
    .node(variable="n")
    .return_()
    .order_by(properties=("n.name", Order.DESC))
    .execute()
)

print(results)
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (n) RETURN * ORDER BY n.name DESC;
```

  </TabItem>
</Tabs>

Similarly, you can use `Order.DESCENDING` to get `DESCENDING` keyword in `ORDER BY` clause.

### Order by a list of values

To **order the returned results by more than one value**, use the
`order_by(properties)` method, where `properties` can be a list of strings or
tuples of strings (list of properties with or without order).

The following query will order the results in ascending order by the property
`id`, then again in ascending (default) order by the property `name` of a node.
After that, it will order the results in descending order by the property
`last_name`, then in ascending order by the property `age` of a node. Lastly,
the query will order the results in descending order by the node property
`middle_name`.

<Tabs
defaultValue="gqlalchemy"
values={[
{label: 'GQLAlchemy', value: 'gqlalchemy'},
{label: 'Cypher', value: 'cypher'}
]}>
<TabItem value="gqlalchemy">

```python
from gqlalchemy import match
from gqlalchemy.query_builders.memgraph_query_builder import Order

results = list(
    match()
    .node(variable="n")
    .return_()
    .order_by(
        properties=[
            ("n.id", Order.ASC),
            "n.name",
            ("n.last_name", Order.DESC),
            ("n.age", Order.ASCENDING),
            ("n.middle_name", Order.DESCENDING),
        ]
    )
    .execute()
)

print(results)
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (n) 
RETURN * 
ORDER BY n.id ASC, n.name, n.last_name DESC, n.age ASCENDING, n.middle_name DESCENDING;
```

  </TabItem>
</Tabs>

## Delete and remove objects

You can use the methods [`delete()`](../reference/gqlalchemy/query_builders/declarative_base.md#delete) and [`remove()`](../reference/gqlalchemy/query_builders/declarative_base.md#remove) to construct queries that will
remove nodes and relationships or properties and labels.

### Delete a node

To **delete a node** from the database, use the `delete()` method:

<Tabs
  defaultValue="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'}
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import match

match().node(labels="Person", name="Harry", variable="p").delete(
    variable_expressions="p"
).execute()
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (p:Person {name: 'Harry'}) DELETE p;
```

</TabItem>
</Tabs>

### Delete a relationship

To **delete a relationship** from the database, use the `delete()` method:

<Tabs
  defaultValue="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'}
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import match

match().node(labels="Person", name="Leslie").to(
    relationship_type="FRIENDS_WITH", variable="f"
).node(labels="Person").delete(variable_expressions="f").execute()
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (:Person {name: 'Leslie'})-[f:FRIENDS_WITH]->(:Person) DELETE f;
```

</TabItem>
</Tabs>

### Remove properties

To remove a property (or properties) from the database, use the `remove()` method:

<Tabs
  defaultValue="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'}
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import match

match().node(labels="Person", name="Jane", variable="p").remove(
    items=["p.name", "p.last_name"]
).execute()
```

  </TabItem>
  <TabItem value="cypher">

```cypher
MATCH (p:Person {name: 'Jane'}) REMOVE p.name, p.last_name;
```

</TabItem>
</Tabs>


## Call procedures

You can use the methods [`call()`](../reference/gqlalchemy/query_builders/declarative_base.md#call) and [`yield_()`](../reference/gqlalchemy/query_builders/declarative_base.md#yield_) to construct queries that will
call procedure and return results from them.

### Call procedure with no arguments

To call a procedure with no arguments, don't specify the arguments in the
`call()` method:

<Tabs
  defaultValue="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'}
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import call

results = list(call("pagerank.get").yield_().return_().execute())
print(results)
```

  </TabItem>
  <TabItem value="cypher">

```cypher
CALL pagerank.get() YIELD * RETURN *;
```

</TabItem>
</Tabs>

### Call procedure with arguments

To call a procedure with arguments, specify the arguments as a string in the
`call()` method:

<Tabs
  defaultValue="gqlalchemy"
  values={[
    {label: 'GQLAlchemy', value: 'gqlalchemy'},
    {label: 'Cypher', value: 'cypher'}
  ]}>
  <TabItem value="gqlalchemy">

```python
from gqlalchemy import call

results = list(
    call(
        "json_util.load_from_url",
        "'https://download.memgraph.com/asset/mage/data.json'",
    )
    .yield_("objects")
    .return_(results="objects")
    .execute()
)

print("Load from URL with argument:", results, "\n")
```

  </TabItem>
  <TabItem value="cypher">

```cypher
CALL json_util.load_from_url('https://download.memgraph.com/asset/mage/data.json') 
YIELD objects 
RETURN objects;
```

</TabItem>
</Tabs>

<details>
<summary> <b>Code example using all of the above mentioned queries</b> </summary>

```python
from gqlalchemy import create, merge, Memgraph, match, models, call
from gqlalchemy.query_builders.memgraph_query_builder import Operator, Order


db = Memgraph()
# clean database
db.drop_database()

# create nodes and a relationship between them

create().node(labels="Person", name="Leslie").to(relationship_type="FRIENDS_WITH").node(
    labels="Person", name="Ron"
).execute()


# merge a node
merge().node(labels="Person", name="Leslie").execute()

# create nodes and a relationship between them
create().node(
    labels="Person", name="Jane", last_name="James", address="street", age=19
).from_(relationship_type="FRIENDS_WITH", since="2023-02-16").node(
    labels="Person", name="John", last_name="James", address="street", age=8
).execute()


# merge a relationship between existing nodes

match().node(labels="Person", name="Leslie", variable="leslie").match().node(
    labels="Person", name="Ron", variable="ron"
).merge().node(variable="leslie").to(relationship_type="FRIENDS_WITH").node(
    variable="ron"
).execute()


# set a property
create().node(labels="Country", variable="c", name="Germany").set_(
    item="c.population", operator=Operator.ASSIGNMENT, literal=83000001
).execute()

# update a property
match().node(labels="Country", variable="c", name="Germany").set_(
    item="c.population", operator=Operator.ASSIGNMENT, literal=10000
).execute()


# update multiple properties
match().node(variable="n").where(item="n.name", operator="=", literal="Germany").set_(
    item="n.population", operator=Operator.ASSIGNMENT, literal=83000001
).set_(item="n.capital", operator=Operator.ASSIGNMENT, literal="Berlin").execute()


# replace all properties
match().node(variable="c", labels="Country").where(
    item="c.name", operator="=", literal="Germany"
).set_(
    item="c",
    operator=Operator.ASSIGNMENT,
    literal={"country_name": "Germany", "population": 85000000},
).execute()


# update multiple properties

match().node(variable="c", labels="Country").where(
    item="c.country_name", operator="=", literal="Germany"
).set_(
    item="c",
    operator=Operator.INCREMENT,
    literal={"population": "85000000"},
).execute()


models.IGNORE_SUBCLASSNOTFOUNDWARNING = True

results = list(
    match()
    .node(labels="Person", variable="p1")
    .to(relationship_type="FRIENDS_WITH")
    .node(labels="Person", variable="p2")
    .where(item="p1.name", operator=Operator.LESS_THAN, expression="p2.name")
    .return_()
    .execute()
)

print("Filter by property comparison:", results, "\n")

results = list(
    match()
    .node(labels="Person", variable="p1")
    .to(relationship_type="FRIENDS_WITH")
    .node(labels="Person", variable="p2")
    .where_not(item="p1.name", operator=Operator.LESS_THAN, expression="p2.name")
    .return_()
    .execute()
)

print("Filter by property comparison (negation):", results, "\n")

results = list(
    match()
    .node(labels="Person", variable="p1")
    .to(relationship_type="FRIENDS_WITH")
    .node(labels="Person", variable="p2")
    .where(item="p1.address", operator=Operator.EQUAL, expression="p2.address")
    .and_where(item="p1.last_name", operator=Operator.EQUAL, expression="p2.last_name")
    .and_not_where(item="p1.name", operator=Operator.EQUAL, expression="p2.name")
    .return_()
    .execute()
)

print("Filter by property comparison + logical operators:", results, "\n")

results = list(
    match()
    .node(labels="Person", variable="p")
    .where(item="p.age", operator=Operator.GREATER_THAN, literal=18)
    .return_()
    .execute()
)

print("Filter by property value:", results, "\n")

results = list(
    match()
    .node(labels="Person", variable="p")
    .where(item="p.age", operator=Operator.GREATER_THAN, literal=18)
    .or_where(item="p.name", operator=Operator.EQUAL, literal="John")
    .return_()
    .execute()
)

print("Filter by property value + logical operators:", results, "\n")

results = list(
    match()
    .node(variable="p")
    .where(item="p", operator=Operator.LABEL_FILTER, expression="Person")
    .return_()
    .execute()
)

print("Filter by label:", results, "\n")


results = list(match().node(labels="Person", variable="p").return_().execute())
print("Return all:", results, "\n")

results = list(
    match()
    .node(labels="Person", variable="p1")
    .to()
    .node(labels="Person", variable="p2")
    .return_(results=[("p1", "first"), "p2"])
    .execute()
)

for result in results:
    print("Here is one pair:")
    print(result["first"])
    print(result["p2"])

print()

results = list(match().node(labels="Person", variable="p").return_().limit(3).execute())
print("Limit results:", results, "\n")


results = list(
    match().node(variable="n").return_().order_by(properties="n.name").execute()
)
print("Order descending:", results, "\n")

results = list(
    match()
    .node(variable="n")
    .return_()
    .order_by(properties=("n.name", Order.ASCENDING))
    .execute()
)
print("Order ascending:", results, "\n")

results = list(
    match()
    .node(variable="n")
    .return_()
    .order_by(properties=("n.name", Order.DESC))
    .execute()
)

print("Order descending with ordering:", results, "\n")

results = list(
    match()
    .node(variable="n")
    .return_()
    .order_by(
        properties=[
            ("n.id", Order.ASC),
            "n.name",
            ("n.last_name", Order.DESC),
            ("n.age", Order.ASCENDING),
            ("n.middle_name", Order.DESCENDING),
        ]
    )
    .execute()
)

print("Mix of ordering:", results, "\n")


# create a node to delete
create().node(labels="Person", name="Harry").execute()

# delete a node
match().node(labels="Person", name="Harry", variable="p").delete(
    variable_expressions="p"
).execute()

# delete a relationship between Leslie and her friends
match().node(labels="Person", name="Leslie").to(
    relationship_type="FRIENDS_WITH", variable="f"
).node(labels="Person").delete(variable_expressions="f").execute()

# remove name and last_name properties from Jane
match().node(labels="Person", name="Jane", variable="p").remove(
    items=["p.name", "p.last_name"]
).execute()

# calculate PageRank
results = list(call("pagerank.get").yield_().return_().execute())
print("PageRank:", results, "\n")

# Load JSON from URL with arguments
results = list(
    call(
        "json_util.load_from_url",
        "'https://download.memgraph.com/asset/mage/data.json'",
    )
    .yield_("objects")
    .return_(results="objects")
    .execute()
)

print("Load from URL with argument:", results, "\n")
```
</details>

## Load CSV file

To load a CSV file using query builder, use the `load_csv()` procedure. Here is an example CSV file:
```
id,name,age,city
100,Daniel,30,London
101,Alex,15,Paris
102,Sarah,17,London
103,Mia,25,Zagreb
104,Lucy,21,Paris
```

To load it, run the following code:

```python
from gqlalchemy import load_csv, Memgraph
from gqlalchemy.utilities import CypherVariable

db = Memgraph()

load_csv(
      path="/path-to/people_nodes.csv", header=True, row="row"
  )
  .create()
  .node(
      variable="n",
      labels="Person",
      id=CypherVariable(name="row.id"),
      name=CypherVariable(name="row.name"),
      age=CypherVariable(name="ToInteger(row.age)"),
      city=CypherVariable(name="row.city"),
  )
  .execute()
```   

>Hopefully, this guide has taught you how to properly use GQLAlchemy query builder. If you
>have any more questions, join our community and ping us on [Discord](https://discord.gg/memgraph).

