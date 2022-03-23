# Copyright (c) 2016-2022 Memgraph Ltd. [https://memgraph.com]
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

from . import Memgraph
from .query_builder import QueryBuilder, Unwind
from abc import ABC, abstractmethod
from dataclasses import dataclass
from dacite import from_dict
from gqlalchemy.models import (
    MemgraphIndex, 
    MemgraphTrigger, 
    TriggerEventObject, 
    TriggerEventType, 
    TriggerExecutionPhase
)
from pyarrow import fs
from typing import (
    List, 
    Dict, 
    Any, 
    Optional,
    Tuple, 
    Union
)
import pyarrow.dataset as ds
import adlfs

from enum import Enum

NAME_MAPPINGS_KEY = "name_mappings"
ONE_TO_MANY_RELATIONS_KEY = "one_to_many_relations"
INDICES_KEY = "indices"
MANY_TO_MANY_RELATIONS_KEY = "many_to_many_relations"

FROM_NODE_VARIABLE_NAME = "from_node"
TO_NODE_VARIABLE_NAME = "to_node"

NODE_A = "a"
NODE_B = "b"


@dataclass(frozen=True)
class ForeignKeyMapping:
    """
    Class that contains the full description of a single foreign key in a table.

    :param column_name: Column name that holds the foreign key
    :type column_name: str
    :param reference_table: Name of a table from which the foreign key is taken
    :type reference_table: str
    :param reference_key: Column name in referenced table from which the foreign key is taken
    :type reference_key: str
    """
    column_name: str
    reference_table: str
    reference_key: str


@dataclass(frozen=True)
class OneToManyMapping:
    """
    Class that holds the full description of a single one to many mapping in a table.

    :param foreign_key: Foreign key used for mapping
    :type foreing_key: ForeignKeyMapping
    :param label: Label which will be applied to the relationship created from this object
    :type label: str
    :param from_entity: Direction of the relationship created from mapping object
    :type from_entity: bool
    :param variables: Variables that will be added to the relationship created from this object (Optional)
    :type variables: Dict[str, str]
    """

    foreign_key: ForeignKeyMapping
    label: str
    from_entity: bool = False
    variables: Optional[Dict[str, str]] = None


@dataclass(frozen=True)
class ManyToManyMapping:
    """
    Class that holds the full description of a single many to many mapping in a table.
    Many to many mapping is intended to be used in case of associative tables

    :param foreign_key_from: Describes the source of the relationship
    :type foreign_key_from: ForeignKeyMapping
    :param foreign_key_to: Describes the destination of the relationship
    :type foreign_key_to: ForeignKeyMapping
    :param label: Label to be applied to the newly created relationship
    :type label: str
    :param variables: Variables that will be added to the relationship created from this object (Optional)
    :type variables: Dict[str, str]
    """
    foreign_key_from: ForeignKeyMapping
    foreign_key_to: ForeignKeyMapping
    label: str
    variables: Optional[Dict[str, str]] = None


Mapping = Union[List[OneToManyMapping], ManyToManyMapping]


@dataclass
class TableMapping:
    """
    Class that holds the full description of all of the mappings for a single table.

    :param table_name: Name of the table
    :type table_name: str
    :param mapping: All of the mappings in the table (Optional)
    :type mapping: Mapping
    :param indices: List of the indices to be created for this table (Optional)
    :type indices: List[str]
    """
    table_name: str
    mapping: Optional[Mapping] = None
    indices: Optional[List[str]] = None


@dataclass(frozen=True)
class NameMappings:
    """
    Class that contains new label name and all of the column name mappings for a single table

    :param label: New label (Optional)
    :type label: str
    :param column_names_mapping: Dictionary containing key-value pairs in form ("column name", "property name") (Optional)
    :type column_names_mapping: Dict[str, str]
    """
    label: Optional[str] = None
    column_names_mapping: Optional[Dict[str, str]] = None


class FileSystemHandler(ABC):
    """
    Abstract class for defining FileSystemHandler. Inherit this class and initialize
    connection to custom data source.
    """
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def get_path(self):
        """
        returns complete path in specific file system. Used to read the file system
        for a specific file.
        
        :return: str
        """
        pass


class S3FileSystemHandler(FileSystemHandler):
    """
    Handler connection to Amazon S3 service via pyarrow
    """
    def __init__(self, **kwargs):
        """
        kwargs>
        :param bucket_name: Name of the bucket on S3 from which to read the data
        :type bucket_name: str
        :param s3_access_key: S3 access key
        :type s3_access_key: str
        :param s3_secret_key: S3 secret key
        :type s3_secret_key: str
        :param s3_region: S3 region
        :type s3_region: str
        :param s3_session_token: S3 session token (Optional)
        :type s3_session_token: str
        """
        self.fs = fs.S3FileSystem(
            region=kwargs.get('s3_region'),
            access_key=kwargs.get('s3_access_key'),
            secret_key=kwargs.get('s3_secret_key'),
            session_token=kwargs.get('s3_session_token', None),
        )
        self._bucket_name = kwargs.get('bucket_name')

    def get_path(
        self,
        collection_name: str,
        file_extension: str
        ) -> str:
        """
        Get file path in file system

        :param collection_name: Name of file to read
        :type collection_name: str
        :param file_extension: File type
        :type file_extension: str

        :returns: string
        """
        return f"{self._bucket_name}/{collection_name}.{file_extension}"


class AzureBlobFileSystemHandler(FileSystemHandler):
    """
    Handles connection to Azure Blob service via adlfs package
    """
    def __init__(self, **kwargs) -> None:
        """
        kwargs>
        :param blob_account_name: Account name from Azure Blob
        :type blob_account_name: str
        :param blob_account_key: Account key for Azure Blob (Optional - if using sas_token)
        :type blob_account_key: str
        :param blob_sas_token: Shared access signature token for authentification (Optional)
        :type blob_sas_token: str
        :param container_name: Name of Blob container storing data
        :type container_name: str
        """
        self.fs = adlfs.AzureBlobFileSystem(
            account_name=kwargs.get('blob_account_name'),
            account_key=kwargs.get('blob_account_key', None),
            sas_token=kwargs.get('blob_sas_token', None)
        )
        self._container_name = kwargs['container_name']

    def get_path(
        self,
        collection_name: str,
        file_extension: str
    ) -> str:
        """
        Get file path in file system

        :param collection_name: Name of file to read
        :type collection_name: str
        :param file_extension: File type
        :type file_extension: str

        :returns: str
        """
        return f"{self._container_name}/{collection_name}.{file_extension}"


class DataLoader(ABC):
    """
    Implements loading of data type from file system service to TableToGraphImporter
    """
    def __init__(
        self,
        file_system_handler: FileSystemHandler
    ) -> None:
        """
        :param file_system_handler: object for handling of file system service
        :type file_system_handler: FileSystemHandler
        """
        super().__init__()
        self._file_system_handler = file_system_handler

    @abstractmethod
    def load_data(
        self,
        collection_name: str,
        is_cross_table: bool=False
    ) -> None:
        """
        Override this method in the derived class. Intended to be used for reading data from data format.

        :param collection_name: name of file to read
        :type collection_name: str
        :param is_cross_table: Indicate whether or not the collection contains associative table (default=False)
        :type is_cross_table: bool
        """
        pass


class PyarrowDataLoader(DataLoader):
    """
    Loads data using Pyarrow.
    Pyarrow currently supports "parquet", "ipc"/"arrow"/"feather", "csv",
    and "orc", see pyarrow.dataset.dataset for up-to-date info.
    ds.dataset in load_data accepts any fsspec subclass, making this DataLoader
    compatible with fsspec-compatible filesystems.
    """
    def __init__(
        self,
        file_extension: str,
        file_system_handler: FileSystemHandler,
    ) -> None:
        """
        :param file_extension: File format to be read
        :type file_extension: str
        :param file_system_handler: Object for handling of file system service
        :type file_system_handler: FileSystemHandler
        """
        super().__init__(file_system_handler=file_system_handler)
        self._file_extension = file_extension

    def load_data(
        self,
        collection_name: str,
        is_cross_table: bool = False,
        columns: Optional[List[str]] = None
    ) -> None:
        """
        Generator for loading data from data format.

        :param collection_name: Name of file to read
        :type collection_name: str
        :param is_cross_table: Flag signifying whether it is a cross table
        :type is_cross_table: bool
        :param columns: Table columns to read
        :type columns: List[str]
        """
        source = self._file_system_handler.get_path(collection_name, self._file_extension)
        print("Loading " + ("cross table " if is_cross_table else "") + f"data from {source}")

        # Load dataset via Pyarrow
        dataset = ds.dataset(
            source=source,
            filesystem=self._file_system_handler.fs
        )

        # Load batches from raw data
        for batch in dataset.to_batches(
            columns=columns,
        ):
            for batch in batch.to_pylist():
                yield batch


class FileSystemTypeEnum(Enum):
    AmazonS3 = "AmazonS3"
    AzureBlob = "AzureBlob"


def get_data_loader(
    file_extension: str,
    filesystem_type: FileSystemTypeEnum,
    **kwargs
    ) -> DataLoader:
    """
    Returns DataLoader object, which uses instance of FileSystemHandler, in order to load data
    of specific type from specific File System.

    :param file_extension: File type to read
    :type file_extension: str
    :param filesystem_type: Type of filesystem we want to use
    :type filesystem_type: FileSystemTypeEnum
    :param **kwargs: For filesystem use

    :returns: DataLoader 
    """
    if (file_extension == "parquet" or
        file_extension == "csv" or
        file_extension == "orc" or
        file_extension == "ipc" or
        file_extension == "feather" or
        file_extension == "arrow"):
        return PyarrowDataLoader(
            file_extension=file_extension,
            file_system_handler=get_filesystem(filesystem_type, **kwargs)
        )
    else:
        raise ValueError(f"{file_extension} is currently not supported")


def get_filesystem(filesystem_type: FileSystemTypeEnum, **kwargs) -> FileSystemHandler:
    """
    Returns specific FileSystemHandler.

    :param filesystem_type: Type of filesystem we want to use
    :type filesystem_type: FileSystemTypeEnum

    :returns: FileSystemHandler
    """
    if filesystem_type == FileSystemTypeEnum.AmazonS3:
        return S3FileSystemHandler(**kwargs)
    elif filesystem_type == FileSystemTypeEnum.AzureBlob:
        return AzureBlobFileSystemHandler(**kwargs)


class TableToGraphImporter:
    """
    Class that implements translation of table data to graph data, and imports it to Memgraph
    """
    _DIRECTION = {
        True: (NODE_A, NODE_B),
        False: (NODE_B, NODE_A),
    }

    def __init__(
        self,
        file_extension: str,
        filesystem_type: FileSystemTypeEnum,
        data_configuration: Dict[str, Any],
        memgraph: Optional[Memgraph] = None,
        **kwargs
    ) -> None:
        """
        :param file_extension: file format to be read
        :type file_extension: string
        :param file_system: type of file system storage to use
        :type file_system: string
        :param data_configuration: Configuration for the translations
        :type data_configuration: Dict[str, Any]
        :param memgraph: Connection to Memgraph (Optional)
        :type memgraph: Memgraph
        """
        self._data_loader: DataLoader = get_data_loader(file_extension, filesystem_type, **kwargs)
        self._memgraph: Memgraph = memgraph if memgraph is not None else Memgraph()

        self.__load_configuration(data_configuration=data_configuration)

    def translate(self, drop_database_on_start: bool) -> None:
        """
        Performs the translations
        
        :param drop_database_on_start: Indicate whether or not the database should be dropped prior to the start of the translations
        :type drop_database_on_start: bool
        """
        if drop_database_on_start:
            self._memgraph.drop_database()
            self._drop_indices() # to gqla
            self._drop_triggers() # to gqla

        self._create_indices()
        self._create_triggers() # to gqla

        self._load_nodes()
        self._load_cross_relationships()

    def _load_nodes(self) -> None:
        """
        Reads all of the data from the single table in the data source, translates it, and writes it to memgraph.
        """
        for one_to_many_mapping in self._one_to_many_mappings:
            collection_name = one_to_many_mapping.table_name
            for row in self._data_loader.load_data(collection_name=collection_name):
                self._save_row_as_node(
                    label=collection_name, 
                    row=row
                )

    def _load_cross_relationships(self) -> None:
        """
        Reads all of the data from the single associative table in the data source, translates it, and writes it to memgraph.
        """
        for many_to_many_mapping in self._many_to_many_mappings:
            collection_name = many_to_many_mapping.table_name
            mapping_from = many_to_many_mapping.mapping.foreign_key_from
            mapping_to = many_to_many_mapping.mapping.foreign_key_to

            table_name_from, property_from = mapping_from.reference_table, mapping_from.reference_key
            table_name_to, property_to = mapping_to.reference_table, mapping_to.reference_key

            node_from = self._get_node_name(original_name=table_name_from)
            node_to = self._get_node_name(original_name=table_name_to)

            new_property_from = self._get_property_name(collection_name=table_name_from, original_column_name=property_from)
            new_property_to = self._get_property_name(collection_name=table_name_to, original_column_name=property_to)

            for row in self._data_loader.load_data(collection_name=collection_name, is_cross_table=True):
                self._save_row_as_relationship(
                    relations=[node_from, node_to],
                    on_properties=[(property_from, new_property_from), (property_to, new_property_to)],
                    relation_label=many_to_many_mapping.mapping.label,
                    row=row
                )

    def _create_triggers(self) -> None:
        """
        Creates all of the Triggers in the Memgraph. Triggers are used as a part of speeding up the translation.
        Since nodes and relationships are written in one go, foreign keys that are represented as relationships
        might not yet be present in memgraph. When they do appear, triggers make sure to write relationship at that point in time,
        rather than having hanging relationship.
        """
        for one_to_many_mapping in self._one_to_many_mappings:
            label1 = self._get_node_name(original_name=one_to_many_mapping.table_name)
            for mapping in one_to_many_mapping.mapping:
                property1 = self._get_property_name(
                    collection_name=one_to_many_mapping.table_name, 
                    original_column_name=mapping.foreign_key.column_name
                )
                label2 = self._get_node_name(
                    original_name=mapping.foreign_key.reference_table
                )
                property2 = self._get_property_name(
                    collection_name=one_to_many_mapping.table_name, 
                    original_column_name=mapping.foreign_key.reference_key
                )
                edge_type = mapping.label
                from_entity = mapping.from_entity

                self._create_trigger(
                    label1=label1, 
                    label2=label2, 
                    property1=property1, 
                    property2=property2, 
                    edge_type=edge_type, 
                    from_entity=from_entity
                )
                self._create_trigger(
                    label1=label2, 
                    label2=label1, 
                    property1=property2, 
                    property2=property1, 
                    edge_type=edge_type, 
                    from_entity=not from_entity
                )

    def _drop_triggers(self) -> None:
        """
        Drops all of the triggers from Memgraph
        """
        for trigger in self._memgraph.get_triggers():
            self._memgraph.drop_trigger(MemgraphTrigger(trigger["trigger name"], None, None, None, None))

    def _create_trigger(
        self, 
        label1: str, 
        label2: str, 
        property1: str, 
        property2: str, 
        edge_type: str, 
        from_entity: bool
    ) -> None:
        """
        Creates translation trigger in Memgraph. 

        :param label1: Label of the first Node
        :type label1: str
        :param label2: Label of the second Node
        :type label2: str
        :param property1: Property of the first Node
        :type property1: str
        :param property2: Property of the second Node
        :type property2: str
        :param edge_type: Label for the relationship that the trigger creates
        :type edge_type: str
        :param from_entity: Indicate whether relationship goes from or to first entity
        :type from_entity: bool
        """
        trigger_name = "__".join([label1, property1, label2, property2])

        trigger = MemgraphTrigger(
            name=trigger_name,
            event_type=TriggerEventType.CREATE,
            event_object=TriggerEventObject.NODE,
            execution_phase=TriggerExecutionPhase.BEFORE,
            statement=self._create_trigger_cypher_query(label1, label2, property1, property2, edge_type, from_entity)
        )
        print(f"Created trigger {trigger_name}")

        self._memgraph.create_trigger(trigger)

    def _create_indices(self) -> None:
        """
        Creates indices in Memgraph
        """
        for one_to_many_mapping in self._one_to_many_mappings:
            collection_name = self._get_node_name(original_name=one_to_many_mapping.table_name)
            for index in one_to_many_mapping.indices:
                new_index = self._get_property_name(
                    collection_name=one_to_many_mapping.table_name, 
                    original_column_name=index
                )
                self._memgraph.create_index(index=MemgraphIndex(collection_name, new_index))
                print(f"Created index for {collection_name} on {new_index}")

    def _drop_indices(self) -> None:
        """
        Drops all indices from Memgraph
        """
        for index in self._memgraph.get_indexes():
            self._memgraph.drop_index(index)

    def _create_trigger_cypher_query(
        self, 
        label1: str, 
        label2: str, 
        property1: str, 
        property2: str, 
        edge_type: str, 
        from_entity: bool
    ) -> str:
        """
        Creates Cypher Query for translation Trigger

        @TODO: Investigate creating Template string instead of this method
        """
        from_node, to_node = TableToGraphImporter._DIRECTION[from_entity]
        return Unwind(list_expression="createdVertices", variable=NODE_A) \
                .with_(results={NODE_A:""}) \
                .where(property1=f"{NODE_A}:{label2}", operator="MATCH", property2=f"({NODE_B}:{label1})") \
                .where(property1=f"{NODE_B}.{property1}", operator="=", property2=f"{NODE_A}.{property2}") \
                .create() \
                .node(variable=from_node) \
                .to(edge_label=edge_type) \
                .node(variable=to_node) \
                .construct_query()
            
    def _save_row_as_node(
        self, 
        label: str, 
        row: Dict[str, Any],
    ) -> None:
        """
        Translates row to Node and writes it to Memgraph

        :param label: Original label of the new node
        :type label: str
        :param row: Row that should be saved to Memgraph as Node
        :type row: Dict[str, Any]
        """
        list(
            QueryBuilder(connection=self._memgraph).
            create().
            node(labels=self._get_node_name(label), 
                 **{self._get_property_name(label, k): v for k, v in row.items()})
            .execute())

    def _save_row_as_relationship(
        self, 
        relations: List[str], 
        on_properties: List[Tuple[str, str]], 
        relation_label: str, 
        row: Dict[str, Any],
    ) -> None:
        """
        Translates row to Relationship and writes it to Memgraph

        @TODO: Rewrite this method
        """
        if len(relations) != len(on_properties):
            raise RuntimeError("Relations and properties should be a same-sized list.")

        label_from, label_to = relations[0], relations[1]
        property_from, new_property_from = on_properties[0]
        property_to, new_property_to = on_properties[1]
        
        query_builder = QueryBuilder(connection=self._memgraph)
        list(
            query_builder.match()
            .node(labels=label_from, variable=NODE_A, **{new_property_from: row[property_from]})
            .match()
            .node(labels=label_to, variable=NODE_B, **{new_property_to: row[property_to]})
            .create()
            .node(variable=NODE_A)
            .to(relation_label)
            .node(variable=NODE_B)
            .return_({"1": "1"})
            .execute()
        )

    def _get_node_name(self, original_name: str) -> str:
        """
        Gets node name from original table name

        :param original_name: Original table name
        :type original_name: str
        :returns: str
        """
        configuration = self._configurations.get(original_name, None)

        if configuration is None:
            return original_name

        return configuration.label if configuration.label is not None else original_name

    def _get_property_name(self, collection_name: str, original_column_name: str) -> str:
        """
        Gets property name from original column name

        :param collection_name: Original table name
        :type collection_name: str
        :param original_column_name: Original column name
        :type original_column_name: str
        :returns: str
        """
        configuration = self._configurations.get(collection_name, None)

        if configuration is None or configuration.column_names_mapping is None:
            return original_column_name

        new_col_name = configuration.column_names_mapping.get(original_column_name, None)

        return new_col_name if new_col_name is not None else original_column_name

    def __load_configuration(self, data_configuration: Dict[str, Any]) -> None:
        """
        Loads all of the configuration
        """
        self.__load_name_mappings(data_configuration.get(NAME_MAPPINGS_KEY, {}))
        self.__load_one_to_many_mappings_and_indices(data_configuration[ONE_TO_MANY_RELATIONS_KEY], data_configuration.get(INDICES_KEY, {}))
        self.__load_many_to_many_mappings(data_configuration.get(MANY_TO_MANY_RELATIONS_KEY, {}))

    def __load_name_mappings(self, name_mappings: Dict[str, Any]) -> None:
        """
        Loads name mappings from the configuration
        """
        self._configurations = {k: NameMappings(**v) for k, v in name_mappings.items()}

    def __load_one_to_many_mappings_and_indices(
        self, 
        one_to_many_configuration: Dict[str, List[str]], 
        indices: Dict[str, List[str]]
    ) -> None:
        """
        Loads One To Many Mappings and indices from the configuration. 
        """
        self._one_to_many_mappings = [
            TableMapping(
                table_name=table_name, 
                mapping=[from_dict(data_class=OneToManyMapping, data=relation) for relation in relations], 
                indices=indices.get(table_name, {})
            ) for table_name, relations in one_to_many_configuration.items()]

    def __load_many_to_many_mappings(self, many_to_many_configuration: Dict[str, Any]) -> None:
        """
        Loads Many To Many Mappings from the configuration
        """
        self._many_to_many_mappings = [
            TableMapping(
                table_name=table_name, 
                mapping=from_dict(data_class=ManyToManyMapping, data=relations)
            )
            for table_name, relations in many_to_many_configuration.items()]
