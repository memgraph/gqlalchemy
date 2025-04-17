# How to export data from Memgraph into Python graphs

GQLAlchemy holds translators that can export Memgraph graphs into Python graphs ([NetworkX](https://networkx.org/), [PyG](https://pytorch-geometric.readthedocs.io/en/latest/) or [DGL](https://www.dgl.ai/) graphs). These translators create a Python graph instance from the graph stored in Memgraph. 

[![docs-source](https://img.shields.io/badge/source-examples-FB6E00?logo=github&style=for-the-badge)](https://github.com/memgraph/gqlalchemy/tree/main/tests/transformations/translators)
[![docs-source](https://img.shields.io/badge/source-translators-FB6E00?logo=github&style=for-the-badge)](https://github.com/memgraph/gqlalchemy/tree/main/gqlalchemy/transformations/translators)
[![Related - Under the
hood](https://img.shields.io/static/v1?label=Related&message=Under%20the%20hood&color=orange&style=for-the-badge)](../../under-the-hood/python-graph-translators.md)

In this guide you will learn how to:

- [**Export data from Memgraph into NetworkX graph**](#export-data-from-memgraph-into-networkx-graph)
- [**Export data from Memgraph into PyG graph**](#import-pyg-graph-into-memgraph)
- [**Export data from Memgraph into DGL graph**](#import-dgl-graph-into-memgraph)

## General prerequisites
You need a running **Memgraph Platform instance**, which includes both the MAGE library and Memgraph Lab, a visual interface. To run the image, open a command-line interpreter and run the following Docker command:

```
docker run -it -p 7687:7687 -p 7444:7444 -p 3000:3000 memgraph/memgraph-platform:latest
```

<details>
<summary>To export data from Memgraph, you first have to <b>create a graph in Memgraph</b>. To do that, expand this section and run the given Python script.</summary>

```python
from gqlalchemy import Memgraph

memgraph = Memgraph()
memgraph.drop_database()

queries = []
queries.append(f"CREATE (m:Node {{id: 1, num: 80, edem: 30, lst: [2, 3, 3, 2]}})")
queries.append(f"CREATE (m:Node {{id: 2, num: 91, edem: 32, lst: [2, 2, 3, 3]}})")
queries.append(
    f"CREATE (m:Node {{id: 3, num: 100, edem: 34, lst: [3, 2, 2, 3, 4, 4]}})"
)
queries.append(f"CREATE (m:Node {{id: 4, num: 12, edem: 34, lst: [2, 2, 2, 3, 5, 5]}})")
queries.append(
    f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 1, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1, 0, 1, 0, 1]}}]->(m)"
)
queries.append(
    f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 2, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
)
queries.append(
    f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 3, edge_num: 99, edge_edem: 12, edge_lst: [1, 0, 1, 0, 1, 0, 1]}}]->(m)"
)
queries.append(
    f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 4, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
)
queries.append(
    f"MATCH (n:Node {{id: 1}}), (m:Node {{id: 3}}) CREATE (n)-[r:CONNECTION {{edge_id: 5, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
)
queries.append(
    f"MATCH (n:Node {{id: 2}}), (m:Node {{id: 4}}) CREATE (n)-[r:CONNECTION {{edge_id: 6, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1, 0, 0]}}]->(m)"
)
queries.append(
    f"MATCH (n:Node {{id: 4}}), (m:Node {{id: 2}}) CREATE (n)-[r:CONNECTION {{edge_id: 7, edge_num: 99, edge_edem: 12, edge_lst: [1, 1, 0, 0, 1, 1, 0, 1]}}]->(m)"
)
queries.append(
    f"MATCH (n:Node {{id: 3}}), (m:Node {{id: 1}}) CREATE (n)-[r:CONNECTION {{edge_id: 8, edge_num: 99, edge_edem: 12, edge_lst: [0, 1, 0, 1]}}]->(m)"
)

for query in queries:
    memgraph.execute(query)
```

</details>

## Export data from Memgraph into NetworkX graph

### Prerequisites

Except for the [**general prerequisites**](#general-prerequisites), you also need to install [**NetworkX Python library**](https://pypi.org/project/networkx/).

### Create and run a Python script

Create a new Python script `memgraph-to-nx.py`, in the code editor of your choice, with the following code:

```python
from gqlalchemy.transformations.translators.nx_translator import NxTranslator

translator = NxTranslator()
graph = translator.get_instance()

print(graph.number_of_edges())
print(graph.number_of_nodes())
```

To run it, open a command-line interpreter and run the following command:

```python
python3 memgraph-to-nx.py
```

You will get the following output:
```
8
4
```

This means that the NetworkX graph has the correct number of nodes and edges. You can explore it more to see if it has all the required features.

## Export data from Memgraph into PyG graph

### Prerequisites

Except for the [**general prerequisites**](#general-prerequisites), you also need to install [**Pytorch Geometric Python library**](https://pytorch-geometric.readthedocs.io/en/latest/install/installation.html).

### Create and run a Python script

Create a new Python script `memgraph-to-pyg.py`, in the code editor of your choice, with the following code:

```python
from gqlalchemy.transformations.translators.pyg_translator import PyGTranslator

translator = PyGTranslator()
graph = translator.get_instance()

print(len(graph.edge_types))
print(len(graph.node_types))

source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
can_etype = (source_node_label, edge_type, dest_node_label)
print(graph[source_node_label].num_nodes)
print(graph[can_etype].num_edges)
```

To run it, open a command-line interpreter and run the following command:

```python
python3 memgraph-to-pyg.py
```

You will get the following output:
```
1
1
4
8
```

This means that the PyG graph has the correct number of node and edge types, as well as correct total number of nodes and edges. You can explore it more to see if it has all the required features.


## Export data from Memgraph into DGL graph

### Prerequisites

Except for the [**general prerequisites**](#general-prerequisites), you also need to install [**Deep Graph Library**](https://www.dgl.ai/pages/start.html).

### Create and run a Python script

Create a new Python script `memgraph-to-dgl.py`, in the code editor of your choice, with the following code:

```python
from gqlalchemy.transformations.translators.dgl_translator import DGLTranslator

translator = DGLTranslator()
graph = translator.get_instance()

print(len(graph.canonical_etypes))
print(len(graph.ntypes))

source_node_label, edge_type, dest_node_label = ("Node", "CONNECTION", "Node")
can_etype = (source_node_label, edge_type, dest_node_label)
print(graph[can_etype].number_of_nodes())
print(graph[can_etype].number_of_edges())
print(len(graph.nodes[source_node_label].data.keys()))
print(len(graph.edges[(source_node_label, edge_type, dest_node_label)].data.keys()))
```

To run it, open a command-line interpreter and run the following command:

```python
python3 memgraph-to-dgl.py
```

You will get the following output:
```
1
1
4
8
3
3
```

This means that the DGL graph has the correct number of node and edge types, total number of nodes and edges, as well as node and edge features. You can explore it more to see if it has all the required features.

## Learn more

Head over to the [**Under the hood**](../../under-the-hood/python-graph-translators.md) section to read about implementation details. If you want to learn more about using NetworkX with Memgraph with interesting resources and courses, head over to the [**Memgraph for NetworkX developers**](https://memgraph.com/memgraph-for-networkx?utm_source=docs&utm_medium=referral&utm_campaign=networkx_ppp&utm_term=docsgqla%2Bhowto&utm_content=textlink) website. If you have any questions or want to connect with the Memgraph community, [**join our Discord server**](https://www.discord.gg/memgraph).
