---
sidebar_label: graph_importer
title: gqlalchemy.transformations.importing.graph_importer
---

## GraphImporter Objects

```python
class GraphImporter(Importer)
```

Imports dgl, pyg or networkx graph representations to Memgraph.
The following code will suffice for importing queries.
&gt;&gt;&gt; importer = GraphImporter(&quot;dgl&quot;)
graph = DGLGraph(...)
importer.translate(graph)  # queries are inserted in this step

**Arguments**:

- `graph_type` - The type of the graph.

#### translate

```python
def translate(graph) -> None
```

Gets cypher queries using the underlying translator and then inserts all queries to Memgraph DB.

**Arguments**:

- `graph` - dgl, pytorch geometric or nx graph instance.

