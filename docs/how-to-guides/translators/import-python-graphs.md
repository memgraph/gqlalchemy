# How to import Python graphs into Memgraph

GQLAlchemy holds translators that can import Python graphs ([NetworkX](https://networkx.org/), [PyG](https://pytorch-geometric.readthedocs.io/en/latest/) or [DGL](https://www.dgl.ai/) graphs) into Memgraph. These translators take the Python graph object and translate it to the appropriate Cypher queries. The Cypher queries are then executed to create a graph inside Memgraph. 

[![docs-source](https://img.shields.io/badge/source-examples-FB6E00?logo=github&style=for-the-badge)](https://github.com/memgraph/gqlalchemy/tree/main/tests/transformations/translators)
[![docs-source](https://img.shields.io/badge/source-translators-FB6E00?logo=github&style=for-the-badge)](https://github.com/memgraph/gqlalchemy/tree/main/gqlalchemy/transformations/translators)
[![Related - Under the
hood](https://img.shields.io/static/v1?label=Related&message=Under%20the%20hood&color=orange&style=for-the-badge)](../../under-the-hood/python-graph-translators.md)

In this guide you will learn how to:

- [**Import NetworkX graph into Memgraph**](#import-networkx-graph-into-memgraph)
- [**Import PyG graph into Memgraph**](#import-pyg-graph-into-memgraph)
- [**Import DGL graph into Memgraph**](#import-dgl-graph-into-memgraph)

## General prerequisites
You need a running **Memgraph Platform instance**, which includes both the MAGE library and Memgraph Lab, a visual interface. To run the image, open a command-line interpreter and run the following Docker command:

```
docker run -it -p 7687:7687 -p 7444:7444 -p 3000:3000 memgraph/memgraph-platform:latest
```

## Import NetworkX graph into Memgraph 

### Prerequisites

Except for the [**general prerequisites**](#general-prerequisites), you also need to install [**NetworkX Python library**](https://pypi.org/project/networkx/).

### Create and run a Python script

Create a new Python script `networkx-graph.py` in the code editor of your choice, with the following code:

```python
import networkx as nx
from gqlalchemy import Memgraph
from gqlalchemy.transformations.translators.nx_translator import NxTranslator

memgraph = Memgraph()
memgraph.drop_database()

graph = nx.Graph()
graph.add_nodes_from([(1, {"labels": "First"}), (2, {"name": "Kata"}), 3])
graph.add_edges_from([(1, 2, {"type": "EDGE_TYPE", "date": "today"}), (1, 3)])

translator = NxTranslator()

for query in list(translator.to_cypher_queries(graph)):
    memgraph.execute(query)
```

First, connect to a running Memgraph instance. Next, drop the database to be sure that it's empty. After that, create a simple NetworkX graph and add nodes and edges to it. In the end, call `to_cypher_queries` procedure on `NxTranslator` instance to transform the NetworkX graph to Cypher queries which will be executed in Memgraph.

To run it, open a command-line interpreter and run the following command:

```python
python3 networkx-graph.py
```

### Explore the graph

[Connect to Memgraph](htps://memgraph.com/docs/data-visualization/install-and-connect) via Memgraph Lab which is running at `localhost:3000`. Open the **Query Execution** section and write the following query:

```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m;
```

Click **Run Query** button to see the results.

<img src={require('../data/networkx-example-2.png').default} alt="networkx-example-1" className={"imgBorder"}/>

The NetworkX node identification number maps to the `id` node property in Memgraph. The `labels` key is reserved for the node label in Memgraph, while the edge `type` key is reserved for the relationship type in Memgraph. If no `type` is defined, then the relationship will be of type `TO` in Memgraph. You can notice that the node with the property `name` Kata and property `id` 2 doesn't have a label. This happened because the node property key `labels` was not defined. 

## Import PyG graph into Memgraph 

### Prerequisites

Except for the [**general prerequisites**](#general-prerequisites), you also need to install [**Pytorch Geometric Python library**](https://pytorch-geometric.readthedocs.io/en/latest/install/installation.html).

### Create and run a Python script

Create a new Python script `pyg-graph.py` in the code editor of your choice, with the following code:

```python
import torch
from gqlalchemy import Memgraph
from gqlalchemy.transformations.translators.pyg_translator import PyGTranslator
from torch_geometric.data import HeteroData


memgraph = Memgraph()
memgraph.drop_database()

graph = HeteroData()

graph[("user", "PLUS", "movie")].edge_index = torch.tensor(
    [[0, 0, 1], [0, 1, 0]], dtype=torch.int32
)
graph[("user", "MINUS", "movie")].edge_index = torch.tensor(
    [[2], [1]], dtype=torch.int32
)
# Set node features
graph["user"].prop1 = torch.randn(size=(3, 1))
graph["user"].prop2 = torch.randn(size=(3, 1))
graph["movie"].prop1 = torch.randn(size=(2, 1))
graph["movie"].prop2 = torch.randn(size=(2, 1))
graph["movie"].prop3 = torch.randn(size=(2, 1))
graph["movie"].x = torch.randn(size=(2, 1))
graph["movie"].y = torch.randn(size=(2, 1))
# Set edge features
graph[("user", "PLUS", "movie")].edge_prop1 = torch.randn(size=(3, 1))
graph[("user", "PLUS", "movie")].edge_prop2 = torch.randn(size=(3, 1))
graph[("user", "MINUS", "movie")].edge_prop1 = torch.randn(size=(1, 1))

translator = PyGTranslator()

for query in list(translator.to_cypher_queries(graph)):
    memgraph.execute(query)
```

First, connect to a running Memgraph instance. Next, drop the database to be sure that it's empty. After that, create a simple PyG heterogeneous graph and add nodes and edges along with their features to it. The graph consist of three `user` nodes and two `movie` nodes, as well as two types of edges - `PLUS` and `MINUS`. The `edge_index` of a graph determines which nodes are connected by which edges. Provide a tensor, that is a multi-dimensional matrix, as a value of `edge_index`, to define edges. Each tensor element maps to one graph node - first row of matrix maps to `user`, while the second one to the `movie` nodes. Hence, `user` node 0 is connected to the `movie` node 0, `user` node 0 is connected to the `movie` node 1, and `user` node 1 is connected to the `movie` node 0, with edge of type `PLUS`. These integers are mapping to the values of the `pyg_id` nodes' property in Memgraph. Similarly, the edge of type `MINUS` is created between `user` node 2 and `movie` node 1. In the end, call `to_cypher_queries` procedure on `PyGTranslator` instance to transform the PysG graph to Cypher queries which will be executed in Memgraph.

To run it, open a command-line interpreter and run the following command:

```python
python3 pyg-graph.py
```

### Explore the graph

[Connect to Memgraph](htps://memgraph.com/docs/data-visualization/install-and-connect) via Memgraph Lab which is running at `localhost:3000`. Open the **Query Execution** section and write the following query:

```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m;
```

Click **Run Query** button to see the results.

<img src={require('../data/pyg-example.png').default} alt="pyg-example" className={"imgBorder"}/>

You can notice that we have nodes labeled with `user` and `movie` and relationships of type `PLUS` and `MINUS`. Besides that, nodes and relationships have randomized array properties as well as `pyg_id` property.
 
## Import DGL graph into Memgraph 

### Prerequisites

Except for the [**general prerequisites**](#general-prerequisites), you also need to install [**Deep Graph Library**](https://www.dgl.ai/pages/start.html).

### Create and run a Python script

Create a new Python script `dgl-graph.py` in the code editor of your choice, with the following code:

```python
import numpy as np
import dgl
import torch
from gqlalchemy import Memgraph
from gqlalchemy.transformations.translators.dgl_translator import DGLTranslator

memgraph = Memgraph()
memgraph.drop_database()

graph = dgl.heterograph(
    {
        ("user", "PLUS", "movie"): (np.array([0, 0, 1]), np.array([0, 1, 0])),
        ("user", "MINUS", "movie"): (np.array([2]), np.array([1])),
    }
)
# Set node features
graph.nodes["user"].data["prop1"] = torch.randn(size=(3, 1))
graph.nodes["user"].data["prop2"] = torch.randn(size=(3, 1))
graph.nodes["movie"].data["prop1"] = torch.randn(size=(2, 1))
graph.nodes["movie"].data["prop2"] = torch.randn(size=(2, 1))
graph.nodes["movie"].data["prop3"] = torch.randn(size=(2, 1))
# Set edge features
graph.edges[("user", "PLUS", "movie")].data["edge_prop1"] = torch.randn(size=(3, 1))
graph.edges[("user", "PLUS", "movie")].data["edge_prop2"] = torch.randn(size=(3, 1))
graph.edges[("user", "MINUS", "movie")].data["edge_prop1"] = torch.randn(size=(1, 1))

translator = DGLTranslator()

for query in list(translator.to_cypher_queries(graph)):
    memgraph.execute(query)
```

First, connect to a running Memgraph instance. Next, drop the database to be sure that it's is empty. After that, create a simple DGL heterogeneous graph and add nodes and edges along with their features to it. The graph consist of three `user` nodes and two `movie` nodes, as well as two types of edges - `PLUS` and `MINUS`. To define nodes and edge between them we are providing appropriate NumPy arrays. Hence, `user` node 0 is connected to the `movie` node 0, `user` node 0 is connected to the `movie` node 1, and `user` node 1 is connected to the `movie` node 0, with edge of type `PLUS`. These integers are mapping to the values of the `dgl_id` properties in Memgraph. Similarly, the edge of type `MINUS` is created between `user` node 2 and `movie` node 1. In the end, call `to_cypher_queries` procedure on `DGLTranslator` instance to transform the DGL graph to Cypher queries which will be executed in Memgraph.

To run it, open a command-line interpreter and run the following command:

```python
python3 dgl-graph.py
```

### 3. Explore the graph

[Connect to Memgraph](htps://memgraph.com/docs/data-visualization/install-and-connect) via Memgraph Lab which is running at `localhost:3000`. Open the **Query Execution** section and write the following query:

```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m;
```

Click **Run Query** button to see the results.

<img src={require('../data/dgl-example.png').default} alt="pyg-example" className={"imgBorder"}/>

You can notice that we have nodes labeled with `user` and `movie` and relationships of type `PLUS` and `MINUS`. Besides that, nodes and relationships have randomized array properties ad well as `dgl_id` property.

## Learn more

Head over to the [**Under the hood**](../../under-the-hood/python-graph-translators.md) section to read about implementation details. If you want to learn more about using NetworkX with Memgraph with interesting resources and courses, head over to the [**Memgraph for NetworkX developers**](https://memgraph.com/memgraph-for-networkx?utm_source=docs&utm_medium=referral&utm_campaign=networkx_ppp&utm_term=docsgqla%2Bhowto&utm_content=textlink) website. If you have any questions or want to connect with the Memgraph community, [**join our Discord server**](https://www.discord.gg/memgraph).
