---
sidebar_label: dgl_translator
title: gqlalchemy.transformations.translators.dgl_translator
---

## DGLTranslator Objects

```python
class DGLTranslator(Translator)
```

Performs conversion from cypher queries to the DGL graph representation. DGL assigns to each edge a unique integer, called the edge ID,
based on the order in which it was added to the graph. In DGL, all the edges are directed, and an edge (u,v) indicates that the direction goes
from node u to node v. Only features of numerical types (e.g., float, double, and int) are allowed. They can be scalars, vectors or multi-dimensional
tensors (DGL requirement). Each node feature has a unique name and each edge feature has a unique name. The features of nodes and edges can have
the same name. A feature is created via tensor assignment, which assigns a feature to each node/edge in the graph. The leading dimension of that
tensor must be equal to the number of nodes/edges in the graph. You cannot assign a feature to a subset of the nodes/edges in the graph. Features of the
same name must have the same dimensionality and data type.

#### to\_cypher\_queries

```python
def to_cypher_queries(graph: Union[dgl.DGLGraph, dgl.DGLHeteroGraph])
```

Produce cypher queries for data saved as part of the DGL graph. The method handles both homogeneous and heterogeneous graph. If the graph is homogeneous, a default DGL&#x27;s labels will be used.
_N as a node label and _E as edge label. The method converts 1D as well as multidimensional features. If there are some isolated nodes inside DGL graph, they won&#x27;t get transferred. Nodes and edges
created in Memgraph DB will, for the consistency reasons, have property `dgl_id` set to the id they have as part of the DGL graph. Note that this method doesn&#x27;t insert anything inside the database,
it just creates cypher queries. To insert queries the following code can be used:
&gt;&gt;&gt; memgraph = Memgraph()
dgl_graph = DGLGraph(...)
for query in DGLTranslator().to_cypher_queries(dgl_graph):
memgraph.execute(query)

**Arguments**:

- `graph` - A reference to the DGL graph.

**Returns**:

  cypher queries.

#### get\_instance

```python
def get_instance() -> dgl.DGLHeteroGraph
```

Create instance of DGL graph from all edges that are inside Memgraph. Currently, isolated nodes are ignored because they don&#x27;t contribute in message passing neural networks. Only numerical features
that are set on all nodes or all edges are transferred to the DGL instance since this is DGL&#x27;s requirement. That means that any string values properties won&#x27;t be transferred, as well as numerical properties
that aren&#x27;t set on all nodes. However, features of type list are transferred to the DGL and can be used as any other feature in the DGL graph. Regardless of data residing inside Memgraph database, the created
DGL graph is a heterograph instance.

**Returns**:

  DGL heterograph instance.

