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

import os
import sqlite3
from typing import List, Optional, Union

from gqlalchemy.connection import Connection, MemgraphConnection
from gqlalchemy.disk_storage import OnDiskPropertyDatabase
from gqlalchemy.exceptions import (
    GQLAlchemyError,
    GQLAlchemyFileNotFoundError,
    GQLAlchemyOnDiskPropertyDatabaseNotDefinedError,
    GQLAlchemyUniquenessConstraintError,
)
from gqlalchemy.models import (
    MemgraphConstraintExists,
    MemgraphConstraintUnique,
    MemgraphIndex,
    MemgraphStream,
    MemgraphTrigger,
    Node,
    Relationship,
)
from gqlalchemy.vendors.database_client import DatabaseClient
from gqlalchemy.graph_algorithms.query_modules import QueryModule
import gqlalchemy.memgraph_constants as mg_consts

__all__ = ("Memgraph",)


class MemgraphConstants:
    CONSTRAINT_TYPE = "constraint type"
    EXISTS = "exists"
    LABEL = "label"
    PROPERTY = "property"
    PROPERTIES = "properties"
    UNIQUE = "unique"


class Memgraph(DatabaseClient):
    def __init__(
        self,
        host: str = mg_consts.MG_HOST,
        port: int = mg_consts.MG_PORT,
        username: str = mg_consts.MG_USERNAME,
        password: str = mg_consts.MG_PASSWORD,
        encrypted: bool = mg_consts.MG_ENCRYPTED,
        client_name: str = mg_consts.MG_CLIENT_NAME,
        lazy: bool = mg_consts.MG_LAZY,
    ):
        super().__init__(
            host=host, port=port, username=username, password=password, encrypted=encrypted, client_name=client_name
        )
        self._lazy = lazy
        self._on_disk_db = None

    def get_indexes(self) -> List[MemgraphIndex]:
        """Returns a list of all database indexes (label and label-property types)."""
        indexes = []
        for result in self.execute_and_fetch("SHOW INDEX INFO;"):
            indexes.append(
                MemgraphIndex(
                    result[MemgraphConstants.LABEL],
                    result[MemgraphConstants.PROPERTY],
                )
            )
        return indexes

    def ensure_indexes(self, indexes: List[MemgraphIndex]) -> None:
        """Ensures that database indexes match input indexes."""
        old_indexes = set(self.get_indexes())
        new_indexes = set(indexes)
        for obsolete_index in old_indexes.difference(new_indexes):
            self.drop_index(obsolete_index)
        for missing_index in new_indexes.difference(old_indexes):
            self.create_index(missing_index)

    def get_constraints(
        self,
    ) -> List[Union[MemgraphConstraintExists, MemgraphConstraintUnique]]:
        """Returns a list of all database constraints (label and label-property types)."""
        constraints: List[Union[MemgraphConstraintExists, MemgraphConstraintUnique]] = []
        for result in self.execute_and_fetch("SHOW CONSTRAINT INFO;"):
            if result[MemgraphConstants.CONSTRAINT_TYPE] == MemgraphConstants.UNIQUE:
                constraints.append(
                    MemgraphConstraintUnique(
                        result[MemgraphConstants.LABEL],
                        tuple(result[MemgraphConstants.PROPERTIES]),
                    )
                )
            elif result[MemgraphConstants.CONSTRAINT_TYPE] == MemgraphConstants.EXISTS:
                constraints.append(
                    MemgraphConstraintExists(
                        result[MemgraphConstants.LABEL],
                        result[MemgraphConstants.PROPERTIES],
                    )
                )
        return constraints

    def get_exists_constraints(
        self,
    ) -> List[MemgraphConstraintExists]:
        return [x for x in self.get_constraints() if isinstance(x, MemgraphConstraintExists)]

    def get_unique_constraints(
        self,
    ) -> List[MemgraphConstraintUnique]:
        return [x for x in self.get_constraints() if isinstance(x, MemgraphConstraintUnique)]

    def new_connection(self) -> Connection:
        """Creates new Memgraph connection."""
        args = dict(
            host=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            encrypted=self._encrypted,
            client_name=self._client_name,
        )
        return MemgraphConnection(**args)

    def create_stream(self, stream: MemgraphStream) -> None:
        """Create a stream."""
        query = stream.to_cypher()
        self.execute(query)

    def start_stream(self, stream: MemgraphStream) -> None:
        """Start a stream."""
        query = f"START STREAM {stream.name};"
        self.execute(query)

    def get_streams(self) -> List[str]:
        """Returns a list of all streams."""
        streams = []
        for result in self.execute_and_fetch("SHOW STREAMS;"):
            streams.append(result)
        return streams

    def drop_stream(self, stream: MemgraphStream) -> None:
        """Drop a stream."""
        query = f"DROP STREAM {stream.name};"
        self.execute(query)

    def create_trigger(self, trigger: MemgraphTrigger) -> None:
        """Creates a trigger."""
        query = trigger.to_cypher()
        self.execute(query)

    def get_triggers(self) -> List[MemgraphTrigger]:
        """Returns a list of all database triggers."""
        triggers_list = list(self.execute_and_fetch("SHOW TRIGGERS;"))
        memgraph_triggers_list = []
        for trigger in triggers_list:
            event_type = trigger["event type"]
            event_object = None

            if event_type == "ANY":
                event_type = None
            elif len(event_type.split()) > 1:
                [event_object, event_type] = [part for part in event_type.split()]

            memgraph_triggers_list.append(
                MemgraphTrigger(
                    name=trigger["trigger name"],
                    event_type=event_type,
                    event_object=event_object,
                    execution_phase=trigger["phase"].split()[0],
                    statement=trigger["statement"],
                )
            )
        return memgraph_triggers_list

    def drop_trigger(self, trigger: MemgraphTrigger) -> None:
        """Drop a trigger."""
        query = f"DROP TRIGGER {trigger.name};"
        self.execute(query)

    def drop_triggers(self) -> None:
        """Drops all triggers in the database."""
        for trigger in self.get_triggers():
            self.drop_trigger(trigger)

    def _new_connection(self) -> Connection:
        """Creates new Memgraph connection."""
        args = dict(
            host=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            encrypted=self._encrypted,
            client_name=self._client_name,
        )
        return MemgraphConnection(**args)

    def init_disk_storage(self, on_disk_db: OnDiskPropertyDatabase) -> None:
        """Adds and OnDiskPropertyDatabase to the database so that any property
        that has a Field(on_disk=True) can be stored to and loaded from
        an OnDiskPropertyDatabase.
        """
        self.on_disk_db = on_disk_db

    def remove_on_disk_storage(self) -> None:
        """Removes the OnDiskPropertyDatabase from the database."""
        self.on_disk_db = None

    def save_node(self, node: Node) -> Node:
        """Saves node to the database.
        If the node._id is not None it fetches the node with the same id from
        the database and updates it's fields.
        If the node has unique fields it fetches the nodes with the same unique
        fields from the database and updates it's fields.
        Otherwise it creates a new node with the same properties.
        Null properties are ignored.
        """
        result = None
        if node._id is not None:
            result = self.save_node_with_id(node)
        elif node.has_unique_fields():
            matching_nodes = list(self._get_nodes_with_unique_fields(node))
            if len(matching_nodes) > 1:
                raise GQLAlchemyUniquenessConstraintError(
                    f"Uniqueness constraints match multiple nodes: {matching_nodes}"
                )
            elif len(matching_nodes) == 1:
                node._id = matching_nodes[0]["node"]._id
                result = self.save_node_with_id(node)
            else:
                result = self.create_node(node)
        else:
            result = self.create_node(node)

        result = self._save_node_properties_on_disk(node, result)
        return result

    def _save_node_properties_on_disk(self, node: Node, result: Node) -> Node:
        """Saves all on_disk properties to the on disk database attached to
        the database.
        """
        for field in node.__fields__:
            value = getattr(node, field, None)
            if value is not None and "on_disk" in node.__fields__[field].field_info.extra:
                if self.on_disk_db is None:
                    raise GQLAlchemyOnDiskPropertyDatabaseNotDefinedError()
                self.on_disk_db.save_node_property(result._id, field, value)
                setattr(result, field, value)

        return result

    def load_node(self, node: Node) -> Optional[Node]:
        """Loads a node from the database.
        If the node._id is not None it fetches the node from the database with that
        internal id.
        If the node has unique fields it fetches the node from the database with
        those unique fields set.
        Otherwise it tries to find any node in the database that has all properties
        set to exactly the same values.
        If no node is found or no properties are set it raises a GQLAlchemyError.
        """
        if node._id is not None:
            result = self.load_node_with_id(node)
        elif node.has_unique_fields():
            matching_node = self.get_variable_assume_one(
                query_result=self._get_nodes_with_unique_fields(node), variable_name="node"
            )
            result = matching_node
        else:
            result = self.load_node_with_all_properties(node)

        result = self._load_node_properties_on_disk(result)
        return result

    def _load_node_properties_on_disk(self, result: Node) -> Node:
        """Loads all on_disk properties from the on disk database."""
        for field in result.__fields__:
            value = getattr(result, field, None)
            if "on_disk" in result.__fields__[field].field_info.extra:
                if self.on_disk_db is None:
                    raise GQLAlchemyOnDiskPropertyDatabaseNotDefinedError()
                try:
                    new_value = self.on_disk_db.load_node_property(result._id, field)
                except sqlite3.OperationalError:
                    new_value = value
                setattr(result, field, new_value)

        return result

    def load_relationship(self, relationship: Relationship) -> Optional[Relationship]:
        """Returns a relationship loaded from the database.
        If the relationship._id is not None it fetches the relationship from
        the database that has the same internal id.
        Otherwise it returns the relationship whose relationship._start_node_id
        and relationship._end_node_id and all relationship properties that
        are not None match the relationship in the database.
        If there is no relationship like that in the database, or if there are
        multiple relationships like that in the database, throws GQLAlchemyError.
        """
        if relationship._id is not None:
            result = self.load_relationship_with_id(relationship)
        elif relationship._start_node_id is not None and relationship._end_node_id is not None:
            result = self.load_relationship_with_start_node_id_and_end_node_id(relationship)
        else:
            raise GQLAlchemyError("Can't load a relationship without a start_node_id and end_node_id.")
        result = self._load_relationship_properties_on_disk(result)
        return result

    def _load_relationship_properties_on_disk(self, result: Relationship) -> Relationship:
        """Returns the relationship with all on_disk properties loaded from
        the OnDiskPropertyDatabase.
        If there is no OnDiskPropertyDatabase set with
        Memgraph().init_disk_storage() throws a
        GQLAlchemyOnDiskPropertyDatabaseNotDefinedError.
        """
        for field in result.__fields__:
            value = getattr(result, field, None)
            if "on_disk" in result.__fields__[field].field_info.extra:
                if self.on_disk_db is None:
                    raise GQLAlchemyOnDiskPropertyDatabaseNotDefinedError()
                try:
                    new_value = self.on_disk_db.load_relationship_property(result._id, field)
                except sqlite3.OperationalError:
                    new_value = value
                setattr(result, field, new_value)

        return result

    def save_relationship(self, relationship: Relationship) -> Optional[Relationship]:
        """Saves a relationship to the database.
        If relationship._id is not None it finds the relationship in the database
        and updates it's properties with the values in `relationship`.
        If relationship._id is None, it creates a new relationship.
        If you want to set a relationship._id instead of creating a new
        relationship, use `load_relationship` first.
        """
        if relationship._id is not None:
            result = self.save_relationship_with_id(relationship)
        elif relationship._start_node_id is not None and relationship._end_node_id is not None:
            result = self.create_relationship(relationship)
        else:
            raise GQLAlchemyError("Can't create a relationship without start_node_id and end_node_id.")

        result = self._save_relationship_properties_on_disk(relationship, result)
        return result

    def _save_relationship_properties_on_disk(self, relationship: Relationship, result: Relationship) -> Relationship:
        """Saves on_disk relationship properties on the OnDiskPropertyDatabase
        added with Memgraph().init_disk_storage(db). If OnDiskPropertyDatabase
        is not defined raises GQLAlchemyOnDiskPropertyDatabaseNotDefinedError.
        """
        for field in relationship.__fields__:
            value = getattr(relationship, field, None)
            if value is not None and "on_disk" in relationship.__fields__[field].field_info.extra:
                if self.on_disk_db is None:
                    raise GQLAlchemyOnDiskPropertyDatabaseNotDefinedError()
                self.on_disk_db.save_relationship_property(result._id, field, value)
                setattr(result, field, value)

        return result

    def get_procedures(self, starts_with: Optional[str] = None, update: bool = False) -> List["QueryModule"]:
        """Return query procedures.

        Maintains a list of query modules in the Memgraph object. If starts_with
        is defined then return those modules that start with starts_with string.

        Args:
            starts_with: Return those modules that start with this string.
            (Optional)
            update: Whether to update the list of modules in
            self.query_modules. (Optional)
        """
        if not hasattr(self, "query_modules") or update:
            results = self.execute_and_fetch("CALL mg.procedures() YIELD *;")
            self.query_modules = [QueryModule(**module_dict) for module_dict in results]

        return (
            self.query_modules
            if starts_with is None
            else [q for q in self.query_modules if q.name.startswith(starts_with)]
        )

    def add_query_module(self, file_path: str, module_name: str) -> "Memgraph":
        """Function for adding a query module in Python written language to Memgraph.
        Example can be found in the functions below (with_kafka_stream, with_power_bi).

        The module is synced dynamically then with the database to enable higher processing
        capabilities.

        Args:
            file_name (str): path to file containing module.
            module_name (str): name of the module.

        Returns:
            Memgraph: Memgraph object.
        """
        if not os.path.isfile(file_path):
            raise GQLAlchemyFileNotFoundError(path=file_path)

        file_text = open(file_path, "r").read().replace("'", '"')
        query = f"CALL mg.create_module_file('{module_name}','{file_text}') YIELD *;"
        list(self.execute_and_fetch(query))

        return self

    def with_kafka_stream(self) -> "Memgraph":
        """Load kafka stream query module.
        Returns:
            Memgraph: Memgraph instance
        """
        file_path = "gqlalchemy/query_modules/push_streams/kafka.py"
        module_name = "kafka_stream.py"

        return self.add_query_module(file_path=file_path, module_name=module_name)

    def with_power_bi(self) -> "Memgraph":
        """Load power_bi stream query module.
        Returns:
            Memgraph: Memgraph instance
        """
        file_path = "gqlalchemy/query_modules/push_streams/power_bi.py"
        module_name = "power_bi_stream.py"

        return self.add_query_module(file_path=file_path, module_name=module_name)
