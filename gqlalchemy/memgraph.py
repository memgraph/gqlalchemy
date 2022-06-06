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

from typing import Any, Dict, Iterator, List, Optional, Union

from .connection import Connection
from .disk_storage import OnDiskPropertyDatabase
from .graph_algorithms.query_modules import QueryModule
from .exceptions import (
    GQLAlchemyError,
    GQLAlchemyUniquenessConstraintError,
    GQLAlchemyOnDiskPropertyDatabaseNotDefinedError,
)
from .models import (
    MemgraphConstraint,
    MemgraphConstraintExists,
    MemgraphConstraintUnique,
    MemgraphIndex,
    MemgraphStream,
    MemgraphTrigger,
    Node,
    Relationship,
)


__all__ = ("Memgraph",)

MG_HOST = os.getenv("MG_HOST", "127.0.0.1")
MG_PORT = int(os.getenv("MG_PORT", "7687"))
MG_USERNAME = os.getenv("MG_USERNAME", "")
MG_PASSWORD = os.getenv("MG_PASSWORD", "")
MG_ENCRYPTED = os.getenv("MG_ENCRYPT", "false").lower() == "true"
MG_CLIENT_NAME = os.getenv("MG_CLIENT_NAME", "GQLAlchemy")
MG_LAZY = os.getenv("MG_LAZY", "false").lower() == "true"


class MemgraphConstants:
    CONSTRAINT_TYPE = "constraint type"
    EXISTS = "exists"
    LABEL = "label"
    PROPERTY = "property"
    PROPERTIES = "properties"
    UNIQUE = "unique"


class Memgraph:
    def __init__(
        self,
        host: str = MG_HOST,
        port: int = MG_PORT,
        username: str = MG_USERNAME,
        password: str = MG_PASSWORD,
        encrypted: bool = MG_ENCRYPTED,
        client_name: str = MG_CLIENT_NAME,
        lazy: bool = MG_LAZY,
    ):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._encrypted = encrypted
        self._client_name = client_name
        self._lazy = lazy
        self._cached_connection: Optional[Connection] = None
        self._on_disk_db = None

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    def execute_and_fetch(self, query: str, connection: Connection = None) -> Iterator[Dict[str, Any]]:
        """Executes Cypher query and returns iterator of results."""
        connection = connection or self._get_cached_connection()
        return connection.execute_and_fetch(query)

    def execute(self, query: str, connection: Connection = None) -> None:
        """Executes Cypher query without returning any results."""
        connection = connection or self._get_cached_connection()
        connection.execute(query)

    def create_index(self, index: MemgraphIndex) -> None:
        """Creates an index (label or label-property type) in the database"""
        query = f"CREATE INDEX ON {index.to_cypher()};"
        self.execute(query)

    def drop_index(self, index: MemgraphIndex) -> None:
        """Drops an index (label or label-property type) in the database"""
        query = f"DROP INDEX ON {index.to_cypher()};"
        self.execute(query)

    def get_indexes(self) -> List[MemgraphIndex]:
        """Returns a list of all database indexes (label and label-property types)"""
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
        """Ensures that database indexes match input indexes"""
        old_indexes = set(self.get_indexes())
        new_indexes = set(indexes)
        for obsolete_index in old_indexes.difference(new_indexes):
            self.drop_index(obsolete_index)
        for missing_index in new_indexes.difference(old_indexes):
            self.create_index(missing_index)

    def drop_indexes(self) -> None:
        """Drops all indexes in the database"""
        self.ensure_indexes(indexes=[])

    def create_constraint(self, index: MemgraphConstraint) -> None:
        """Creates a constraint (label or label-property type) in the database"""
        query = f"CREATE CONSTRAINT ON {index.to_cypher()};"
        self.execute(query)

    def drop_constraint(self, index: MemgraphConstraint) -> None:
        """Drops a constraint (label or label-property type) in the database"""
        query = f"DROP CONSTRAINT ON {index.to_cypher()};"
        self.execute(query)

    def get_constraints(
        self,
    ) -> List[Union[MemgraphConstraintExists, MemgraphConstraintUnique]]:
        """Returns a list of all database constraints (label and label-property types)"""
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

    def ensure_constraints(
        self,
        constraints: List[Union[MemgraphConstraintExists, MemgraphConstraintUnique]],
    ) -> None:
        """Ensures that database constraints match input constraints"""
        old_constraints = set(self.get_constraints())
        new_constraints = set(constraints)
        for obsolete_constraints in old_constraints.difference(new_constraints):
            self.drop_constraint(obsolete_constraints)
        for missing_constraint in new_constraints.difference(old_constraints):
            self.create_constraint(missing_constraint)

    def create_stream(self, stream: MemgraphStream) -> None:
        """Create a stream"""
        query = stream.to_cypher()
        self.execute(query)

    def start_stream(self, stream: MemgraphStream) -> None:
        """Start a stream"""
        query = f"START STREAM {stream.name};"
        self.execute(query)

    def get_streams(self) -> List[str]:
        """Returns a list of all streams"""
        streams = []
        for result in self.execute_and_fetch("SHOW STREAMS;"):
            streams.append(result)
        return streams

    def drop_stream(self, stream: MemgraphStream) -> None:
        """Drop a stream"""
        query = f"DROP STREAM {stream.name};"
        self.execute(query)

    def drop_database(self):
        """Drops database by removing all nodes and edges"""
        self.execute("MATCH (n) DETACH DELETE n;")

    def create_trigger(self, trigger: MemgraphTrigger) -> None:
        """Creates a trigger"""
        query = trigger.to_cypher()
        self.execute(query)

    def get_triggers(self) -> List[str]:
        """Returns a list of all database triggers"""
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
        """Drop a trigger"""
        query = f"DROP TRIGGER {trigger.name};"
        self.execute(query)

    def drop_triggers(self) -> None:
        """Drops all triggers in the database"""
        for trigger in self.get_triggers():
            self.drop_trigger(trigger)

    def _get_cached_connection(self) -> Connection:
        """Returns cached connection if it exists, creates it otherwise"""
        if self._cached_connection is None or not self._cached_connection.is_active():
            self._cached_connection = self._new_connection()

        return self._cached_connection

    def _new_connection(self) -> Connection:
        """Creates new Memgraph connection"""
        args = dict(
            host=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            encrypted=self._encrypted,
            client_name=self._client_name,
        )
        return Connection.create(**args)

    def init_disk_storage(self, on_disk_db: OnDiskPropertyDatabase) -> None:
        """Adds and OnDiskPropertyDatabase to Memgraph so that any property
        that has a Field(on_disk=True) can be stored to and loaded from
        an OnDiskPropertyDatabase.
        """
        self.on_disk_db = on_disk_db

    def remove_on_disk_storage(self) -> None:
        """Removes the OnDiskPropertyDatabase from Memgraph"""
        self.on_disk_db = None

    def _get_nodes_with_unique_fields(self, node: Node) -> Optional[Node]:
        """Get's all nodes from Memgraph that have any of the unique fields
        set to the values in the `node` object.
        """
        return self.execute_and_fetch(
            f"MATCH (node: {node._label})"
            + f" WHERE {node._get_cypher_unique_fields_or_block('node')}"
            + " RETURN node;"
        )

    def get_variable_assume_one(self, query_result: Iterator[Dict[str, Any]], variable_name: str) -> Any:
        """Returns a single result from the query_result (usually gotten from
        the execute_and_fetch function).
        If there is more than one result, raises a GQLAlchemyError.
        """
        result = next(query_result, None)
        next_result = next(query_result, None)
        if result is None:
            raise GQLAlchemyError("No result found. Result list is empty.")
        elif next_result is not None:
            raise GQLAlchemyError(
                f"One result expected, but more than one result found. First result: {result}, second result: {next_result}"
            )
        elif variable_name not in result:
            raise GQLAlchemyError(f"Variable name {variable_name} not present in result.")

        return result[variable_name]

    def create_node(self, node: Node) -> Optional[Node]:
        """Creates a node in Memgraph from the `node` object."""
        results = self.execute_and_fetch(
            f"CREATE (node:{node._label}) {node._get_cypher_set_properties('node')} RETURN node;"
        )
        return self.get_variable_assume_one(results, "node")

    def save_node(self, node: Node) -> Node:
        """Saves node to Memgraph.
        If the node._id is not None it fetches the node with the same id from
        Memgraph and updates it's fields.
        If the node has unique fields it fetches the nodes with the same unique
        fields from Memgraph and updates it's fields.
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

    def save_nodes(self, nodes: List[Node]) -> None:
        """Saves a list of nodes to Memgraph."""
        for i in range(len(nodes)):
            nodes[i]._id = self.save_node(nodes[i])._id

    def _save_node_properties_on_disk(self, node: Node, result: Node) -> Node:
        """Saves all on_disk properties to the on disk database attached to
        Memgraph.
        """
        for field in node.__fields__:
            value = getattr(node, field, None)
            if value is not None and "on_disk" in node.__fields__[field].field_info.extra:
                if self.on_disk_db is None:
                    raise GQLAlchemyOnDiskPropertyDatabaseNotDefinedError()
                self.on_disk_db.save_node_property(result._id, field, value)
                setattr(result, field, value)

        return result

    def save_node_with_id(self, node: Node) -> Optional[Node]:
        """Saves a node in Memgraph using the internal Memgraph id."""
        results = self.execute_and_fetch(
            f"MATCH (node: {node._label})"
            + f" WHERE id(node) = {node._id}"
            + f" {node._get_cypher_set_properties('node')}"
            + " RETURN node;"
        )

        return self.get_variable_assume_one(results, "node")

    def load_node(self, node: Node) -> Optional[Node]:
        """Loads a node from Memgraph.
        If the node._id is not None it fetches the node from Memgraph with that
        internal id.
        If the node has unique fields it fetches the node from Memgraph with
        those unique fields set.
        Otherwise it tries to find any node in Memgraph that has all properties
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

    def load_node_with_all_properties(self, node: Node) -> Optional[Node]:
        """Loads a node from Memgraph with all equal property values."""
        results = self.execute_and_fetch(
            f"MATCH (node: {node._label}) WHERE {node._get_cypher_fields_and_block('node')} RETURN node;"
        )
        return self.get_variable_assume_one(results, "node")

    def load_node_with_id(self, node: Node) -> Optional[Node]:
        """Loads a node with the same internal Memgraph id."""
        results = self.execute_and_fetch(f"MATCH (node: {node._label}) WHERE id(node) = {node._id} RETURN node;")

        return self.get_variable_assume_one(results, "node")

    def load_relationship(self, relationship: Relationship) -> Optional[Relationship]:
        """Returns a relationship loaded from Memgraph.
        If the relationship._id is not None it fetches the relationship from
        Memgraph that has the same internal id.
        Otherwise it returns the relationship whose relationship._start_node_id
        and relationship._end_node_id and all relationship properties that
        are not None match the relationship in Memgraph.
        If there is no relationship like that in Memgraph, or if there are
        multiple relationships like that in Memgraph, throws GQLAlchemyError.
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

    def load_relationship_with_id(self, relationship: Relationship) -> Optional[Relationship]:
        """Loads a relationship from Memgraph using the internal id."""
        results = self.execute_and_fetch(
            f"MATCH (start_node)-[relationship: {relationship._type}]->(end_node)"
            + f" WHERE id(start_node) = {relationship._start_node_id}"
            + f" AND id(end_node) = {relationship._end_node_id}"
            + f" AND id(relationship) = {relationship._id}"
            + " RETURN relationship;"
        )
        return self.get_variable_assume_one(results, "relationship")

    def load_relationship_with_start_node_id_and_end_node_id(
        self, relationship: Relationship
    ) -> Optional[Relationship]:
        """Loads a relationship from Memgraph using start node and end node id
        for which all properties of the relationship that are not None match.
        """
        and_block = relationship._get_cypher_fields_and_block("relationship")
        if and_block.strip():
            and_block = " AND " + and_block
        results = self.execute_and_fetch(
            f"MATCH (start_node)-[relationship:{relationship._type}]->(end_node)"
            + f" WHERE id(start_node) = {relationship._start_node_id}"
            + f" AND id(end_node) = {relationship._end_node_id}"
            + and_block
            + " RETURN relationship;"
        )
        return self.get_variable_assume_one(results, "relationship")

    def save_relationship(self, relationship: Relationship) -> Optional[Relationship]:
        """Saves a relationship to Memgraph.
        If relationship._id is not None it finds the relationship in Memgraph
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

    def save_relationships(self, relationships: List[Relationship]) -> None:
        """Saves a list of relationships to Memgraph."""
        for i in range(len(relationships)):
            relationships[i]._id = self.save_relationship(relationships[i])._id

    def _save_relationship_properties_on_disk(self, relationship: Relationship, result: Relationship) -> Relationship:
        """Saves on_disk relationship propeties on the OnDiskPropertyDatabase
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

    def save_relationship_with_id(self, relationship: Relationship) -> Optional[Relationship]:
        """Saves a relationship in Memgraph using the relationship._id."""
        results = self.execute_and_fetch(
            f"MATCH (start_node)-[relationship: {relationship._type}]->(end_node)"
            + f" WHERE id(start_node) = {relationship._start_node_id}"
            + f" AND id(end_node) = {relationship._end_node_id}"
            + f" AND id(relationship) = {relationship._id}"
            + relationship._get_cypher_set_properties("relationship")
            + " RETURN node;"
        )

        return self.get_variable_assume_one(results, "relationship")

    def create_relationship(self, relationship: Relationship) -> Optional[Relationship]:
        """Creates a new relationship in Memgraph."""
        results = self.execute_and_fetch(
            "MATCH (start_node), (end_node)"
            + f" WHERE id(start_node) = {relationship._start_node_id}"
            + f" AND id(end_node) = {relationship._end_node_id}"
            + f" CREATE (start_node)-[relationship:{relationship._type}]->(end_node)"
            + relationship._get_cypher_set_properties("relationship")
            + "RETURN relationship"
        )

        return self.get_variable_assume_one(results, "relationship")

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
