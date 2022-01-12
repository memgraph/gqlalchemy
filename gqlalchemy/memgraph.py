# Copyright (c) 2016-2021 Memgraph Ltd. [https://memgraph.com]
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

from .connection import Connection
from .models import MemgraphConstraint, MemgraphConstraintExists, MemgraphConstraintUnique, MemgraphIndex, Node
from .utilities import GQLAlchemyError, GQLAlchemyUniquenessConstraintError

__all__ = ("Memgraph",)

MG_HOST = os.getenv("MG_HOST", "127.0.0.1")
MG_PORT = int(os.getenv("MG_PORT", "7687"))
MG_USERNAME = os.getenv("MG_USERNAME", "")
MG_PASSWORD = os.getenv("MG_PASSWORD", "")
MG_ENCRYPTED = os.getenv("MG_ENCRYPT", "false").lower() == "true"


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
    ):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._encrypted = encrypted
        self._cached_connection: Optional[Connection] = None

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
        query = f"CREATE INDEX ON {index.to_cypher()}"
        self.execute(query)

    def drop_index(self, index: MemgraphIndex) -> None:
        """Drops an index (label or label-property type) in the database"""
        query = f"DROP INDEX ON {index.to_cypher()}"
        self.execute(query)

    def get_indexes(self) -> List[MemgraphIndex]:
        """Returns a list of all database indexes (label and label-property types)"""
        indexes = []
        for result in self.execute_and_fetch("SHOW INDEX INFO"):
            indexes.append(MemgraphIndex(result[MemgraphConstants.LABEL], result[MemgraphConstants.PROPERTY]))
        return indexes

    def ensure_indexes(self, indexes: List[MemgraphIndex]) -> None:
        """Ensures that database indexes match input indexes"""
        old_indexes = set(self.get_indexes())
        new_indexes = set(indexes)
        for obsolete_index in old_indexes.difference(new_indexes):
            self.drop_index(obsolete_index)
        for missing_index in new_indexes.difference(old_indexes):
            self.create_index(missing_index)

    def create_constraint(self, index: MemgraphConstraint) -> None:
        """Creates a constraint (label or label-property type) in the database"""
        query = f"CREATE CONSTRAINT ON {index.to_cypher()}"
        self.execute(query)

    def drop_constraint(self, index: MemgraphConstraint) -> None:
        """Drops a constraint (label or label-property type) in the database"""
        query = f"DROP CONSTRAINT ON {index.to_cypher()}"
        self.execute(query)

    def get_constraints(self) -> List[Union[MemgraphConstraintExists, MemgraphConstraintUnique]]:
        """Returns a list of all database constraints (label and label-property types)"""
        constraints: List[Union[MemgraphConstraintExists, MemgraphConstraintUnique]] = []
        for result in self.execute_and_fetch("SHOW CONSTRAINT INFO"):
            if result[MemgraphConstants.CONSTRAINT_TYPE] == MemgraphConstants.UNIQUE:
                constraints.append(
                    MemgraphConstraintUnique(
                        result[MemgraphConstants.LABEL], tuple(result[MemgraphConstants.PROPERTIES])
                    )
                )
            elif result[MemgraphConstants.CONSTRAINT_TYPE] == MemgraphConstants.EXISTS:
                constraints.append(
                    MemgraphConstraintExists(result[MemgraphConstants.LABEL], result[MemgraphConstants.PROPERTIES])
                )
        return constraints

    def ensure_constraints(self, constraints: List[Union[MemgraphConstraintExists, MemgraphConstraintUnique]]) -> None:
        """Ensures that database constraints match input constraints"""
        old_constraints = set(self.get_constraints())
        new_constraints = set(constraints)
        for obsolete_constraints in old_constraints.difference(new_constraints):
            self.drop_constraint(obsolete_constraints)
        for missing_constraint in new_constraints.difference(old_constraints):
            self.create_constraint(missing_constraint)

    def drop_database(self):
        """Drops database by removing all nodes and edges"""
        self.execute("MATCH (n) DETACH DELETE n")

    def _get_cached_connection(self) -> Connection:
        """Returns cached connection if it exists, creates it otherwise"""
        if self._cached_connection is None or not self._cached_connection.is_active():
            self._cached_connection = self.new_connection()

        return self._cached_connection

    def new_connection(self) -> Connection:
        """Creates new Memgraph connection"""
        args = dict(
            host=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            encrypted=self._encrypted,
        )
        return Connection.create(**args)

    def _get_nodes_with_unique_fields(self, node: Node) -> Optional[Node]:
        return self.execute_and_fetch(
            f"MATCH (node: {node._label})" " WHERE " + node._get_cypher_unique_fields_or_block() + " RETURN node"
        )

    def get_variable_assume_one(self, query_result: Iterator[Dict[str, Any]], variable_name: str) -> Any:
        result = next(query_result, None)
        if result is None:
            raise GQLAlchemyError("No result found. Result list is empty.")

        if next(query_result, None) is not None:
            raise GQLAlchemyError("One result expected, but more than one result found.")

        if variable_name not in result:
            raise GQLAlchemyError(f"Variable name {variable_name} not present in result.")

        return result[variable_name]

    def create_node(self, node: Node) -> Optional[Node]:
        results = self.execute_and_fetch(
            f"CREATE (node:{node._label})" + node._get_cypher_set_properties() + "RETURN node"
        )
        return self.get_variable_assume_one(results, "node")

    def save_node(self, node: Node):
        if node._id is not None:
            return self._save_node_with_id(node)

        elif any(getattr(node, key) is not None for key in node._primary_keys):
            matching_nodes = list(self._get_nodes_with_unique_fields(node))
            if len(matching_nodes) > 1:
                raise GQLAlchemyUniquenessConstraintError(
                    f"Uniqueness constraints match multiple nodes: {matching_nodes}"
                )
            elif len(matching_nodes) == 1:
                node._id = matching_nodes[0]["node"]._id
                return self.save_node_with_id(node)
            else:
                return self.create_node(node)
        else:
            return self.create_node(node)

    def save_node_with_id(self, node: Node) -> Optional[Node]:
        results = self.execute_and_fetch(
            f"MATCH (node: {node._label})"
            f" WHERE id(node) = {node._id}" + node._get_cypher_set_properties() + " RETURN node"
        )

        return self.get_variable_assume_one(results, "node")

    def load_node(self, node: Node) -> Optional[Node]:
        if node._id is not None:
            return self.load_node_with_id(node)
        elif any(getattr(node, key) is not None for key in node._primary_keys):
            matching_nodes = list(self._get_nodes_with_unique_fields(node))
            if len(matching_nodes) > 1:
                raise GQLAlchemyUniquenessConstraintError(
                    f"Uniqueness constraints match multiple nodes: {matching_nodes}"
                )
            elif len(matching_nodes) == 1:
                node._id = matching_nodes[0]["node"]._id
                return self.load_node_with_id(node)
            else:
                raise GQLAlchemyError("No node found that matches properties.")
        else:
            return self.load_node_with_all_properties(node)

    def load_node_with_all_properties(self, node: Node) -> Optional[Node]:
        results = self.execute_and_fetch(
            f"MATCH (node: {node._label}" " WHERE " + node._get_cypher_fields_or_block() + " RETURN node"
        )
        return self.get_variable_assume_one(results, "node")

    def load_node_with_id(self, node: Node) -> Optional[Node]:
        results = self.execute_and_fetch(
            f"MATCH (node: {node._label})" f" WHERE id(node) = {node._id}" + node._get_cypher_set_properties() + " RETURN node"
        )

        return self.get_variable_assume_one(results, "node")
