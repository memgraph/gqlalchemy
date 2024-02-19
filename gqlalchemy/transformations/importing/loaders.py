# Copyright (c) 2016-2023 Memgraph Ltd. [https://memgraph.com]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import platform
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from string import Template
from typing import List, Dict, Any, Optional, Union

import adlfs

try:
    import pyarrow.dataset as ds
except ModuleNotFoundError:
    ds = None
try:
    from pyarrow import fs
except ModuleNotFoundError:
    fs = None
from dacite import from_dict

from gqlalchemy import Memgraph
from gqlalchemy.models import (
    MemgraphIndex,
    MemgraphTrigger,
    TriggerEventObject,
    TriggerEventType,
    TriggerExecutionPhase,
)
from gqlalchemy.query_builders.memgraph_query_builder import Operator, QueryBuilder, Unwind
from gqlalchemy.transformations.importing.importer import Importer

NAME_MAPPINGS_KEY = "name_mappings"
ONE_TO_MANY_RELATIONS_KEY = "one_to_many_relations"
INDICES_KEY = "indices"
MANY_TO_MANY_RELATIONS_KEY = "many_to_many_relations"

FROM_NODE_VARIABLE_NAME = "from_node"
TO_NODE_VARIABLE_NAME = "to_node"

NODE_A = "a"
NODE_B = "b"

PARQUET_EXTENSION = "parquet"
CSV_EXTENSION = "csv"
ORC_EXTENSION = "orc"
IPC_EXTENSION = "ipc"
FEATHER_EXTENSION = "feather"
ARROW_EXTENSION = "arrow"

BLOB_ACCOUNT_NAME = "account_name"
BLOB_ACCOUNT_KEY = "account_key"
BLOB_SAS_TOKEN = "sas_token"
BLOB_CONTAINER_NAME_KEY = "container_name"

S3_REGION = "region"
S3_ACCESS_KEY = "access_key"
S3_SECRET_KEY = "secret_key"
S3_SESSION_TOKEN = "session_token"
S3_BUCKET_NAME_KEY = "bucket_name"

LOCAL_STORAGE_PATH = "local_storage_path"


@dataclass(frozen=True)
class ForeignKeyMapping:
    """Class that contains the full description of a single foreign key in a table.

    Attributes:
        column_name: Column name that holds the foreign key.
        reference_table: Name of a table from which the foreign key is taken.
        reference_key: Column name in the referenced table from which the foreign key is taken.
    """

    column_name: str
    reference_table: str
    reference_key: str


@dataclass(frozen=True)
class OneToManyMapping:
    """Class that holds the full description of a single one to many mapping in a table.

    Attributes:
        foreign_key: Foreign key used for mapping.
        label: Label which will be applied to the relationship created from this object.
        from_entity: Direction of the relationship created from the mapping object.
        parameters: Parameters that will be added to the relationship created from this object (Optional).
    """

    foreign_key: ForeignKeyMapping
    label: str
    from_entity: bool = False
    parameters: Optional[Dict[str, str]] = None


@dataclass(frozen=True)
class ManyToManyMapping:
    """Class that holds the full description of a single many to many mapping in a table.
    Many to many mapping is intended to be used in case of associative tables.

    Attributes:
        foreign_key_from: Describes the source of the relationship.
        foreign_key_to: Describes the destination of the relationship.
        label: Label to be applied to the newly created relationship.
        parameters: Parameters that will be added to the relationship created from this object (Optional).
    """

    foreign_key_from: ForeignKeyMapping
    foreign_key_to: ForeignKeyMapping
    label: str
    parameters: Optional[Dict[str, str]] = None


Mapping = Union[List[OneToManyMapping], ManyToManyMapping]


@dataclass
class TableMapping:
    """Class that holds the full description of all of the mappings for a single table.

    Attributes:
        table_name: Name of the table.
        mapping: All of the mappings in the table (Optional).
        indices: List of the indices to be created for this table (Optional).
    """

    table_name: str
    mapping: Optional[Mapping] = None
    indices: Optional[List[str]] = None


@dataclass(frozen=True)
class NameMappings:
    """Class that contains new label name and all of the column name mappings for a single table.

    Attributes:
        label: New label (Optional).
        column_names_mapping: Dictionary containing key-value pairs in form ("column name", "property name") (Optional).
    """

    label: Optional[str] = None
    column_names_mapping: Dict[str, str] = field(default_factory=dict)

    def get_property_name(self, column_name: str):
        return self.column_names_mapping.get(column_name, column_name)


class NameMapper:
    """Class that holds all name mappings for all of the collections."""

    def __init__(self, mappings: Dict[str, Any]) -> None:
        self._name_mappings: Dict[str, NameMappings] = {k: NameMappings(**v) for k, v in mappings.items()}

    def get_label(self, collection_name: str) -> str:
        """Returns label for given collection.

        Args:
            collection_name: Original collection name.
        """
        label = self._name_mappings[collection_name].label

        return label if label is not None else collection_name

    def get_property_name(self, collection_name: str, column_name: str) -> str:
        """Returns property name for column from collection.

        Args:
            collection_name: Original collection name.
            column_name: Original column name.
        """
        return self._name_mappings[collection_name].get_property_name(column_name=column_name)


class FileSystemHandler(ABC):
    """Abstract class for defining FileSystemHandler.

    Inherit this class, define a custom data source and initialize the
    connection.
    """

    def __init__(self, fs: Any) -> None:
        super().__init__()
        self._fs = fs

    @property
    def fs(self):
        return self._fs

    @abstractmethod
    def get_path(self, collection_name: str) -> str:
        """Returns complete path in specific file system. Used to read the file system
        for a specific file.
        """
        pass


class S3FileSystemHandler(FileSystemHandler):
    """Handles connection to Amazon S3 service via PyArrow."""

    def __init__(self, bucket_name: str, **kwargs):
        """Initializes connection and data bucket.

        Args:
            bucket_name: Name of the bucket on S3 from which to read the data

        Kwargs:
            access_key: S3 access key.
            secret_key: S3 secret key.
            region: S3 region.
            session_token: S3 session token (Optional).

        Raises:
            KeyError: kwargs doesn't contain necessary fields.
        """
        if S3_ACCESS_KEY not in kwargs:
            raise KeyError(f"{S3_ACCESS_KEY} is needed to connect to S3 storage")
        if S3_SECRET_KEY not in kwargs:
            raise KeyError(f"{S3_SECRET_KEY} is needed to connect to S3 storage")

        if fs is None:
            raise ModuleNotFoundError("No module named 'pyarrow'")

        super().__init__(fs=fs.S3FileSystem(**kwargs))
        self._bucket_name = bucket_name

    def get_path(self, collection_name: str) -> str:
        """Get file path in file system.

        Args:
            collection_name: Name of the file to read.
        """
        return f"{self._bucket_name}/{collection_name}"


class AzureBlobFileSystemHandler(FileSystemHandler):
    """Handles connection to Azure Blob service via adlfs package."""

    def __init__(self, container_name: str, **kwargs) -> None:
        """Initializes connection and data container.

        Args:
            container_name: Name of the Blob container storing data.

        Kwargs:
            account_name: Account name from Azure Blob.
            account_key: Account key for Azure Blob (Optional - if using sas_token).
            sas_token: Shared access signature token for authentication (Optional).

        Raises:
            KeyError: kwargs doesn't contain necessary fields.
        """
        if BLOB_ACCOUNT_KEY not in kwargs and BLOB_SAS_TOKEN not in kwargs:
            raise KeyError(f"{BLOB_ACCOUNT_KEY} or {BLOB_SAS_TOKEN} is needed to connect to Blob storage")
        if BLOB_ACCOUNT_NAME not in kwargs:
            raise KeyError(f"{BLOB_ACCOUNT_NAME} is needed to connect to Blob storage")

        super().__init__(fs=adlfs.AzureBlobFileSystem(**kwargs))
        self._container_name = container_name

    def get_path(self, collection_name: str) -> str:
        """Get file path in file system.

        Args:
            collection_name: Name of the file to read.
        """
        return f"{self._container_name}/{collection_name}"


class LocalFileSystemHandler(FileSystemHandler):
    """Handles a local filesystem."""

    def __init__(self, path: str) -> None:
        """Initializes an fsspec local file system and sets path to data.

        Args:
            path: path to the local storage location.
        """
        if fs is None:
            raise ModuleNotFoundError("No module named 'pyarrow'")

        super().__init__(fs=fs.LocalFileSystem())
        self._path = path

    def get_path(self, collection_name: str) -> str:
        """Get file path in the local file system.

        Args:
            collection_name: Name of the file to read.
        """
        return f"{self._path}/{collection_name}"


class DataLoader(ABC):
    """Implements loading of a data type from file system service to TableToGraphImporter."""

    def __init__(self, file_extension: str, file_system_handler: FileSystemHandler) -> None:
        """
        Args:
            file_extension: File format to be read.
            file_system_handler: Object for handling of the file system service.
        """
        super().__init__()
        self._file_extension = file_extension
        self._file_system_handler = file_system_handler

    @abstractmethod
    def load_data(self, collection_name: str, is_cross_table: bool = False) -> None:
        """Override this method in the derived class. Intended to be used for reading data from data format.

        Args:
            collection_name: Name of the file to read.
            is_cross_table: Indicate whether or not the collection contains associative table (default=False).

        Raises:
            NotImplementedError: The method is not implemented in the extended class.
        """
        raise NotImplementedError("Subclasses must override load_data() for use in TableToGraphImporter")


class PyArrowFileTypeEnum(Enum):
    """Enumerates file types supported by PyArrow"""

    Default = 1
    Parquet = 2
    CSV = 3
    ORC = 4
    Feather = 5


class PyArrowDataLoader(DataLoader):
    """Loads data using PyArrow.

    PyArrow currently supports "parquet", "ipc"/"arrow"/"feather", "csv",
    and "orc", see pyarrow.dataset.dataset for up-to-date info.
    ds.dataset in load_data accepts any fsspec subclass, making this DataLoader
    compatible with fsspec-compatible filesystems.
    """

    def __init__(
        self,
        file_extension_enum: PyArrowFileTypeEnum,
        file_system_handler: FileSystemHandler,
    ) -> None:
        """
        Args:
            file_extension_enum: The file format to be read.
            file_system_handler: Object for handling of the file system service.
        """
        super().__init__(file_extension=file_extension_enum.name.lower(), file_system_handler=file_system_handler)

    def load_data(
        self, collection_name: str, is_cross_table: bool = False, columns: Optional[List[str]] = None
    ) -> None:
        """Generator for loading data.

        Args:
            collection_name: Name of the file to read.
            is_cross_table: Flag signifying whether it is a cross table.
            columns: Table columns to read.
        """
        source = self._file_system_handler.get_path(f"{collection_name}.{self._file_extension}")
        print("Loading data from " + ("cross " if is_cross_table else "") + f"table {source}...")

        if ds is None:
            raise ModuleNotFoundError("No module named 'pyarrow'")

        dataset = ds.dataset(source=source, format=self._file_extension, filesystem=self._file_system_handler.fs)

        for batch in dataset.to_batches(
            columns=columns,
        ):
            for batch_item in batch.to_pylist():
                yield batch_item

        print("Data loaded.")


class TableToGraphImporter(Importer):
    """Implements translation of table data to graph data, and imports it to Memgraph."""

    _DIRECTION = {
        True: (NODE_A, NODE_B),
        False: (NODE_B, NODE_A),
    }

    _TriggerQueryTemplate = Template(
        Unwind(list_expression="createdVertices", variable="$node_a")
        .with_(results={"$node_a": ""})
        .where(item="$node_a", operator=Operator.LABEL_FILTER, expression="$label_2")
        .match()
        .node(labels="$label_1", variable="$node_b")
        .where(item="$node_b.$property_1", operator=Operator.EQUAL, expression="$node_a.$property_2")
        .create()
        .node(variable="$from_node")
        .to(relationship_type="$relationship_type")
        .node(variable="$to_node")
        .construct_query()
    )

    @staticmethod
    def _create_trigger_cypher_query(
        label1: str, label2: str, property1: str, property2: str, relationship_type: str, from_entity: bool
    ) -> str:
        """Creates a Cypher query for the translation trigger.

        Args:
            label1: Label of the first node.
            label2: Label of the second node.
            property1: Property of the first node.
            property2: Property of the second node.
            relationship_type: Label for the relationship that the trigger creates.
            from_entity: Indicate whether the relationship goes from or to the first entity.
        """
        from_node, to_node = TableToGraphImporter._DIRECTION[from_entity]

        return TableToGraphImporter._TriggerQueryTemplate.substitute(
            node_a=NODE_A,
            node_b=NODE_B,
            label_1=label1,
            label_2=label2,
            property_1=property1,
            property_2=property2,
            from_node=from_node,
            to_node=to_node,
            relationship_type=relationship_type,
        )

    def __init__(
        self,
        data_loader: DataLoader,
        data_configuration: Dict[str, Any],
        memgraph: Optional[Memgraph] = None,
    ) -> None:
        """
        Args:
            data_loader: Object for loading data.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).
        """
        self._data_loader: DataLoader = data_loader
        self._memgraph: Memgraph = memgraph if memgraph is not None else Memgraph()

        self.__load_configuration(data_configuration=data_configuration)

    def translate(self, drop_database_on_start: bool = True) -> None:
        """Performs the translations.

        Args:
            drop_database_on_start: Indicate whether or not the database should be dropped prior to the start of the translations.
        """
        if drop_database_on_start:
            self._memgraph.drop_database()
            self._memgraph.drop_indexes()
            self._memgraph.drop_triggers()

        self._create_indexes()
        self._create_triggers()

        self._load_nodes()
        self._load_cross_relationships()

    def _load_nodes(self) -> None:
        """Reads all of the data from the single table in the data source, translates it, and writes it to Memgraph."""
        for one_to_many_mapping in self._one_to_many_mappings:
            collection_name = one_to_many_mapping.table_name
            for row in self._data_loader.load_data(collection_name=collection_name):
                self._save_row_as_node(label=collection_name, row=row)

    def _load_cross_relationships(self) -> None:
        """Reads all of the data from the single associative table in the data source, translates it, and writes it to Memgraph."""
        for many_to_many_mapping in self._many_to_many_mappings:
            mapping_from = many_to_many_mapping.mapping.foreign_key_from
            mapping_to = many_to_many_mapping.mapping.foreign_key_to

            for row in self._data_loader.load_data(
                collection_name=many_to_many_mapping.table_name, is_cross_table=True
            ):
                self._save_row_as_relationship(
                    collection_name_from=mapping_from.reference_table,
                    collection_name_to=mapping_to.reference_table,
                    property_from=mapping_from.reference_key,
                    property_to=mapping_to.reference_key,
                    relation_label=many_to_many_mapping.mapping.label,
                    row=row,
                )

    def _create_triggers(self) -> None:
        """Creates all of the Triggers in Memgraph.

        Triggers are used as a part of speeding up the translation. Since nodes
        and relationships are written in one go, foreign keys that are represented
        as relationships might not yet be present in memgraph. When they do appear,
        triggers make sure to create the relationship at that point in time, rather
        than having hanging relationship.
        """
        for one_to_many_mapping in self._one_to_many_mappings:
            label1 = self._name_mapper.get_label(collection_name=one_to_many_mapping.table_name)
            for mapping in one_to_many_mapping.mapping:
                property1 = self._name_mapper.get_property_name(
                    collection_name=one_to_many_mapping.table_name, column_name=mapping.foreign_key.column_name
                )
                label2 = self._name_mapper.get_label(collection_name=mapping.foreign_key.reference_table)
                property2 = self._name_mapper.get_property_name(
                    collection_name=one_to_many_mapping.table_name, column_name=mapping.foreign_key.reference_key
                )
                relationship_type = mapping.label
                from_entity = mapping.from_entity

                self._create_trigger(
                    label1=label1,
                    label2=label2,
                    property1=property1,
                    property2=property2,
                    relationship_type=relationship_type,
                    from_entity=from_entity,
                )
                self._create_trigger(
                    label1=label2,
                    label2=label1,
                    property1=property2,
                    property2=property1,
                    relationship_type=relationship_type,
                    from_entity=not from_entity,
                )

    def _create_trigger(
        self, label1: str, label2: str, property1: str, property2: str, relationship_type: str, from_entity: bool
    ) -> None:
        """Creates a translation trigger in Memgraph.

        Args:
            label1: Label of the first node.
            label2: Label of the second node.
            property1: Property of the first node.
            property2: Property of the second node.
            relationship_type: Label for the relationship that the trigger creates.
            from_entity: Indicate whether the relationship goes from or to the first entity.
        """
        trigger_name = "__".join([label1, property1, label2, property2])

        trigger = MemgraphTrigger(
            name=trigger_name,
            event_type=TriggerEventType.CREATE,
            event_object=TriggerEventObject.NODE,
            execution_phase=TriggerExecutionPhase.BEFORE,
            statement=TableToGraphImporter._create_trigger_cypher_query(
                label1, label2, property1, property2, relationship_type, from_entity
            ),
        )

        self._memgraph.create_trigger(trigger)

        print(f"Created trigger {trigger_name}")

    def _create_indexes(self) -> None:
        """Creates indices in Memgraph."""
        for one_to_many_mapping in self._one_to_many_mappings:
            collection_name = self._name_mapper.get_label(collection_name=one_to_many_mapping.table_name)
            for index in one_to_many_mapping.indices:
                new_index = self._name_mapper.get_property_name(
                    collection_name=one_to_many_mapping.table_name, column_name=index
                )
                self._memgraph.create_index(index=MemgraphIndex(collection_name, new_index))
                print(f"Created index for {collection_name} on {new_index}")

    def _save_row_as_node(
        self,
        label: str,
        row: Dict[str, Any],
    ) -> None:
        """Translates a row to a node and writes it to Memgraph.

        Args:
            label: Original label of the new node.
            row: The row that should be saved to Memgraph as a node.
        """
        (
            QueryBuilder(connection=self._memgraph)
            .create()
            .node(
                labels=self._name_mapper.get_label(collection_name=label),
                **{
                    self._name_mapper.get_property_name(collection_name=label, column_name=k): v for k, v in row.items()
                },
            )
            .execute()
        )

    def _save_row_as_relationship(
        self,
        collection_name_from: str,
        collection_name_to: str,
        property_from: str,
        property_to: str,
        relation_label: str,
        row: Dict[str, Any],
    ) -> None:
        """Translates a row to a relationship and writes it to Memgraph.

        Args:
            collection_name_from: Collection name of the source node.
            collection_name_to: Collection name of the destination node.
            property_from: Property of the source node.
            property_to: Property of the destination node.
            relation_label: Label for the relationship.
            row: The row to be translated.
        """
        (
            QueryBuilder(connection=self._memgraph)
            .match()
            .node(
                labels=self._name_mapper.get_label(collection_name=collection_name_from),
                variable=NODE_A,
                **{
                    self._name_mapper.get_property_name(
                        collection_name=collection_name_from, column_name=property_from
                    ): row[property_from]
                },
            )
            .match()
            .node(
                labels=self._name_mapper.get_label(collection_name=collection_name_to),
                variable=NODE_B,
                **{
                    self._name_mapper.get_property_name(
                        collection_name=collection_name_to, column_name=property_to
                    ): row[property_to]
                },
            )
            .create()
            .node(variable=NODE_A)
            .to(relation_label)
            .node(variable=NODE_B)
            .execute()
        )

    def __load_configuration(self, data_configuration: Dict[str, Any]) -> None:
        """Loads all of the configuration.

        Args:
            data_configuration: instructions to translate table to graph.
        """
        self.__load_name_mappings(data_configuration.get(NAME_MAPPINGS_KEY, {}))
        self.__load_one_to_many_mappings_and_indices(
            data_configuration[ONE_TO_MANY_RELATIONS_KEY], data_configuration.get(INDICES_KEY, {})
        )
        self.__load_many_to_many_mappings(data_configuration.get(MANY_TO_MANY_RELATIONS_KEY, {}))

    def __load_name_mappings(self, name_mappings: Dict[str, Any]) -> None:
        """Loads name mappings from the configuration."""
        self._name_mapper = NameMapper(mappings=name_mappings)

    def __load_one_to_many_mappings_and_indices(
        self, one_to_many_configuration: Dict[str, List[str]], indices: Dict[str, List[str]]
    ) -> None:
        """Loads One To Many Mappings and indices from the configuration."""
        self._one_to_many_mappings = [
            TableMapping(
                table_name=table_name,
                mapping=[from_dict(data_class=OneToManyMapping, data=relation) for relation in relations],
                indices=indices.get(table_name, {}),
            )
            for table_name, relations in one_to_many_configuration.items()
        ]

    def __load_many_to_many_mappings(self, many_to_many_configuration: Dict[str, Any]) -> None:
        """Loads Many To Many Mappings from the configuration."""
        self._many_to_many_mappings = [
            TableMapping(table_name=table_name, mapping=from_dict(data_class=ManyToManyMapping, data=relations))
            for table_name, relations in many_to_many_configuration.items()
        ]


class PyArrowImporter(TableToGraphImporter):
    """TableToGraphImporter wrapper for use with PyArrow for reading data."""

    def __init__(
        self,
        file_system_handler: str,
        file_extension_enum: PyArrowFileTypeEnum,
        data_configuration: Dict[str, Any],
        memgraph: Optional[Memgraph] = None,
    ) -> None:
        """
        Args:
            file_system_handler: File system to read from.
            file_extension_enum: File format to be read.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).

        Raises:
            ValueError: PyArrow doesn't support ORC on Windows.
        """
        if file_extension_enum == PyArrowFileTypeEnum.ORC and platform.system() == "Windows":
            raise ValueError("ORC filetype is currently not supported by PyArrow on Windows")

        super().__init__(
            data_loader=PyArrowDataLoader(
                file_extension_enum=file_extension_enum, file_system_handler=file_system_handler
            ),
            data_configuration=data_configuration,
            memgraph=memgraph,
        )


class PyArrowS3Importer(PyArrowImporter):
    """PyArrowImporter wrapper for use with the Amazon S3 File System."""

    def __init__(
        self,
        bucket_name: str,
        file_extension_enum: PyArrowFileTypeEnum,
        data_configuration: Dict[str, Any],
        memgraph: Optional[Memgraph] = None,
        **kwargs,
    ) -> None:
        """
        Args:
            bucket_name: Name of the bucket in S3 to read from.
            file_extension_enum: File format to be read.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).
            **kwargs: Specified for S3FileSystem.
        """
        super().__init__(
            file_system_handler=S3FileSystemHandler(bucket_name=bucket_name, **kwargs),
            file_extension_enum=file_extension_enum,
            data_configuration=data_configuration,
            memgraph=memgraph,
        )


class PyArrowAzureBlobImporter(PyArrowImporter):
    """PyArrowImporter wrapper for use with the Azure Blob File System."""

    def __init__(
        self,
        container_name: str,
        file_extension_enum: PyArrowFileTypeEnum,
        data_configuration: Dict[str, Any],
        memgraph: Optional[Memgraph] = None,
        **kwargs,
    ) -> None:
        """
        Args:
            container_name: Name of the container in Azure Blob to read from.
            file_extension_enum: File format to be read.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).
            **kwargs: Specified for AzureBlobFileSystem.
        """
        super().__init__(
            file_system_handler=AzureBlobFileSystemHandler(container_name=container_name, **kwargs),
            file_extension_enum=file_extension_enum,
            data_configuration=data_configuration,
            memgraph=memgraph,
        )


class PyArrowLocalFileSystemImporter(PyArrowImporter):
    """PyArrowImporter wrapper for use with the Local File System."""

    def __init__(
        self,
        path: str,
        file_extension_enum: PyArrowFileTypeEnum,
        data_configuration: Dict[str, Any],
        memgraph: Optional[Memgraph] = None,
    ) -> None:
        """
        Args:
            path: Full path to the directory to read from.
            file_extension_enum: File format to be read.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).
        """
        super().__init__(
            file_system_handler=LocalFileSystemHandler(path=path),
            file_extension_enum=file_extension_enum,
            data_configuration=data_configuration,
            memgraph=memgraph,
        )


class ParquetS3FileSystemImporter(PyArrowS3Importer):
    """PyArrowS3Importer wrapper for use with the S3 file system and the parquet file type."""

    def __init__(
        self, bucket_name: str, data_configuration: Dict[str, Any], memgraph: Optional[Memgraph] = None, **kwargs
    ) -> None:
        """
        Args:
            bucket_name: Name of the bucket in S3 to read from.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).
            **kwargs: Specified for S3FileSystem.
        """
        super().__init__(
            bucket_name=bucket_name,
            file_extension_enum=PyArrowFileTypeEnum.Parquet,
            data_configuration=data_configuration,
            memgraph=memgraph,
            **kwargs,
        )


class CSVS3FileSystemImporter(PyArrowS3Importer):
    """PyArrowS3Importer wrapper for use with the S3 file system and the CSV file type."""

    def __init__(
        self, bucket_name: str, data_configuration: Dict[str, Any], memgraph: Optional[Memgraph] = None, **kwargs
    ) -> None:
        """
        Args:
            bucket_name: Name of the bucket in S3 to read from.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).
            **kwargs: Specified for S3FileSystem.
        """
        super().__init__(
            bucket_name=bucket_name,
            file_extension_enum=PyArrowFileTypeEnum.CSV,
            data_configuration=data_configuration,
            memgraph=memgraph,
            **kwargs,
        )


class ORCS3FileSystemImporter(PyArrowS3Importer):
    """PyArrowS3Importer wrapper for use with the S3 file system and the ORC file type."""

    def __init__(
        self, bucket_name: str, data_configuration: Dict[str, Any], memgraph: Optional[Memgraph] = None, **kwargs
    ) -> None:
        """
        Args:
            bucket_name: Name of the bucket in S3 to read from.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).
            **kwargs: Specified for S3FileSystem.
        """
        super().__init__(
            bucket_name=bucket_name,
            file_extension_enum=PyArrowFileTypeEnum.ORC,
            data_configuration=data_configuration,
            memgraph=memgraph,
            **kwargs,
        )


class FeatherS3FileSystemImporter(PyArrowS3Importer):
    """PyArrowS3Importer wrapper for use with the S3 file system and the feather file type."""

    def __init__(
        self, bucket_name: str, data_configuration: Dict[str, Any], memgraph: Optional[Memgraph] = None, **kwargs
    ) -> None:
        """
        Args:
            bucket_name: Name of the bucket in S3 to read from.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).
            **kwargs: Specified for S3FileSystem.
        """
        super().__init__(
            bucket_name=bucket_name,
            file_extension_enum=PyArrowFileTypeEnum.Feather,
            data_configuration=data_configuration,
            memgraph=memgraph,
            **kwargs,
        )


class ParquetAzureBlobFileSystemImporter(PyArrowAzureBlobImporter):
    """PyArrowAzureBlobImporter wrapper for use with the Azure Blob file system and the parquet file type."""

    def __init__(
        self, container_name: str, data_configuration: Dict[str, Any], memgraph: Optional[Memgraph] = None, **kwargs
    ) -> None:
        """
        Args:
            container_name: Name of the container in Azure Blob storage to read from.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).
            **kwargs: Specified for AzureBlobFileSystem.
        """
        super().__init__(
            container_name=container_name,
            file_extension_enum=PyArrowFileTypeEnum.Parquet,
            data_configuration=data_configuration,
            memgraph=memgraph,
            **kwargs,
        )


class CSVAzureBlobFileSystemImporter(PyArrowAzureBlobImporter):
    """PyArrowAzureBlobImporter wrapper for use with the Azure Blob file system and the CSV file type."""

    def __init__(
        self, container_name: str, data_configuration: Dict[str, Any], memgraph: Optional[Memgraph] = None, **kwargs
    ) -> None:
        """
        Args:
            container_name: Name of the container in Azure Blob storage to read from.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).
            **kwargs: Specified for AzureBlobFileSystem.
        """
        super().__init__(
            container_name=container_name,
            file_extension_enum=PyArrowFileTypeEnum.CSV,
            data_configuration=data_configuration,
            memgraph=memgraph,
            **kwargs,
        )


class ORCAzureBlobFileSystemImporter(PyArrowAzureBlobImporter):
    """PyArrowAzureBlobImporter wrapper for use with the Azure Blob file system and the CSV file type."""

    def __init__(
        self, container_name, data_configuration: Dict[str, Any], memgraph: Optional[Memgraph] = None, **kwargs
    ) -> None:
        """
        Args:
            container_name: Name of the container in Blob storage to read from.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).
            **kwargs: Specified for AzureBlobFileSystem.
        """
        super().__init__(
            container_name=container_name,
            file_extension_enum=PyArrowFileTypeEnum.ORC,
            data_configuration=data_configuration,
            memgraph=memgraph,
            **kwargs,
        )


class FeatherAzureBlobFileSystemImporter(PyArrowAzureBlobImporter):
    """PyArrowAzureBlobImporter wrapper for use with the Azure Blob file system and the Feather file type."""

    def __init__(
        self, container_name, data_configuration: Dict[str, Any], memgraph: Optional[Memgraph] = None, **kwargs
    ) -> None:
        """
        Args:
            container_name: Name of the container in Blob storage to read from.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).
            **kwargs: Specified for AzureBlobFileSystem.
        """
        super().__init__(
            container_name=container_name,
            file_extension_enum=PyArrowFileTypeEnum.Feather,
            data_configuration=data_configuration,
            memgraph=memgraph,
            **kwargs,
        )


class ParquetLocalFileSystemImporter(PyArrowLocalFileSystemImporter):
    """PyArrowLocalFileSystemImporter wrapper for use with the local file system and the parquet file type."""

    def __init__(self, path: str, data_configuration: Dict[str, Any], memgraph: Optional[Memgraph] = None) -> None:
        """
        Args:
            path: Full path to directory.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).
            **kwargs: Specified for LocalFileSystem.
        """
        super().__init__(
            path=path,
            file_extension_enum=PyArrowFileTypeEnum.Parquet,
            data_configuration=data_configuration,
            memgraph=memgraph,
        )


class CSVLocalFileSystemImporter(PyArrowLocalFileSystemImporter):
    """PyArrowLocalFileSystemImporter wrapper for use with the local file system and the CSV file type."""

    def __init__(self, path: str, data_configuration: Dict[str, Any], memgraph: Optional[Memgraph] = None) -> None:
        """
        Args:
            path: Full path to directory.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).
            **kwargs: Specified for LocalFileSystem.
        """
        super().__init__(
            path=path,
            file_extension_enum=PyArrowFileTypeEnum.CSV,
            data_configuration=data_configuration,
            memgraph=memgraph,
        )


class ORCLocalFileSystemImporter(PyArrowLocalFileSystemImporter):
    """PyArrowLocalFileSystemImporter wrapper for use with the local file system and the ORC file type."""

    def __init__(self, path: str, data_configuration: Dict[str, Any], memgraph: Optional[Memgraph] = None) -> None:
        """
        Args:
            path: Full path to directory.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).
            **kwargs: Specified for LocalFileSystem.
        """
        super().__init__(
            path=path,
            file_extension_enum=PyArrowFileTypeEnum.ORC,
            data_configuration=data_configuration,
            memgraph=memgraph,
        )


class FeatherLocalFileSystemImporter(PyArrowLocalFileSystemImporter):
    """PyArrowLocalFileSystemImporter wrapper for use with the local file system and the Feather/IPC/Arrow file type."""

    def __init__(self, path: str, data_configuration: Dict[str, Any], memgraph: Optional[Memgraph] = None) -> None:
        """
        Args:
            path: Full path to directory.
            data_configuration: Configuration for the translations.
            memgraph: Connection to Memgraph (Optional).
            **kwargs: Specified for LocalFileSystem.
        """
        super().__init__(
            path=path,
            file_extension_enum=PyArrowFileTypeEnum.Feather,
            data_configuration=data_configuration,
            memgraph=memgraph,
        )
