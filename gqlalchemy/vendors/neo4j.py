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
from typing import List, Optional, Union

from gqlalchemy.connection import Connection, Neo4jConnection
from gqlalchemy.exceptions import (
    GQLAlchemyError,
    GQLAlchemyUniquenessConstraintError,
)
from gqlalchemy.models import (
    Neo4jConstraintExists,
    Neo4jConstraintUnique,
    Neo4jIndex,
    Node,
    Relationship,
)
from gqlalchemy.vendors.database_client import DatabaseClient

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


class Neo4j(DatabaseClient):
    def __init__(
        self,
        host: str = NEO4J_HOST,
        port: int = NEO4J_PORT,
        username: str = NEO4J_USERNAME,
        password: str = NEO4J_PASSWORD,
        encrypted: bool = NEO4J_ENCRYPTED,
        client_name: str = NEO4J_CLIENT_NAME,
    ):
        super().__init__(
            host=host, port=port, username=username, password=password, encrypted=encrypted, client_name=client_name
        )
        self._cached_connection: Optional[Connection] = None

    def get_indexes(self) -> List[Neo4jIndex]:
        """Returns a list of all database indexes (label and label-property types)."""
        indexes = []
        for result in self.execute_and_fetch("SHOW INDEX;"):
            indexes.append(
                Neo4jIndex(
                    result[Neo4jConstants.LABEL][0]
                    if result[Neo4jConstants.TYPE] != Neo4jConstants.LOOKUP
                    else result[Neo4jConstants.LABEL],
                    result[Neo4jConstants.PROPERTIES][0]
                    if result[Neo4jConstants.TYPE] != Neo4jConstants.LOOKUP
                    else result[Neo4jConstants.PROPERTIES],
                    result[Neo4jConstants.TYPE],
                    result[Neo4jConstants.UNIQUENESS],
                )
            )
        return indexes

    def ensure_indexes(self, indexes: List[Neo4jIndex]) -> None:
        """Ensures that database indexes match input indexes."""
        old_indexes = set(self.get_indexes())
        new_indexes = set(indexes)
        for obsolete_index in old_indexes.difference(new_indexes):
            if obsolete_index.type != Neo4jConstants.LOOKUP and obsolete_index.uniqueness != Neo4jConstants.UNIQUE:
                self.drop_index(obsolete_index)
        for missing_index in new_indexes.difference(old_indexes):
            self.create_index(missing_index)

    def get_constraints(
        self,
    ) -> List[Union[Neo4jConstraintExists, Neo4jConstraintUnique]]:
        """Returns a list of all database constraints (label and label-property types)."""
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

    def new_connection(self) -> Connection:
        """Creates new Neo4j connection."""
        args = dict(
            host=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            encrypted=self._encrypted,
            client_name=self._client_name,
        )
        return Neo4jConnection(**args)

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

        return result
