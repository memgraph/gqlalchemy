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



@dataclass(frozen=True)
class RelationshipMapping:
    foreign_key: str
    reference_table: str
    reference_key: str
    label: str
    variables: Optional[Dict[str, str]] = None



@dataclass(frozen=True)
class Nx1Mapping:
    mapping: RelationshipMapping
    from_entity: bool = False



@dataclass(frozen=True)
class MxNMapping:
    mapping1: RelationshipMapping
    mapping2: RelationshipMapping
    label: str
    from_first: bool = True



Mapping = Union[List[Nx1Mapping], MxNMapping]



@dataclass
class CollectionMapping:
    collection_name: str
    mapping: Mapping = None
    indices: Optional[List[str]] = None



class DataSource(ABC):
    def __init__(self, file_extension: str) -> None:
        self._file_extension: str = file_extension

    
    @abstractmethod
    def load_data(
        self,
        collection_name: str,
        is_cross_table: bool=False
    ) -> None:
        pass



class S3DataSource(DataSource):
    def __init__(
        self, 
        bucket_name: str,
        s3_access_key: str,
        s3_secret_key: str,
        s3_region: str,
        file_extension: str,
        s3_session_token: Optional[str] = None,
    ) -> None:
        super().__init__(file_extension=file_extension)
        self._bucket_name: str = bucket_name
        self._s3_access_key: str = s3_access_key
        self._s3_secret_key: str = s3_secret_key
        self._s3_region: str = s3_region
        self._s3_session_token: Optional[str] = s3_session_token

    
    def load_data(
        self,
        collection_name: str,
        is_cross_table: bool=False,
        columns: Optional[List[str]] = None,
    ) -> None:
        s3 = fs.S3FileSystem(
            region=self._s3_region,
            access_key=self._s3_access_key,
            secret_key=self._s3_secret_key,
            session_token=self._s3_session_token,
        )
        source = f"{self._bucket_name}/{collection_name}.{self._file_extension}"
        print("Loading " + ("cross table " if is_cross_table else "") + f"data from {source}")

        # Load dataset via Pyarrow
        dataset = ds.dataset(source, filesystem=s3)

        # Load batches from raw data
        for batch in dataset.to_batches(
            columns=columns,
        ):
            for batch in batch.to_pylist():
                yield batch


@dataclass(frozen=True)
class Configuration:
    label: Optional[str] = None
    column_names_mapping: Optional[Dict[str, str]] = None


class Translator:
    _DIRECTION = {
        True: ("a", "b"),
        False: ("b", "a"),
    }

    def __init__(
        self,
        data_source: DataSource,
        data_configuration: Dict[str, Any], 
        memgraph: Optional[Memgraph] = None
    ) -> None:
        self._memgraph: Memgraph = memgraph if memgraph is not None else Memgraph()
        self._data_source = data_source
        self._collection_mappings: List[CollectionMapping] = []
        self._cross_relationship_mappings: List[CollectionMapping] = []

        self._load_name_mappings(data_configuration["name_mappings"])
        self._load_nx1_relations_and_indices(data_configuration["nx1_relations"], data_configuration["indices"])
        self._load_mxn_relations(data_configuration["mxn_relations"])


    def translate(self, drop_database_on_start: bool):
        if drop_database_on_start:
            self._memgraph.drop_database()
            self._drop_indices() # to gqla
            self._drop_triggers() # to gqla

        self._create_indices()
        self._create_triggers() # to gqla

        self._load_nodes()
        self._load_cross_relationships()


    def _load_nodes(self) -> None:
        for collection_mapping in self._collection_mappings:
            collection_name = collection_mapping.collection_name
            for row in self._data_source.load_data(collection_name=collection_name):
                self._save_row_as_node(
                    label=collection_name, 
                    row=row
                )


    def _load_cross_relationships(self) -> None:
        for cross_relationship_mapping in self._cross_relationship_mappings:
            collection_name = cross_relationship_mapping.collection_name
            
            mapping1 = cross_relationship_mapping.mapping.mapping1
            mapping2 = cross_relationship_mapping.mapping.mapping2

            table_name1 = mapping1.reference_table
            table_name2 = mapping2.reference_table

            node1 = self._get_node_name(table_name1)
            node2 = self._get_node_name(table_name2)

            property1 = mapping1.reference_key
            property2 = mapping2.reference_key

            new_property1 = self._get_property_name(table_name1, property1)
            new_property2 = self._get_property_name(table_name2, property2)

            for row in self._data_source.load_data(collection_name=collection_name, is_cross_table=True):
                self._save_row_as_relationship(
                    relations=[node1, node2],
                    on_properties=[(property1, new_property1), (property2, new_property2)],
                    relation_label=cross_relationship_mapping.mapping.label,
                    row=row
                )


    def _create_triggers(self) -> None:
        for collection_mapping in self._collection_mappings:
            label1 = self._get_node_name(collection_mapping.collection_name)
            for nx1_mapping in collection_mapping.mapping:
                property1 = self._get_property_name(collection_mapping.collection_name, nx1_mapping.mapping.foreign_key)
                label2 = self._get_node_name(nx1_mapping.mapping.reference_table)
                property2 = self._get_property_name(collection_mapping.collection_name, nx1_mapping.mapping.reference_key)
                edge_type = nx1_mapping.mapping.label
                from_entity = nx1_mapping.from_entity

                self._create_trigger(label1, label2, property1, property2, edge_type, from_entity)
                self._create_trigger(label2, label1, property2, property1, edge_type, not from_entity)


    def _drop_triggers(self) -> None:
        for trigger in self._memgraph.get_triggers():
            self._memgraph.drop_trigger(MemgraphTrigger(trigger["trigger name"], None, None, None, None))


    def _create_trigger(self, label1: str, label2: str, property1: str, property2: str, edge_type: str, from_entity: bool) -> None:
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
        for collection_mapping in self._collection_mappings:
            collection_name = self._get_node_name(collection_mapping.collection_name)
            for index in collection_mapping.indices:
                new_index = self._get_property_name(collection_mapping.collection_name, index)
                self._memgraph.create_index(MemgraphIndex(collection_name, new_index))
                print(f"Created index for {collection_name} on {new_index}")


    def _drop_indices(self) -> None:
        for index in self._memgraph.get_indexes():
            self._memgraph.drop_index(index)


    def _create_trigger_cypher_query(self, label1: str, label2: str, property1: str, property2: str, edge_type: str, from_entity: bool) -> str:
        from_node, to_node = Translator._DIRECTION[from_entity]
        return Unwind(list_expression="createdVertices", variable="a") \
                .with_(results={"a":""}) \
                .where(property1=f"a:{label2}", operator="MATCH", property2=f"(b:{label1})") \
                .where(property1=f"b.{property1}", operator="=", property2=f"a.{property2}") \
                .create() \
                .node(variable=from_node) \
                .to(edge_label=edge_type) \
                .node(variable=to_node) \
                .construct_query()
            

    def _save_row_as_node(self, label: str, row: Dict[str, Any]):
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
        from_first: bool = True
    ):
        if len(relations) != len(on_properties):
            raise RuntimeError("Relations and properties should be a same-sized list.")

        from_node, to_node = Translator._DIRECTION[from_first]
        label1, label2 = relations[0], relations[1]
        property1, new_property1 = on_properties[0]
        property2, new_property2 = on_properties[1]
        
        query_builder = QueryBuilder(connection=self._memgraph)
        list(
            query_builder.match()
            .node(labels=label1, variable=from_node, **{new_property1: row[property1]})
            .match()
            .node(labels=label2, variable=to_node, **{new_property2: row[property2]})
            .create()
            .node(variable=from_node)
            .to(relation_label)
            .node(variable=to_node)
            .return_({"1": "1"})
            .execute()
        )


    def _get_node_name(self, original_name: str) -> str:
        configuration = self._configurations.get(original_name, None)

        if configuration is None:
            return original_name

        return configuration.label if configuration.label is not None else original_name


    def _get_property_name(self, collection_name: str, original_column_name: str):
        configuration = self._configurations.get(collection_name, None)

        if configuration is None or configuration.column_names_mapping is None:
            return original_column_name

        new_col_name = configuration.column_names_mapping.get(original_column_name, None)

        return new_col_name if new_col_name is not None else original_column_name


    def _load_name_mappings(self, name_mappings: Dict[str, Any]):
        self._configurations = {k: Configuration(**v) for k, v in name_mappings.items()}


    def _load_nx1_relations_and_indices(self, nx1_relations: Dict[str, List[str]], indices: Dict[str, List[str]]) -> None:
        self._collection_mappings = [
            CollectionMapping(
                collection_name=table_name, 
                mapping=[Nx1Mapping(mapping=RelationshipMapping(**relation)) for relation in relations], 
                indices=indices[table_name]
            ) for table_name, relations in nx1_relations.items()]


    def _load_mxn_relations(self, mxn_relations: Dict):
        self._cross_relationship_mappings = [
            CollectionMapping(
            collection_name=table_name, 
                mapping=MxNMapping(
                    mapping1=RelationshipMapping(**relations["mapping1"]),
                    mapping2=RelationshipMapping(**relations["mapping2"]),
                    label=relations["label"]
                )
            )
            for table_name, relations in mxn_relations.items()]



class S3Translator(Translator):
    def __init__(
        self, 
        bucket_name: str,
        s3_access_key: str,
        s3_secret_key: str,
        s3_region: str,
        data_configuration: Dict[str, Any],
        file_extension: str, 
        s3_session_token: Optional[str] = None,
        memgraph: Optional[Memgraph] = None
    ) -> None:
        super().__init__(
            data_source=S3DataSource(
                bucket_name=bucket_name,
                s3_access_key=s3_access_key,
                s3_secret_key=s3_secret_key,
                s3_region=s3_region,
                s3_session_token=s3_session_token,
                file_extension=file_extension
            ),
            data_configuration=data_configuration,
            memgraph=memgraph
        )
