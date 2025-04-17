---
sidebar_label: pyg_translator
title: gqlalchemy.transformations.translators.pyg_translator
---

## PyGTranslator Objects

```python
class PyGTranslator(Translator)
```

#### get\_node\_properties

```python
@classmethod
def get_node_properties(cls, graph, node_label: str, node_id: int)
```

Extracts node properties from heterogeneous graph based on the node_label.

**Arguments**:

- `graph` - A reference to the PyG graph.
- `node_label` - Node label
- `node_id` - Node_id

#### extract\_node\_edge\_properties\_from\_homogeneous\_graph

```python
@classmethod
def extract_node_edge_properties_from_homogeneous_graph(cls, graph)
```

Homogenous graph don&#x27;t have node and etype properties so it is hard to extract node and edge attributes.

**Arguments**:

- `graph` - Data = reference to the PyG graph.

**Returns**:

  node and edge attributes as dictionaries

#### to\_cypher\_queries

```python
def to_cypher_queries(graph)
```

Produce cypher queries for data saved as part of thePyG graph. The method handles both homogeneous and heterogeneous graph.
The method converts 1D as well as multidimensional features. If there are some isolated nodes inside the graph, they won&#x27;t get transferred. Nodes and edges
created in Memgraph DB will, for the consistency reasons, have property `pyg_id` set to the id they have as part of the PyG graph. Note that this method doesn&#x27;t insert anything inside
the database, it just creates cypher queries. To insert queries the following code can be used:
&gt;&gt;&gt; memgraph = Memgraph()
pyg_graph = HeteroData(...)
for query in PyGTranslator().to_cypher_queries(pyg_graph):
memgraph.execute(query)

**Arguments**:

- `graph` - A reference to the PyG graph.

**Returns**:

  cypher queries.

#### get\_instance

```python
def get_instance()
```

Create instance of PyG graph from all edges that are inside Memgraph. Currently, isolated nodes are ignored because they don&#x27;t contribute in message passing neural networks. Only numerical features
that are set on all nodes or all edges are transferred to the PyG instance since this is PyG&#x27;s requirement. That means that any string values properties won&#x27;t be transferred, as well as numerical properties
that aren&#x27;t set on all nodes. However, features that are of type list are transferred to the PyG instance and can be used as any other feature in the PyG graph. Regardless of data residing inside Memgraph database, the created
PyG graph is a heterograph instance.

**Returns**:

  PyG heterograph instance.

