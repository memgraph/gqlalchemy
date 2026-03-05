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

#### translate_dot_file

```python
def translate_dot_file(path: str) -> None
```

Parses a DOT file into a NetworkX graph and imports it to Memgraph. This method is available when `graph_type="NX"`.

**Arguments**:

- `path` - Path to a DOT file.

#### translate_dot_data

```python
def translate_dot_data(dot_data: str) -> None
```

Parses DOT content from a string into a NetworkX graph and imports it to Memgraph. This method is available when `graph_type="NX"`.

**Arguments**:

- `dot_data` - Raw DOT graph content.

