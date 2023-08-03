---
id: installation
title: How to install GQLAlchemy
sidebar_label: Installation
---

There are two main ways of installing GQLAlchemy: with package managers such
as pip and Poetry, and by building it from source.

## Prerequisites

To install GQLAlchemy, you will need the following:

- **Python 3.8 - 3.10**
- GQLAlchemy is built on top of Memgraph's low-level Python client `pymgclient`, so you need to install `pymgclient` [build prerequisites](https://memgraph.github.io/pymgclient/introduction.html#build-prerequisites).

:::caution
GQLAlchemy can't be installed with Python 3.11 [(#203)](https://github.com/memgraph/gqlalchemy/issues/203) and on Windows with Python >= 3.10 [(#179)](https://github.com/memgraph/gqlalchemy/issues/179). If this is currently a blocker for you, please let us know by commenting on opened issues.
:::

## Install with pip {#pip}

After you’ve installed the prerequisites, run the following command to install
GQLAlchemy:

```bash
pip install gqlalchemy
```

With the above command, you get the default GQLAlchemy installation which
doesn’t include import/export support for certain formats (see below). To get
additional import/export capabilities, use one of the following install options:

```bash
pip install gqlalchemy[arrow] # Support for the CSV, Parquet, ORC and IPC/Feather/Arrow formats
pip install gqlalchemy[dgl] # DGL support (also includes torch)

pip install gqlalchemy[all] # All of the above
```

:::note
If you are using zsh terminal, you need to pass literal square brackets as an argument to a command:
```
pip install 'gqlalchemy[arrow]'
```
:::

## Build from source

Clone or download the [GQLAlchemy source code](https://github.com/memgraph/gqlalchemy) locally and run the following command to build it from source with Poetry:

```bash
poetry install --all-extras
```

The ``poetry install --all-extras`` command installs GQLAlchemy with all extras
(optional dependencies). Alternatively, you can use the ``-E`` option to define
what extras to install:

```bash
poetry install # No extras

poetry install -E arrow # Support for the CSV, Parquet, ORC and IPC/Feather/Arrow formats
poetry install -E dgl # DGL support (also includes torch)

```

To run the tests, make sure you have an [active Memgraph instance](/memgraph), and execute one of the following commands:

```bash
poetry run pytest . -k "not slow" # If all extras installed

poetry run pytest . -k "not slow and not extras" # Otherwise
```

If you’ve installed only certain extras, it’s also possible to run their associated tests:

```bash
poetry run pytest . -k "arrow"
poetry run pytest . -k "dgl"
```
