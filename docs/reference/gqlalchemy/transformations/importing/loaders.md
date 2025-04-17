---
sidebar_label: loaders
title: gqlalchemy.transformations.importing.loaders
---

## ForeignKeyMapping Objects

```python
@dataclass(frozen=True)
class ForeignKeyMapping()
```

Class that contains the full description of a single foreign key in a table.

**Attributes**:

- `column_name` - Column name that holds the foreign key.
- `reference_table` - Name of a table from which the foreign key is taken.
- `reference_key` - Column name in the referenced table from which the foreign key is taken.

## OneToManyMapping Objects

```python
@dataclass(frozen=True)
class OneToManyMapping()
```

Class that holds the full description of a single one to many mapping in a table.

**Attributes**:

- `foreign_key` - Foreign key used for mapping.
- `label` - Label which will be applied to the relationship created from this object.
- `from_entity` - Direction of the relationship created from the mapping object.

## ManyToManyMapping Objects

```python
@dataclass(frozen=True)
class ManyToManyMapping()
```

Class that holds the full description of a single many to many mapping in a table.
Many to many mapping is intended to be used in case of associative tables.

**Attributes**:

- `foreign_key_from` - Describes the source of the relationship.
- `foreign_key_to` - Describes the destination of the relationship.
- `label` - Label to be applied to the newly created relationship.
- `properties` - Properties that will be added to the relationship created from this object (Optional).

## TableMapping Objects

```python
@dataclass
class TableMapping()
```

Class that holds the full description of all of the mappings for a single table.

**Attributes**:

- `table_name` - Name of the table.
- `mapping` - All of the mappings in the table (Optional).
- `indices` - List of the indices to be created for this table (Optional).

## NameMappings Objects

```python
@dataclass(frozen=True)
class NameMappings()
```

Class that contains new label name and all of the column name mappings for a single table.

**Attributes**:

- `label` - New label (Optional).
- `column_names_mapping` - Dictionary containing key-value pairs in form (&quot;column name&quot;, &quot;property name&quot;) (Optional).

## NameMapper Objects

```python
class NameMapper()
```

Class that holds all name mappings for all of the collections.

#### get\_label

```python
def get_label(collection_name: str) -> str
```

Returns label for given collection.

**Arguments**:

- `collection_name` - Original collection name.

#### get\_property\_name

```python
def get_property_name(collection_name: str, column_name: str) -> str
```

Returns property name for column from collection.

**Arguments**:

- `collection_name` - Original collection name.
- `column_name` - Original column name.

## FileSystemHandler Objects

```python
class FileSystemHandler(ABC)
```

Abstract class for defining FileSystemHandler.

Inherit this class, define a custom data source and initialize the
connection.

#### get\_path

```python
@abstractmethod
def get_path(collection_name: str) -> str
```

Returns complete path in specific file system. Used to read the file system
for a specific file.

## S3FileSystemHandler Objects

```python
class S3FileSystemHandler(FileSystemHandler)
```

Handles connection to Amazon S3 service via PyArrow.

#### \_\_init\_\_

```python
def __init__(bucket_name: str, **kwargs)
```

Initializes connection and data bucket.

**Arguments**:

- `bucket_name` - Name of the bucket on S3 from which to read the data
  
  Kwargs:
- `access_key` - S3 access key.
- `secret_key` - S3 secret key.
- `region` - S3 region.
- `session_token` - S3 session token (Optional).
  

**Raises**:

- `KeyError` - kwargs doesn&#x27;t contain necessary fields.

#### get\_path

```python
def get_path(collection_name: str) -> str
```

Get file path in file system.

**Arguments**:

- `collection_name` - Name of the file to read.

## AzureBlobFileSystemHandler Objects

```python
class AzureBlobFileSystemHandler(FileSystemHandler)
```

Handles connection to Azure Blob service via adlfs package.

#### \_\_init\_\_

```python
def __init__(container_name: str, **kwargs) -> None
```

Initializes connection and data container.

**Arguments**:

- `container_name` - Name of the Blob container storing data.
  
  Kwargs:
- `account_name` - Account name from Azure Blob.
- `account_key` - Account key for Azure Blob (Optional - if using sas_token).
- `sas_token` - Shared access signature token for authentication (Optional).
  

**Raises**:

- `KeyError` - kwargs doesn&#x27;t contain necessary fields.

#### get\_path

```python
def get_path(collection_name: str) -> str
```

Get file path in file system.

**Arguments**:

- `collection_name` - Name of the file to read.

## LocalFileSystemHandler Objects

```python
class LocalFileSystemHandler(FileSystemHandler)
```

Handles a local filesystem.

#### \_\_init\_\_

```python
def __init__(path: str) -> None
```

Initializes an fsspec local file system and sets path to data.

**Arguments**:

- `path` - path to the local storage location.

#### get\_path

```python
def get_path(collection_name: str) -> str
```

Get file path in the local file system.

**Arguments**:

- `collection_name` - Name of the file to read.

## DataLoader Objects

```python
class DataLoader(ABC)
```

Implements loading of a data type from file system service to TableToGraphImporter.

#### \_\_init\_\_

```python
def __init__(file_extension: str,
             file_system_handler: FileSystemHandler) -> None
```

**Arguments**:

- `file_extension` - File format to be read.
- `file_system_handler` - Object for handling of the file system service.

#### load\_data

```python
@abstractmethod
def load_data(collection_name: str, is_cross_table: bool = False) -> None
```

Override this method in the derived class. Intended to be used for reading data from data format.

**Arguments**:

- `collection_name` - Name of the file to read.
- `is_cross_table` - Indicate whether or not the collection contains associative table (default=False).
  

**Raises**:

- `NotImplementedError` - The method is not implemented in the extended class.

## PyArrowFileTypeEnum Objects

```python
class PyArrowFileTypeEnum(Enum)
```

Enumerates file types supported by PyArrow

## PyArrowDataLoader Objects

```python
class PyArrowDataLoader(DataLoader)
```

Loads data using PyArrow.

PyArrow currently supports &quot;parquet&quot;, &quot;ipc&quot;/&quot;arrow&quot;/&quot;feather&quot;, &quot;csv&quot;,
and &quot;orc&quot;, see pyarrow.dataset.dataset for up-to-date info.
ds.dataset in load_data accepts any fsspec subclass, making this DataLoader
compatible with fsspec-compatible filesystems.

#### \_\_init\_\_

```python
def __init__(file_extension_enum: PyArrowFileTypeEnum,
             file_system_handler: FileSystemHandler) -> None
```

**Arguments**:

- `file_extension_enum` - The file format to be read.
- `file_system_handler` - Object for handling of the file system service.

#### load\_data

```python
def load_data(collection_name: str,
              is_cross_table: bool = False,
              columns: Optional[List[str]] = None) -> None
```

Generator for loading data.

**Arguments**:

- `collection_name` - Name of the file to read.
- `is_cross_table` - Flag signifying whether it is a cross table.
- `columns` - Table columns to read.

## TableToGraphImporter Objects

```python
class TableToGraphImporter(Importer)
```

Implements translation of table data to graph data, and imports it to Memgraph.

#### \_\_init\_\_

```python
def __init__(data_loader: DataLoader,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None) -> None
```

**Arguments**:

- `data_loader` - Object for loading data.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).

#### translate

```python
def translate(drop_database_on_start: bool = True) -> None
```

Performs the translations.

**Arguments**:

- `drop_database_on_start` - Indicate whether or not the database should be dropped prior to the start of the translations.

## PyArrowImporter Objects

```python
class PyArrowImporter(TableToGraphImporter)
```

TableToGraphImporter wrapper for use with PyArrow for reading data.

#### \_\_init\_\_

```python
def __init__(file_system_handler: str,
             file_extension_enum: PyArrowFileTypeEnum,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None) -> None
```

**Arguments**:

- `file_system_handler` - File system to read from.
- `file_extension_enum` - File format to be read.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).
  

**Raises**:

- `ValueError` - PyArrow doesn&#x27;t support ORC on Windows.

## PyArrowS3Importer Objects

```python
class PyArrowS3Importer(PyArrowImporter)
```

PyArrowImporter wrapper for use with the Amazon S3 File System.

#### \_\_init\_\_

```python
def __init__(bucket_name: str,
             file_extension_enum: PyArrowFileTypeEnum,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None,
             **kwargs) -> None
```

**Arguments**:

- `bucket_name` - Name of the bucket in S3 to read from.
- `file_extension_enum` - File format to be read.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).
- `**kwargs` - Specified for S3FileSystem.

## PyArrowAzureBlobImporter Objects

```python
class PyArrowAzureBlobImporter(PyArrowImporter)
```

PyArrowImporter wrapper for use with the Azure Blob File System.

#### \_\_init\_\_

```python
def __init__(container_name: str,
             file_extension_enum: PyArrowFileTypeEnum,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None,
             **kwargs) -> None
```

**Arguments**:

- `container_name` - Name of the container in Azure Blob to read from.
- `file_extension_enum` - File format to be read.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).
- `**kwargs` - Specified for AzureBlobFileSystem.

## PyArrowLocalFileSystemImporter Objects

```python
class PyArrowLocalFileSystemImporter(PyArrowImporter)
```

PyArrowImporter wrapper for use with the Local File System.

#### \_\_init\_\_

```python
def __init__(path: str,
             file_extension_enum: PyArrowFileTypeEnum,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None) -> None
```

**Arguments**:

- `path` - Full path to the directory to read from.
- `file_extension_enum` - File format to be read.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).

## ParquetS3FileSystemImporter Objects

```python
class ParquetS3FileSystemImporter(PyArrowS3Importer)
```

PyArrowS3Importer wrapper for use with the S3 file system and the parquet file type.

#### \_\_init\_\_

```python
def __init__(bucket_name: str,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None,
             **kwargs) -> None
```

**Arguments**:

- `bucket_name` - Name of the bucket in S3 to read from.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).
- `**kwargs` - Specified for S3FileSystem.

## CSVS3FileSystemImporter Objects

```python
class CSVS3FileSystemImporter(PyArrowS3Importer)
```

PyArrowS3Importer wrapper for use with the S3 file system and the CSV file type.

#### \_\_init\_\_

```python
def __init__(bucket_name: str,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None,
             **kwargs) -> None
```

**Arguments**:

- `bucket_name` - Name of the bucket in S3 to read from.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).
- `**kwargs` - Specified for S3FileSystem.

## ORCS3FileSystemImporter Objects

```python
class ORCS3FileSystemImporter(PyArrowS3Importer)
```

PyArrowS3Importer wrapper for use with the S3 file system and the ORC file type.

#### \_\_init\_\_

```python
def __init__(bucket_name: str,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None,
             **kwargs) -> None
```

**Arguments**:

- `bucket_name` - Name of the bucket in S3 to read from.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).
- `**kwargs` - Specified for S3FileSystem.

## FeatherS3FileSystemImporter Objects

```python
class FeatherS3FileSystemImporter(PyArrowS3Importer)
```

PyArrowS3Importer wrapper for use with the S3 file system and the feather file type.

#### \_\_init\_\_

```python
def __init__(bucket_name: str,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None,
             **kwargs) -> None
```

**Arguments**:

- `bucket_name` - Name of the bucket in S3 to read from.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).
- `**kwargs` - Specified for S3FileSystem.

## ParquetAzureBlobFileSystemImporter Objects

```python
class ParquetAzureBlobFileSystemImporter(PyArrowAzureBlobImporter)
```

PyArrowAzureBlobImporter wrapper for use with the Azure Blob file system and the parquet file type.

#### \_\_init\_\_

```python
def __init__(container_name: str,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None,
             **kwargs) -> None
```

**Arguments**:

- `container_name` - Name of the container in Azure Blob storage to read from.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).
- `**kwargs` - Specified for AzureBlobFileSystem.

## CSVAzureBlobFileSystemImporter Objects

```python
class CSVAzureBlobFileSystemImporter(PyArrowAzureBlobImporter)
```

PyArrowAzureBlobImporter wrapper for use with the Azure Blob file system and the CSV file type.

#### \_\_init\_\_

```python
def __init__(container_name: str,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None,
             **kwargs) -> None
```

**Arguments**:

- `container_name` - Name of the container in Azure Blob storage to read from.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).
- `**kwargs` - Specified for AzureBlobFileSystem.

## ORCAzureBlobFileSystemImporter Objects

```python
class ORCAzureBlobFileSystemImporter(PyArrowAzureBlobImporter)
```

PyArrowAzureBlobImporter wrapper for use with the Azure Blob file system and the CSV file type.

#### \_\_init\_\_

```python
def __init__(container_name,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None,
             **kwargs) -> None
```

**Arguments**:

- `container_name` - Name of the container in Blob storage to read from.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).
- `**kwargs` - Specified for AzureBlobFileSystem.

## FeatherAzureBlobFileSystemImporter Objects

```python
class FeatherAzureBlobFileSystemImporter(PyArrowAzureBlobImporter)
```

PyArrowAzureBlobImporter wrapper for use with the Azure Blob file system and the Feather file type.

#### \_\_init\_\_

```python
def __init__(container_name,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None,
             **kwargs) -> None
```

**Arguments**:

- `container_name` - Name of the container in Blob storage to read from.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).
- `**kwargs` - Specified for AzureBlobFileSystem.

## ParquetLocalFileSystemImporter Objects

```python
class ParquetLocalFileSystemImporter(PyArrowLocalFileSystemImporter)
```

PyArrowLocalFileSystemImporter wrapper for use with the local file system and the parquet file type.

#### \_\_init\_\_

```python
def __init__(path: str,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None) -> None
```

**Arguments**:

- `path` - Full path to directory.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).
- `**kwargs` - Specified for LocalFileSystem.

## CSVLocalFileSystemImporter Objects

```python
class CSVLocalFileSystemImporter(PyArrowLocalFileSystemImporter)
```

PyArrowLocalFileSystemImporter wrapper for use with the local file system and the CSV file type.

#### \_\_init\_\_

```python
def __init__(path: str,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None) -> None
```

**Arguments**:

- `path` - Full path to directory.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).
- `**kwargs` - Specified for LocalFileSystem.

## ORCLocalFileSystemImporter Objects

```python
class ORCLocalFileSystemImporter(PyArrowLocalFileSystemImporter)
```

PyArrowLocalFileSystemImporter wrapper for use with the local file system and the ORC file type.

#### \_\_init\_\_

```python
def __init__(path: str,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None) -> None
```

**Arguments**:

- `path` - Full path to directory.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).
- `**kwargs` - Specified for LocalFileSystem.

## FeatherLocalFileSystemImporter Objects

```python
class FeatherLocalFileSystemImporter(PyArrowLocalFileSystemImporter)
```

PyArrowLocalFileSystemImporter wrapper for use with the local file system and the Feather/IPC/Arrow file type.

#### \_\_init\_\_

```python
def __init__(path: str,
             data_configuration: Dict[str, Any],
             memgraph: Optional[Memgraph] = None) -> None
```

**Arguments**:

- `path` - Full path to directory.
- `data_configuration` - Configuration for the translations.
- `memgraph` - Connection to Memgraph (Optional).
- `**kwargs` - Specified for LocalFileSystem.

