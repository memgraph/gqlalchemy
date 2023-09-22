# Getting started with GQLAlchemy

[![GQLAlchemy](https://img.shields.io/badge/source-GQLAlchemy-FB6E00?style=for-the-badge&logo=github&logoColor=white)](https://github.com/memgraph/gqlalchemy)

**GQLAlchemy** is an open-source Python library and an **Object Graph Mapper** (OGM) - a link between graph database objects and Python objects. GQLAlchemy supports **Memgraph** and **Neo4j**.

An Object Graph Mapper or OGM provides a developer-friendly workflow for writing object-oriented notation to communicate to a graph database. Instead of writing Cypher queries, you can write object-oriented code, which the OGM will automatically translate into Cypher queries.

## Quick start

### 1. Install GQLAlchemy

Either install GQLAlchemy through [pip](installation.md#pip) or [build it from
source](installation.md#source). If you are using [Conda](https://docs.conda.io/en/latest/) for Python environment management, you can install GQLAlchemy through [pip](installation.md#pip).

!!! danger
    Python 3.11 users: On Windows, GQLAlchemy is not yet compatible with this Python version. Linux users can install GQLAlchemy **without** the DGL extra (due to its dependencies not supporting Python 3.11 yet). If this is currently a blocker for you, please let us know by [opening an issue](https://github.com/memgraph/gqlalchemy/issues).

### 2. Connect to Memgraph

Check the [Python quick start guide](https://memgraph.com/docs) to learn how to connect to Memgraph using GQLAlchemy.

### 3. Learn how to use GQLAlchemy

With the help of the [How-to guides](how-to-guides/overview.md) you can learn how to use GQLAlchemy's features, such as object graph mapper and query builder. 

### 3. Check the reference guide

Don't forget to check the [Reference guide](reference/gqlalchemy/overview.md) if you want to find out which methods GQLAlchemy has and how to use it. If the reference guide is not clear enough, head over to the [GQLAlchemy repository](https://github.com/memgraph/gqlalchemy) and inspect the source code. While you're there, feel free to give us a star or contribute to this open-source Python library.
