---
sidebar_label: tfgnn_translator
title: gqlalchemy.transformations.translators.tfgnn_translator
---

## TFGNNTranslator Objects

```python
class TFGNNTranslator(Translator)
```

Translator for converting between Memgraph and TensorFlow GNN (TF-GNN) graph representations.

TF-GNN represents graphs as GraphTensor objects, which are composite tensors that can be used directly in TensorFlow operations. This translator handles the conversion between Memgraph's graph model and TF-GNN's GraphTensor.

TF-GNN is particularly useful for building Graph Neural Networks (GNNs) using TensorFlow and Keras. It supports both homogeneous and heterogeneous graphs with node and edge features.

#### to\_cypher\_queries

```python
def to_cypher_queries(graph_tensor: tfgnn.GraphTensor) -> List[str]
```

Produce Cypher queries for data saved as part of the TF-GNN GraphTensor. The method handles both homogeneous and heterogeneous graphs. If the graph is homogeneous, default labels will be used (`_N` as a node label and `_E` as edge label). The method converts 1D as well as multidimensional features. If there are some isolated nodes inside the GraphTensor, they won't get transferred. Nodes and edges created in Memgraph DB will, for consistency reasons, have property `tfgnn_id` set to the id they have as part of the TF-GNN graph. Note that this method doesn't insert anything inside the database, it just creates Cypher queries. To insert queries the following code can be used:

```python
from gqlalchemy import Memgraph
from gqlalchemy.transformations.translators.tfgnn_translator import TFGNNTranslator

memgraph = Memgraph()
graph_tensor = ...  # Your TF-GNN GraphTensor
for query in TFGNNTranslator().to_cypher_queries(graph_tensor):
    memgraph.execute(query)
```

**Arguments**:

- `graph_tensor` - A reference to the TF-GNN GraphTensor.

**Returns**:

  List of Cypher queries.

#### get\_instance

```python
def get_instance() -> tfgnn.GraphTensor
```

Create an instance of TF-GNN GraphTensor from all nodes and edges that are inside Memgraph.

The translator converts Memgraph node labels to TF-GNN node sets and edge types to edge sets. Node and edge properties are converted to TF-GNN features with the following rules:

- String, Integer, Float, Boolean properties are converted to corresponding TensorFlow dtypes
- List properties are converted to tensors (dense if same length, ragged if different lengths)
- Missing properties result in ragged tensors with empty values
- Map properties are not supported and will raise an error
- Memgraph-specific types (temporal types, Enum, Point) are converted to string representation

**Returns**:

  A TF-GNN GraphTensor instance representing the graph stored in Memgraph.
