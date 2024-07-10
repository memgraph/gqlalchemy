---
sidebar_label: graph_transporter
title: gqlalchemy.transformations.export.graph_transporter
---

## GraphTransporter Objects

```python
class GraphTransporter(Transporter)
```

Here is a possible example for using this module:
&gt;&gt;&gt; transporter = GraphTransporter(&quot;dgl&quot;)
graph = transporter.export()

#### \_\_init\_\_

```python
def __init__(graph_type: str,
             host: str = mg_consts.MG_HOST,
             port: int = mg_consts.MG_PORT,
             username: str = mg_consts.MG_USERNAME,
             password: str = mg_consts.MG_PASSWORD,
             encrypted: bool = mg_consts.MG_ENCRYPTED,
             client_name: str = mg_consts.MG_CLIENT_NAME,
             lazy: bool = mg_consts.MG_LAZY) -> None
```

Initializes GraphTransporter. It is used for converting Memgraph graph to the specific graph type offered by some Python package (PyG, DGL, NX...)
Here is a possible example for using this module:
&gt;&gt;&gt; transporter = GraphTransporter(&quot;dgl&quot;)
graph = transporter.export()

**Arguments**:

- `graph_type` - dgl, pyg or nx

#### export

```python
def export()
```

Creates graph instance for the wanted export option.

