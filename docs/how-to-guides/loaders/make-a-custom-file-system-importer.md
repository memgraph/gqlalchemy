# How to make a custom file system importer

> To learn how to import table data from a file to the Memgraph database, head
> over to the [How to import table
> data](import-table-data-to-graph-database.md) guide.

If you want to read from a file system not currently supported by
**GQLAlchemy**, or use a file type currently not readable, you can implement
your own by extending abstract classes `FileSystemHandler` and `DataLoader`,
respectively.

!!! info
    You can also use this feature with Neo4j:

    ```python
    db = Neo4j(host="localhost", port="7687", username="neo4j", password="test")
    ```

!!! info
    The features below aren’t included in the default GQLAlchemy installation. To use them, make sure to [install GQLAlchemy](../../installation.md) with the relevant extras.

## Implementing a new `FileSystemHandler`

For this guide, you will use the existing `PyArrowDataLoader` capable of reading
CSV, Parquet, ORC and IPC/Feather/Arrow file formats. The PyArrow loader class
supports [fsspec](https://filesystem-spec.readthedocs.io/en/latest/)-compatible
file systems, so to implement an **Azure Blob** file system, you need to follow
these steps.

### 1. Extend the `FileSystemHandler` class

This class holds the connection to the file system service and handles the path
from which the `DataLoader` object reads files. To get a fsspec-compatible instance of
an Azure Blob connection, you can use the [adlfs](https://github.com/fsspec/adlfs) package. We are going to pass `adlfs`-specific parameters such as `account_name` and `account_key` via kwargs. All that's left to do
is to override the `get_path` method.

```python
import adlfs

class AzureBlobFileSystemHandler(FileSystemHandler):

    def __init__(self, container_name: str, **kwargs) -> None:
        """Initializes connection and data container."""
        super().__init__(fs=adlfs.AzureBlobFileSystem(**kwargs))
        self._container_name = container_name

    def get_path(self, collection_name: str) -> str:
        """Get file path in file system."""
        return f"{self._container_name}/{collection_name}"
```

### 2. Wrap the `TableToGraphImporter`

Next, you are going to wrap the `TableToGraphImporter` class. This is optional since you can use the class directly, but it will be easier to use if we extend it with our custom importer class. Since we will be using PyArrow for data loading, you can extend the `PyArrowImporter` class (which extends the `TableToGraphImporter`) and make your own
`PyArrowAzureBlobImporter`. This class should initialize the `AzureBlobFileSystemHandler` and leave the rest to the `PyArrowImporter` class. It should also receive a `file_extension_enum` argument, which defines the file type that you are going to be reading.

```python
class PyArrowAzureBlobImporter(PyArrowImporter):
    """PyArrowImporter wrapper for use with Azure Blob File System."""

    def __init__(
        self,
        container_name: str,
        file_extension_enum: PyArrowFileTypeEnum,
        data_configuration: Dict[str, Any],
        memgraph: Optional[Memgraph] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            file_system_handler=AzureBlobFileSystemHandler(        
                container_name=container_name, **kwargs
            ),
            file_extension_enum=file_extension_enum,
            data_configuration=data_configuration,
            memgraph=memgraph,
        )
```

### 3. Call `translate()`

Finally, to use your custom file system, initialize the Importer class and call
`translate()`

```python
importer = PyArrowAzureBlobImporter(
    container_name="test"
    file_extension_enum=PyArrowFileTypeEnum.Parquet,
    data_configuration=parsed_yaml,
    account_name="your_account_name",
    account_key="your_account_key",
)

importer.translate(drop_database_on_start=True)
```

If you want to see the full implementation of the `AzureBlobFileSystem` and
other loader components, have a look [at the
code](https://github.com/memgraph/gqlalchemy). Feel free to create a PR on the
GQLAlchemy repository if you think of a new feature we could use. If you have
any more questions, join our community and ping us on
[Discord](https://discord.gg/memgraph).
