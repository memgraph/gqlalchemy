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

from typing import Any, Dict, Iterator, List, Optional, Union

from .connection import Connection, Neo4jConnection
from .exceptions import (
    GQLAlchemyError,
    GQLAlchemyUniquenessConstraintError,
)
from .models import (
    Neo4jConstraint,
    Neo4jConstraintExists,
    Neo4jConstraintUnique,
    Neo4jIndex,
    Node,
    Relationship,
)


__all__ = ("Neo4j",)

NEO4J_HOST = os.getenv("NEO4J_HOST", "localhost")
NEO4J_PORT = int(os.getenv("NEO4J_PORT", "7687"))
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "test")
NEO4J_ENCRYPTED = os.getenv("NEO4J_ENCRYPT", "false").lower() == "true"
NEO4J_CLIENT_NAME = os.getenv("NEO4J_CLIENT_NAME", "neo4j")


class Neo4jConstants:
    CONSTRAINT_TYPE = "constraint type"
    EXISTS = "exists"
    LABEL = "labelsOrTypes"
    PROPERTY = "property"
    PROPERTIES = "properties"
    UNIQUE = "unique"
    LOOKUP = "LOOKUP"
    TYPE = "type"
    UNIQUE = "UNIQUE"
    UNIQUENESS = "uniqueness"


class Neo4j:
    def __init__(
        self,
        host: str = NEO4J_HOST,
        port: int = NEO4J_PORT,
        username: str = NEO4J_USERNAME,
        password: str = NEO4J_PASSWORD,
        encrypted: bool = NEO4J_ENCRYPTED,
        client_name: str = NEO4J_CLIENT_NAME,
    ):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._encrypted = encrypted
        self._client_name = client_name
        self._cached_connection: Optional[Connection] = None

    def execute_and_fetch(self, query: str, connection: Connection = None) -> Iterator[Dict[str, Any]]:
        """Executes Cypher query and returns iterator of results."""
        connection = connection or self._get_cached_connection()
        return connection.execute_and_fetch(query)

    def execute(self, query: str, connection: Connection = None) -> None:
        """Executes Cypher query without returning any results."""
        connection = connection or self._get_cached_connection()
        connection.execute(query)

    def create_index(self, index: Neo4jIndex) -> None:
        """Creates an index (label or label-property type) in the database"""
        query = f"CREATE INDEX ON {index.to_cypher()};"
        self.execute(query)

    def drop_index(self, index: Neo4jIndex) -> None:
        """Drops an index (label or label-property type) in the database"""
        query = f"DROP INDEX ON {index.to_cypher()};"
        self.execute(query)

    def get_indexes(self) -> List[Neo4jIndex]:
        """Returns a list of all database indexes (label and label-property types)"""
        indexes = []
        for result in self.execute_and_fetch("SHOW INDEX;"):
            if result[Neo4jConstants.TYPE] != Neo4jConstants.LOOKUP:
                indexes.append(
                    Neo4jIndex(
                        result[Neo4jConstants.LABEL][0],
                        result[Neo4jConstants.PROPERTIES][0],
                        result[Neo4jConstants.TYPE],
                        result[Neo4jConstants.UNIQUENESS],
                    )
                )
            else:
                indexes.append(
                    Neo4jIndex(
                        result[Neo4jConstants.LABEL],
                        result[Neo4jConstants.PROPERTIES],
                        result[Neo4jConstants.TYPE],
                        result[Neo4jConstants.UNIQUENESS],
                    )
                )
        return indexes

    def ensure_indexes(self, indexes: List[Neo4jIndex]) -> None:
        """Ensures that database indexes match input indexes"""
        old_indexes = set(self.get_indexes())
        new_indexes = set(indexes)
        for obsolete_index in old_indexes.difference(new_indexes):
            if obsolete_index.type != Neo4jConstants.LOOKUP and obsolete_index.uniqueness != Neo4jConstants.UNIQUE:
                self.drop_index(obsolete_index)
        for missing_index in new_indexes.difference(old_indexes):
            self.create_index(missing_index)

    def drop_indexes(self) -> None:
        """Drops all indexes in the database"""
        self.ensure_indexes(indexes=[])

    def create_constraint(self, index: Neo4jConstraint) -> None:
        """Creates a constraint (label or label-property type) in the database"""
        query = f"CREATE CONSTRAINT ON {index.to_cypher()};"
        self.execute(query)

    def drop_constraint(self, index: Neo4jConstraint) -> None:
        """Drops a constraint (label or label-property type) in the database"""
        query = f"DROP CONSTRAINT ON {index.to_cypher()};"
        self.execute(query)

    def get_constraints(
        self,
    ) -> List[Union[Neo4jConstraintExists, Neo4jConstraintUnique]]:
        """Returns a list of all database constraints (label and label-property types)"""
        constraints: List[Union[Neo4jConstraintExists, Neo4jConstraintUnique]] = []
        for result in self.execute_and_fetch("SHOW CONSTRAINTS;"):
            if result[Neo4jConstants.TYPE] == "UNIQUENESS":
                constraints.append(
                    Neo4jConstraintUnique(
                        result[Neo4jConstants.LABEL][0],
                        tuple(result[Neo4jConstants.PROPERTIES]),
                    )
                )
        return constraints

    def get_exists_constraints(
        self,
    ) -> List[Neo4jConstraintExists]:
        return [x for x in self.get_constraints() if isinstance(x, Neo4jConstraintExists)]

    def get_unique_constraints(
        self,
    ) -> List[Neo4jConstraintUnique]:
        return [x for x in self.get_constraints() if isinstance(x, Neo4jConstraintUnique)]

    def ensure_constraints(
        self,
        constraints: List[Union[Neo4jConstraintExists, Neo4jConstraintUnique]],
    ) -> None:
        """Ensures that database constraints match input constraints"""
        old_constraints = set(self.get_constraints())
        new_constraints = set(constraints)
        for obsolete_constraints in old_constraints.difference(new_constraints):
            self.drop_constraint(obsolete_constraints)
        for missing_constraint in new_constraints.difference(old_constraints):
            self.create_constraint(missing_constraint)

    def drop_database(self):
        """Drops database by removing all nodes and edges"""
        self.execute("MATCH (n) DETACH DELETE n;")

    def _get_cached_connection(self) -> Connection:
        """Returns cached connection if it exists, creates it otherwise"""
        if self._cached_connection is None or not self._cached_connection.is_active():
            self._cached_connection = self.new_connection()

        return self._cached_connection

    def new_connection(self) -> Connection:
        """Creates new Neo4j connection"""
        args = dict(
            host=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            encrypted=self._encrypted,
            client_name=self._client_name,
        )
        return Neo4jConnection(**args)

    def _get_nodes_with_unique_fields(self, node: Node) -> Optional[Node]:
        """Get's all nodes from Neo4j that have any of the unique fields
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
        """Creates a node in Neo4j from the `node` object."""
        results = self.execute_and_fetch(
            f"CREATE (node:{node._label}) {node._get_cypher_set_properties('node')} RETURN node;"
        )
        return self.get_variable_assume_one(results, "node")

    def save_node(self, node: Node) -> Node:
        """Saves node to Neo4j.
        If the node._id is not None it fetches the node with the same id from
        Neo4j and updates it's fields.
        If the node has unique fields it fetches the nodes with the same unique
        fields from Neo4j and updates it's fields.
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

        return result

    def save_nodes(self, nodes: List[Node]) -> None:
        """Saves a list of nodes to Neo4j."""
        for i in range(len(nodes)):
            nodes[i]._id = self.save_node(nodes[i])._id

    def save_node_with_id(self, node: Node) -> Optional[Node]:
        """Saves a node in Neo4j using the internal Neo4j id."""
        results = self.execute_and_fetch(
            f"MATCH (node: {node._label})"
            + f" WHERE id(node) = {node._id}"
            + f" {node._get_cypher_set_properties('node')}"
            + " RETURN node;"
        )

        return self.get_variable_assume_one(results, "node")

    def load_node(self, node: Node) -> Optional[Node]:
        """Loads a node from Neo4j.
        If the node._id is not None it fetches the node from Neo4j with that
        internal id.
        If the node has unique fields it fetches the node from Neo4j with
        those unique fields set.
        Otherwise it tries to find any node in Neo4j that has all properties
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

        return result

    def load_node_with_all_properties(self, node: Node) -> Optional[Node]:
        """Loads a node from Neo4j with all equal property values."""
        results = self.execute_and_fetch(
            f"MATCH (node: {node._label}) WHERE {node._get_cypher_fields_and_block('node')} RETURN node;"
        )
        return self.get_variable_assume_one(results, "node")

    def load_node_with_id(self, node: Node) -> Optional[Node]:
        """Loads a node with the same internal Neo4j id."""
        results = self.execute_and_fetch(f"MATCH (node: {node._label}) WHERE id(node) = {node._id} RETURN node;")

        return self.get_variable_assume_one(results, "node")

    def load_relationship(self, relationship: Relationship) -> Optional[Relationship]:
        """Returns a relationship loaded from Neo4j.
        If the relationship._id is not None it fetches the relationship from
        Neo4j that has the same internal id.
        Otherwise it returns the relationship whose relationship._start_node_id
        and relationship._end_node_id and all relationship properties that
        are not None match the relationship in Neo4j.
        If there is no relationship like that in Neo4j, or if there are
        multiple relationships like that in Neo4j, throws GQLAlchemyError.
        """
        if relationship._id is not None:
            result = self.load_relationship_with_id(relationship)
        elif relationship._start_node_id is not None and relationship._end_node_id is not None:
            result = self.load_relationship_with_start_node_id_and_end_node_id(relationship)
        else:
            raise GQLAlchemyError("Can't load a relationship without a start_node_id and end_node_id.")
        return result

    def load_relationship_with_id(self, relationship: Relationship) -> Optional[Relationship]:
        """Loads a relationship from Neo4j using the internal id."""
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
        """Loads a relationship from Neo4j using start node and end node id
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
        """Saves a relationship to Neo4j.
        If relationship._id is not None it finds the relationship in Neo4j
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

        return result

    def save_relationships(self, relationships: List[Relationship]) -> None:
        """Saves a list of relationships to Neo4j."""
        for i in range(len(relationships)):
            relationships[i]._id = self.save_relationship(relationships[i])._id

    def save_relationship_with_id(self, relationship: Relationship) -> Optional[Relationship]:
        """Saves a relationship in Neo4j using the relationship._id."""
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
        """Creates a new relationship in Neo4j."""
        results = self.execute_and_fetch(
            "MATCH (start_node), (end_node)"
            + f" WHERE id(start_node) = {relationship._start_node_id}"
            + f" AND id(end_node) = {relationship._end_node_id}"
            + f" CREATE (start_node)-[relationship:{relationship._type}]->(end_node)"
            + relationship._get_cypher_set_properties("relationship")
            + "RETURN relationship"
        )

        return self.get_variable_assume_one(results, "relationship")
