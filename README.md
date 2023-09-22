# GQLAlchemy

<p>
    <a href="https://github.com/memgraph/gqlalchemy/actions"><img src="https://github.com/memgraph/gqlalchemy/workflows/Build%20and%20Test/badge.svg" /></a>
    <a href="https://github.com/memgraph/gqlalchemy/blob/main/LICENSE"><img src="https://img.shields.io/github/license/memgraph/gqlalchemy" /></a>
    <a href="https://pypi.org/project/gqlalchemy"><img src="https://img.shields.io/pypi/v/gqlalchemy" /></a>
    <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
    <a href="https://memgraph.com/docs/gqlalchemy" alt="Documentation"><img src="https://img.shields.io/badge/documentation-GQLAlchemy-orange" /></a>
    <a href="https://github.com/memgraph/gqlalchemy/stargazers" alt="Stargazers"><img src="https://img.shields.io/github/stars/memgraph/gqlalchemy?style=social" /></a>
</p>

**GQLAlchemy** is a fully open-source Python library and **Object Graph Mapper** (OGM) - a link between graph database objects and Python objects.

An Object Graph Mapper or OGM provides a developer-friendly workflow that allows for writing object-oriented notation to communicate with graph databases. Instead of writing Cypher queries, you will be able to write object-oriented code, which the OGM will automatically translate into Cypher queries.

## Installation

To install GQLAlchemy, you will need the following:

- **Python 3.8 - 3.11**
- `pymgclient` [build prerequisites](https://memgraph.github.io/pymgclient/introduction.html#build-prerequisites): GQLAlchemy is built on top of Memgraph's low-level Python client `pymgclient`

> [!WARNING]  
> Python 3.11 users: On Windows, GQLAlchemy is not yet compatible with this Python version. Linux users can install GQLAlchemy **without** the DGL extra (due to its dependencies not supporting Python 3.11 yet). If this is currently a blocker for you, please let us know by [opening an issue](https://github.com/memgraph/gqlalchemy/issues).

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

If you are using the zsh terminal, surround `gqlalchemy[$extras]` with quotes:

    ```bash
    pip install 'gqlalchemy[arrow]'
    ```

If you intend to use GQLAlchemy with PyTorch Geometric support, that library must be installed manually:

```bash
pip install gqlalchemy[torch_pyg] # prerequisite
pip install torch-scatter torch-sparse torch-cluster torch-spline-conv torch-geometric -f https://data.pyg.org/whl/torch-1.13.0+cpu.html"
```

If you are using [Conda](https://docs.conda.io/en/latest/) for Python environment management, you can install GQLAlchemy through pip.

## Build & Test

The project uses [Poetry](https://python-poetry.org/) to build the library. Clone or download the [GQLAlchemy source code](https://github.com/memgraph/gqlalchemy) locally and run the following command to build it from source with Poetry:

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

To run the tests, make sure you have an [active Memgraph instance](https://memgraph.com/docs/getting-started), and execute one of the following commands:

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

## Development (how to build)

```bash
poetry run flake8 .
poetry run black .
poetry run pytest . -k "not slow and not extras"
```

## Documentation

The GQLAlchemy documentation is available on [GitHub](https://memgraph.github.io/gqlalchemy/).

The reference guide can be generated from the code by executing:

```
pip3 install pydoc-markdown
pydoc-markdown
```

Other parts of the documentation are written and located at docs directory. To test the documentation locally execute:

```
pip3 install mkdocs
pip3 install mkdocs-material
pip3 install pymdown-extensions
mkdocs serve
```

## License

Copyright (c) 2016-2022 [Memgraph Ltd.](https://memgraph.com)

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
