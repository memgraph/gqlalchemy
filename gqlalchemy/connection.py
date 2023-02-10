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
from typing import Any, Dict, Iterator, Optional

import mgclient
from neo4j import GraphDatabase
from neo4j.graph import Node as Neo4jNode
from neo4j.graph import Path as Neo4jPath
from neo4j.graph import Relationship as Neo4jRelationship

from gqlalchemy.exceptions import database_error_handler, connection_handler
from gqlalchemy.models import Node, Path, Relationship

__all__ = ("Connection",)


class Connection(ABC):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        encrypted: bool,
        client_name: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.encrypted = encrypted
        self.client_name = client_name

    @abstractmethod
    def execute(self, query: str, parameters: Dict[str, Any] = {}) -> None:
        """Executes Cypher query without returning any results."""
        pass

    @abstractmethod
    def execute_and_fetch(self, query: str, parameters: Dict[str, Any] = {}) -> Iterator[Dict[str, Any]]:
        """Executes Cypher query and returns iterator of results."""
        pass

    @abstractmethod
    def is_active(self) -> bool:
        """Returns True if connection is active and can be used."""
        pass


class MemgraphConnection(Connection):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        encrypted: bool,
        client_name: Optional[str] = None,
        lazy: bool = False,
    ):
        super().__init__(
            host=host, port=port, username=username, password=password, encrypted=encrypted, client_name=client_name
        )
        self.lazy = lazy
        self._connection = self._create_connection()

    @database_error_handler
    def execute(self, query: str, parameters: Dict[str, Any] = {}) -> None:
        """Executes Cypher query without returning any results."""
        cursor = self._connection.cursor()
        cursor.execute(query, parameters)
        cursor.fetchall()

    @database_error_handler
    def execute_and_fetch(self, query: str, parameters: Dict[str, Any] = {}) -> Iterator[Dict[str, Any]]:
        """Executes Cypher query and returns iterator of results."""
        cursor = self._connection.cursor()
        cursor.execute(query, parameters)
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield {dsc.name: _convert_memgraph_value(row[index]) for index, dsc in enumerate(cursor.description)}

    def is_active(self) -> bool:
        """Returns True if connection is active and can be used."""
        return self._connection is not None and self._connection.status == mgclient.CONN_STATUS_READY

    @connection_handler
    def _create_connection(self) -> Connection:
        """Creates and returns a connection with Memgraph."""
        sslmode = mgclient.MG_SSLMODE_REQUIRE if self.encrypted else mgclient.MG_SSLMODE_DISABLE
        connection = mgclient.connect(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            sslmode=sslmode,
            lazy=self.lazy,
            client_name=self.client_name,
        )
        connection.autocommit = True
        return connection


def _convert_memgraph_value(value: Any) -> Any:
    """Converts Memgraph objects to custom Node/Relationship objects."""
    if isinstance(value, mgclient.Relationship):
        return Relationship.parse_obj(
            {
                "_type": value.type,
                "_id": value.id,
                "_start_node_id": value.start_id,
                "_end_node_id": value.end_id,
                **value.properties,
            }
        )

    if isinstance(value, mgclient.Node):
        return Node.parse_obj(
            {
                "_id": value.id,
                "_labels": set(value.labels),
                **value.properties,
            }
        )

    if isinstance(value, mgclient.Path):
        return Path.parse_obj(
            {
                "_nodes": list([_convert_memgraph_value(node) for node in value.nodes]),
                "_relationships": list([_convert_memgraph_value(rel) for rel in value.relationships]),
            }
        )

    return value


class Neo4jConnection(Connection):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        encrypted: bool,
        client_name: Optional[str] = None,
        lazy: bool = True,
    ):
        super().__init__(
            host=host, port=port, username=username, password=password, encrypted=encrypted, client_name=client_name
        )
        self.lazy = lazy
        self._connection = self._create_connection()

    def execute(self, query: str, parameters: Dict[str, Any] = {}) -> None:
        """Executes Cypher query without returning any results."""
        with self._connection.session() as session:
            session.run(query, parameters)

    def execute_and_fetch(self, query: str, parameters: Dict[str, Any] = {}) -> Iterator[Dict[str, Any]]:
        """Executes Cypher query and returns iterator of results."""
        with self._connection.session() as session:
            results = session.run(query, parameters)
            columns = results.keys()
            for result in results:
                yield {column: _convert_neo4j_value(result[column]) for column in columns}

    def is_active(self) -> bool:
        """Returns True if connection is active and can be used."""
        return self._connection is not None

    def _create_connection(self):
        return GraphDatabase.driver(
            f"bolt://{self.host}:{self.port}", auth=(self.username, self.password), encrypted=self.encrypted
        )


def _convert_neo4j_value(value: Any) -> Any:
    """Converts Neo4j objects to custom Node/Relationship objects."""
    if isinstance(value, Neo4jRelationship):
        return Relationship.parse_obj(
            {
                "_type": value.type,
                "_id": value.id,
                "_start_node_id": value.start_node.id,
                "_end_node_id": value.end_node.id,
                **dict(value.items()),
            }
        )

    if isinstance(value, Neo4jNode):
        return Node.parse_obj(
            {
                "_id": value.id,
                "_labels": set(value.labels),
                **dict(value.items()),
            }
        )

    if isinstance(value, Neo4jPath):
        return Path.parse_obj(
            {
                "_nodes": list([_convert_neo4j_value(node) for node in value.nodes]),
                "_relationships": list([_convert_neo4j_value(rel) for rel in value.relationships]),
            }
        )

    return value
