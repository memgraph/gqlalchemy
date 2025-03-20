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

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional

from gqlalchemy.connection import Connection
from gqlalchemy.exceptions import GQLAlchemyError
from gqlalchemy.models import (
    Constraint,
    Index,
    Node,
    Relationship,
)


class DatabaseClient(ABC):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        encrypted: bool,
        client_name: str,
    ):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._encrypted = encrypted
        self._client_name = client_name
        self._cached_connection: Optional[Connection] = None

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    def execute_and_fetch(
        self, query: str, parameters: Dict[str, Any] = {}, connection: Connection = None
    ) -> Iterator[Dict[str, Any]]:
        """Executes Cypher query and returns iterator of results."""
        connection = connection or self._get_cached_connection()
        return connection.execute_and_fetch(query, parameters)

    def execute(self, query: str, parameters: Dict[str, Any] = {}, connection: Connection = None) -> None:
        """Executes Cypher query without returning any results."""
        connection = connection or self._get_cached_connection()
        connection.execute(query, parameters)

    def create_index(self, index: Index) -> None:
        """Creates an index (label or label-property type) in the database."""
        query = f"CREATE INDEX ON {index.to_cypher()};"
        self.execute(query)

    def drop_index(self, index: Index) -> None:
        """Drops an index (label or label-property type) in the database."""
        query = f"DROP INDEX ON {index.to_cypher()};"
        self.execute(query)

    @abstractmethod
    def get_indexes(self) -> List[Index]:
        """Returns a list of all database indexes (label and label-property types)."""
        pass

    @abstractmethod
    def ensure_indexes(self, indexes: List[Index]) -> None:
        """Ensures that database indexes match input indexes."""
        pass

    def drop_indexes(self) -> None:
        """Drops all indexes in the database"""
        self.ensure_indexes(indexes=[])

    def create_constraint(self, index: Constraint) -> None:
        """Creates a constraint (label or label-property type) in the database."""
        query = f"CREATE CONSTRAINT ON {index.to_cypher()};"
        self.execute(query)

    def drop_constraint(self, index: Constraint) -> None:
        """Drops a constraint (label or label-property type) in the database."""
        query = f"DROP CONSTRAINT ON {index.to_cypher()};"
        self.execute(query)

    @abstractmethod
    def get_constraints(
        self,
    ) -> List[Constraint]:
        """Returns a list of all database constraints (label and label-property types)."""
        pass

    @abstractmethod
    def get_exists_constraints(
        self,
    ) -> List[Constraint]:
        pass

    @abstractmethod
    def get_unique_constraints(
        self,
    ) -> List[Constraint]:
        pass

    def ensure_constraints(
        self,
        constraints: List[Constraint],
    ) -> None:
        """Ensures that database constraints match input constraints."""
        old_constraints = set(self.get_constraints())
        new_constraints = set(constraints)
        for obsolete_constraints in old_constraints.difference(new_constraints):
            self.drop_constraint(obsolete_constraints)
        for missing_constraint in new_constraints.difference(old_constraints):
            self.create_constraint(missing_constraint)

    def drop_database(self):
        """Drops database by removing all nodes and edges."""
        self.execute("MATCH (n) DETACH DELETE n;")

    def _get_cached_connection(self) -> Connection:
        """Returns cached connection if it exists, creates it otherwise."""
        if self._cached_connection is None or not self._cached_connection.is_active():
            self._cached_connection = self.new_connection()

        return self._cached_connection

    @abstractmethod
    def new_connection(self) -> Connection:
        """Creates new database connection."""
        pass

    def _get_nodes_with_unique_fields(self, node: Node) -> Optional[Node]:
        """Get's all nodes from the database that have any of the unique fields
        set to the values in the `node` object.
        """
        return self.execute_and_fetch(
            f"MATCH (node: {node._label})" f" WHERE {node._get_cypher_unique_fields_or_block('node')}" f" RETURN node;"
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
        """Creates a node in database from the `node` object."""
        results = self.execute_and_fetch(
            f"CREATE (node:{node._label}) {node._get_cypher_set_properties('node')} RETURN node;"
        )
        return self.get_variable_assume_one(results, "node")

    @abstractmethod
    def save_node(self, node: Node) -> Node:
        """Saves node to database.
        If the node._id is not None, it fetches the node with the same id from
        the database and updates it's fields.
        If the node has unique fields it fetches the nodes with the same unique
        fields from the database and updates it's fields.
        Otherwise it creates a new node with the same properties.
        Null properties are ignored.
        """
        pass

    def save_nodes(self, nodes: List[Node]) -> None:
        """Saves a list of nodes to the database."""
        for i in range(len(nodes)):
            nodes[i]._id = self.save_node(nodes[i])._id

    def save_node_with_id(self, node: Node) -> Optional[Node]:
        """Saves a node to the database using the internal id."""
        results = self.execute_and_fetch(
            f"MATCH (node: {node._label})"
            f" WHERE id(node) = {node._id}"
            f" {node._get_cypher_set_properties('node')}"
            f" RETURN node;"
        )

        return self.get_variable_assume_one(results, "node")

    @abstractmethod
    def load_node(self, node: Node) -> Optional[Node]:
        """Loads a node from the database.
        If the node._id is not None, it fetches the node from the database with that
        internal id.
        If the node has unique fields it fetches the node from the database with
        those unique fields set.
        Otherwise it tries to find any node in the database that has all properties
        set to exactly the same values.
        If no node is found or no properties are set it raises a GQLAlchemyError.
        """
        pass

    def load_node_with_all_properties(self, node: Node) -> Optional[Node]:
        """Loads a node from the database with all equal property values."""
        results = self.execute_and_fetch(
            f"MATCH (node: {node._label}) WHERE {node._get_cypher_fields_and_block('node')} RETURN node;"
        )
        return self.get_variable_assume_one(results, "node")

    def load_node_with_id(self, node: Node) -> Optional[Node]:
        """Loads a node with the same internal database id."""
        results = self.execute_and_fetch(f"MATCH (node: {node._label}) WHERE id(node) = {node._id} RETURN node;")

        return self.get_variable_assume_one(results, "node")

    @abstractmethod
    def load_relationship(self, relationship: Relationship) -> Optional[Relationship]:
        """Returns a relationship loaded from the database.
        If the relationship._id is not None, it fetches the relationship from
        the database that has the same internal id.
        Otherwise it returns the relationship whose relationship._start_node_id
        and relationship._end_node_id and all relationship properties that
        are not None match the relationship in the database.
        If there is no relationship like that in database, or if there are
        multiple relationships like that in database, throws GQLAlchemyError.
        """
        pass

    def load_relationship_with_id(self, relationship: Relationship) -> Optional[Relationship]:
        """Loads a relationship from the database using the internal id."""
        results = self.execute_and_fetch(
            f"MATCH (start_node)-[relationship: {relationship._type}]->(end_node)"
            f" WHERE id(start_node) = {relationship._start_node_id}"
            f" AND id(end_node) = {relationship._end_node_id}"
            f" AND id(relationship) = {relationship._id}"
            f" RETURN relationship;"
        )
        return self.get_variable_assume_one(results, "relationship")

    def load_relationship_with_start_node_id_and_end_node_id(
        self, relationship: Relationship
    ) -> Optional[Relationship]:
        """Loads a relationship from the database using start node and end node id
        for which all properties of the relationship that are not None match.
        """
        and_block = relationship._get_cypher_fields_and_block("relationship")
        if and_block.strip():
            and_block = f" AND {and_block}"
        results = self.execute_and_fetch(
            f"MATCH (start_node)-[relationship:{relationship._type}]->(end_node)"
            f" WHERE id(start_node) = {relationship._start_node_id}"
            f" AND id(end_node) = {relationship._end_node_id}"
            f"{and_block} RETURN relationship;"
        )
        return self.get_variable_assume_one(results, "relationship")

    @abstractmethod
    def save_relationship(self, relationship: Relationship) -> Optional[Relationship]:
        """Saves a relationship to the database.
        If relationship._id is not None it finds the relationship in the database
        and updates it's properties with the values in `relationship`.
        If relationship._id is None, it creates a new relationship.
        If you want to set a relationship._id instead of creating a new
        relationship, use `load_relationship` first.
        """
        pass

    def save_relationships(self, relationships: List[Relationship]) -> None:
        """Saves a list of relationships to the database."""
        for i in range(len(relationships)):
            relationships[i]._id = self.save_relationship(relationships[i])._id

    def save_relationship_with_id(self, relationship: Relationship) -> Optional[Relationship]:
        """Saves a relationship to the database using the relationship._id."""
        results = self.execute_and_fetch(
            f"MATCH (start_node)-[relationship: {relationship._type}]->(end_node)"
            f" WHERE id(start_node) = {relationship._start_node_id}"
            f" AND id(end_node) = {relationship._end_node_id}"
            f" AND id(relationship) = {relationship._id}"
            f"{relationship._get_cypher_set_properties('relationship')} RETURN relationship;"
        )

        return self.get_variable_assume_one(results, "relationship")

    def create_relationship(self, relationship: Relationship) -> Optional[Relationship]:
        """Creates a new relationship in the database."""
        results = self.execute_and_fetch(
            "MATCH (start_node), (end_node)"
            f" WHERE id(start_node) = {relationship._start_node_id}"
            f" AND id(end_node) = {relationship._end_node_id}"
            f" CREATE (start_node)-[relationship:{relationship._type}]->(end_node)"
            f"{relationship._get_cypher_set_properties('relationship')} RETURN relationship"
        )

        return self.get_variable_assume_one(results, "relationship")
