In this under the hood content you can learn more about GQLAlchemy **Python graph translators**. 

[![Related -
How-to](https://img.shields.io/static/v1?label=Related&message=How%20to%20import&color=blue&style=for-the-badge)](../how-to-guides/translators/import-python-graphs.md)
[![Related -
How-to](https://img.shields.io/static/v1?label=Related&message=How%20to%20export&color=blue&style=for-the-badge)](../how-to-guides/translators/export-python-graphs.md)
[![docs-source](https://img.shields.io/badge/source-examples-FB6E00?logo=github&style=for-the-badge)](https://github.com/memgraph/gqlalchemy/tree/main/tests/transformations/translators)
[![docs-source](https://img.shields.io/badge/source-translators-FB6E00?logo=github&style=for-the-badge)](https://github.com/memgraph/gqlalchemy/tree/main/gqlalchemy/transformations/translators)


Within the code, translators are divided into the following parts, depending on the Python graph type you want to translate:

- [**NetworkX graph translator**](#networkx-graph-translator)
- [**PyG graph translator**](#pyg-graph-translator)
- [**DGL graph translator**](#dgl-graph-translator)


## NetworkX graph translator

The `NxTranslator` class implements the NetworkX graph translator and inherits from the `Translator` class. The `NxTranslator` class can be imported from the `gqlalchemy.transformations.translators.nx_translator` module. 

[![docs-source](https://img.shields.io/badge/source-NetworkX%20Translator-FB6E00?logo=github&style=for-the-badge)](https://github.com/memgraph/gqlalchemy/blob/main/gqlalchemy/transformations/translators/nx_translator.py)

Translating the graph means that you can **import** NetworkX graph into Memgraph as well as **export** data from Memgraph into NetworkX graph in your Python code. The `NxTranslator` defines three important methods:
 
- [`to_cypher_queries()`](#to_cypher_queries-method) - The method which generates Cypher queries to create a graph in Memgraph.
- [`nx_graph_to_memgraph_parallel()`](#nx_graph_to_memgraph_parallel-method) - The method which generates Cypher queries to insert data into Memgraph in parallel.
- [`get_instance()`](#get_instance-method) - The method which creates NetworkX instance from the graph stored in Memgraph. 


### `to_cypher_queries()` method

The `to_cypher_queries()` method yields queries from the `NetworkXCypherBuilder` object. These queries are creating nodes (with indexes) and relationships. To create nodes with indexes, `create_index` in `config` must be set to `True`. In that case, label-property indexes will be created on `id` property of each node. With or without indexes, node creation follows the same set or rules. The value of the `labels` key in NetworkX node will be translated into Memgraph node labels. Other properties will be translated into the same key-value pairs in Memgraph. Every node will have `id` property matching its NetworkX identification number. After Cypher queries for the node creation are generated, then Cypher queries for relationship creation are being generated. Those Cypher queries will match nodes by their label and property `id` and create a relationship between them. The value of the `TYPE` key in NetworkX edge will be translated into relationship type in Memgraph. Any other property in NetworkX edge will be translated into the same key-value pair in Memgraph. To run the generated queries, following code can be used:

```
for query in NxTranslator().to_cypher_queries(nx_graph):
    memgraph.execute(query)
```

### `nx_graph_to_memgraph_parallel()` method

The `nx_graph_to_memgraph_parallel()` method is similar to the [`to_cypher_queries()`](#to_cypher_queries-method) method. It creates a graph inside Memgraph following the same set of rules, but it writes in parallel. To do that, it splits generated queries into query groups and opens up a new connection to Memgraph in order to run queries. It will warn you if you did not set `create_index` in `config` to `True`, because otherwise, the write process might take longer than expected. To run the generated queries, the following code can be used:

```
for query in NxTranslator().nx_graph_to_memgraph_parallel(nx_graph):
    memgraph.execute(query)
```

### `get_instance()` method

The `get_instance()` method translates data stored inside Memgraph into NetworkX graph. It traverses the graph and it stores node and relationship objects along with their properties in a NetworkX DiGraph object. Since NetworkX doesn't support node labels and relationship type in a way Memgraph does, they are encoded as node and edge properties, as values of `label` and `type` key. To create NetworkX graph from data stored in Memgraph, following code can be run:

```
graph =  NxTranslator().get_instance()
```

## PyG graph translator

The `PyGTranslator` class implements the PyG graph translator and inherits from the `Translator` class. The `PyGTranslator` class can be imported from the `gqlalchemy.transformations.translators.pyg_translator` module. 

[![docs-source](https://img.shields.io/badge/source-PyG%20Translator-FB6E00?logo=github&style=for-the-badge)](https://github.com/memgraph/gqlalchemy/blob/main/gqlalchemy/transformations/translators/pyg_translator.py)

Translating the graph means that you can **import** PyG graph into Memgraph as well as **export** data from Memgraph into PyG graph in your Python code. The `PyGTranslator` defines two important methods:
 
- [`to_cypher_queries()`](#to_cypher_queries-method-1) - The method which generates Cypher queries to create a graph in Memgraph.
- [`get_instance()`](#get_instance-method-1) - The method which creates PyG instance from the graph stored in Memgraph. 

### `to_cypher_queries()` method

The `to_cypher_queries()` method produces Cypher queries to create graph objects in Memgraph for both homogeneous and heterogeneous graph. This method can translate one-dimensional as well as multidimensional features to Memgraph properties. Isolated nodes in the graph won't get translated into Memgraph. Nodes and relationships will have property `pyg_id` set to the id they have as part of the PyG graph for the consistency reasons. To run the generated queries, following code can be used:

```
for query in PyGTranslator().to_cypher_queries(pyg_graph):
    memgraph.execute(query)
```


### `get_instance()` method

The `get_instance()` method returns an instance of PyG heterograph from all relationships stored in Memgraph. Isolated nodes are ignored because they don't contribute to message passing neural networks. Only numerical properties that are set on all nodes and relationships are translated to the PyG instance since that is PyG requirement. Hence, any string properties, as well as numerical properties that aren't set on all nodes or relationships, won't be translated to the PyG instance. However, properties of type list will be translated to the PyG instance as a feature. Regardless of how data is connected in Memgraph, the returned PyG graph will be a heterograph instance. To create PyG graph from data stored in Memgraph, the following code can be run:

```
graph =  PyGTranslator().get_instance()
```

## DGL graph translator

The `DGLTranslator` class implements the DGL graph translator and inherits from the `Translator` class. The `DGLTranslator` class can be imported from the `gqlalchemy.transformations.translators.dgl_translator` module. 

[![docs-source](https://img.shields.io/badge/source-DGL%20Translator-FB6E00?logo=github&style=for-the-badge)](https://github.com/memgraph/gqlalchemy/blob/main/gqlalchemy/transformations/translators/dgl_translator.py)

Translating the graph means that you can **import** DGL graph into Memgraph as well as **export** data from Memgraph into DGL graph in your Python code. The `DGLTranslator` defines two important methods:
 
- [`to_cypher_queries()`](#to_cypher_queries-method-2) - The method which generates Cypher queries to create a graph in Memgraph.
- [`get_instance()`](#get_instance-method-2) - The method which creates PyG instance from the graph stored in Memgraph. 

### `to_cypher_queries()` method

The `to_cypher_queries()` method produces Cypher queries to create graph objects in Memgraph for both homogeneous and heterogeneous graph. If the graph is homogeneous, the default `_N` as a node label and `_E` as a relationship label will be used. This method can translate one-dimensional as well as multidimensional features to Memgraph properties. Isolated nodes in the graph won't get translated into Memgraph. Nodes and relationships will have property `dgl_id` set to the ID they have as part of the DGL graph for the consistency reasons. To run the generated queries, the following code can be used:

```
for query in DGLTranslator().to_cypher_queries(dgl_graph):
    memgraph.execute(query)
```

### `get_instance()` method

The `get_instance()` method returns instance of DGL heterograph from all relationships stored in Memgraph. Isolated nodes are ignored because they don't contribute in message passing neural networks. Only numerical properties that are set on all nodes and relationships are translated to the DGL instance since that is DGL requirement. Hence, any string properties, as well as numerical properties, that aren't set on all nodes or relationships, won't be translated to the DGL instance. However, properties of type list will be translated to the PyG instance as a feature. Regardless of how data is connected in Memgraph, the returned DGL graph will be a heterograph instance. To create DGL graph from data stored in Memgraph, following code can be run:

```
graph =  DGLTranslator().get_instance()
```

## Where to next?

If you want to learn more about using NetworkX with Memgraph with interesting resources and courses, head over to the [**Memgraph for NetworkX developers**](https://memgraph.com/memgraph-for-networkx?utm_source=docs&utm_medium=referral&utm_campaign=networkx_ppp&utm_term=docsgqla%2Bhowto&utm_content=textlink) website. If you have any questions or want to connect with the Memgraph community, [**join our Discord server**](https://www.discord.gg/memgraph).
