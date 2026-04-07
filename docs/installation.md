# How to install GQLAlchemy

There are two main ways of installing GQLAlchemy: with package managers such
as pip and uv, and by building it from source.

## Prerequisites

To install GQLAlchemy, you will need the following:

- **Python 3.10 - 3.12**
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
pip install gqlalchemy[dot] # DOT graph import support (pydot)
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

Clone or download the [GQLAlchemy source code](https://github.com/memgraph/gqlalchemy) locally and run the following command to build it from source with [uv](https://docs.astral.sh/uv/):

```bash
uv sync --all-extras
```

The `uv sync --all-extras` command installs GQLAlchemy with all extras
(optional dependencies). Alternatively, you can use the `--extra` option to define
what extras to install:

```bash
uv sync # No extras

uv sync --extra arrow # Support for the CSV, Parquet, ORC and IPC/Feather/Arrow formats
uv sync --extra dgl # Installs torch (DGL must be installed separately, see below)
uv sync --extra dot # DOT graph import support (pydot)
uv sync --extra docker # Docker support

```

The `dgl` and `torch_pyg` extras install PyTorch only. DGL and PyTorch Geometric wheels
must be installed separately due to their custom package indexes:

```bash
# DGL
uv sync --extra dgl
uv pip install dgl -f https://data.dgl.ai/wheels/torch-2.4/repo.html

# PyTorch Geometric
uv sync --extra torch_pyg
uv pip install torch-scatter torch-sparse torch-cluster torch-spline-conv torch-geometric -f https://data.pyg.org/whl/torch-2.4.0+cpu.html
```

To run the tests, make sure you have an [active Memgraph instance](https://memgraph.com/docs/getting-started/install-memgraph), and execute one of the following commands:

```bash
uv run pytest . -k "not slow" # If all extras installed

uv run pytest . -k "not slow and not extras" # Otherwise
```

If you’ve installed only certain extras, it’s also possible to run their associated tests:

```bash
uv run pytest . -k "arrow"
uv run pytest . -k "dgl"
uv run pytest . -k "docker"
```
