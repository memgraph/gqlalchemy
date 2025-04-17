# How to install GQLAlchemy

There are two main ways of installing GQLAlchemy: with package managers such
as pip and Poetry, and by building it from source.

## Prerequisites

To install GQLAlchemy, you will need the following:

- **Python 3.9 - 3.12**
- [`pymgclient`](https://github.com/memgraph/pymgclient):

    * Install `pymgclient` [build prerequisites](https://memgraph.github.io/pymgclient/introduction.html#build-prerequisites)
    * Install `pymgclient` via pip:

    ```bash
    pip install --user pymgclient
    ```

!!! danger
    Python 3.11 users: On Windows, GQLAlchemy is not yet compatible with this Python version. If this is currently a blocker for you, please let us know by [opening an issue](https://github.com/memgraph/gqlalchemy/issues).

## Install with pip

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
pip install gqlalchemy[docker] # Docker support

pip install gqlalchemy[all] # All of the above
```

If you intend to use GQLAlchemy with PyTorch Geometric support, that library must be installed manually:

```bash
pip install gqlalchemy[torch_pyg] # prerequisite
pip install torch-scatter torch-sparse torch-cluster torch-spline-conv torch-geometric -f https://data.pyg.org/whl/torch-1.13.0+cpu.html"
```

!!! note
    If you are using the zsh terminal, surround `gqlalchemy[$extras]` with quotes:
    ```bash
    pip install 'gqlalchemy[arrow]'
    ```
## Build from source

Clone or download the [GQLAlchemy source code](https://github.com/memgraph/gqlalchemy) locally and run the following command to build it from source with Poetry:

```bash
poetry install --all-extras
```

The `poetry install --all-extras` command installs GQLAlchemy with all extras
(optional dependencies). Alternatively, you can use the `-E` option to define
what extras to install:

```bash
poetry install # No extras

poetry install -E arrow # Support for the CSV, Parquet, ORC and IPC/Feather/Arrow formats
poetry install -E dgl # DGL support (also includes torch)
poetry install -E docker # Docker support

```

To run the tests, make sure you have an [active Memgraph instance](https://memgraph.com/docs/getting-started/install-memgraph), and execute one of the following commands:

```bash
poetry run pytest . -k "not slow" # If all extras installed

poetry run pytest . -k "not slow and not extras" # Otherwise
```

If you’ve installed only certain extras, it’s also possible to run their associated tests:

```bash
poetry run pytest . -k "arrow"
poetry run pytest . -k "dgl"
poetry run pytest . -k "docker"
```
