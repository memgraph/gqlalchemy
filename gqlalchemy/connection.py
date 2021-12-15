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

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator

import mgclient

from .models import Node, Path, Relationship

__all__ = ("Connection",)


class Connection(ABC):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        encrypted: bool,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.encrypted = encrypted

    @abstractmethod
    def execute(self, query: str) -> None:
        """Executes Cypher query without returning any results."""
        pass

    @abstractmethod
    def execute_and_fetch(self, query: str) -> Iterator[Dict[str, Any]]:
        """Executes Cypher query and returns iterator of results."""
        pass

    @abstractmethod
    def is_active(self) -> bool:
        """Returns True if connection is active and can be used"""
        pass

    @staticmethod
    def create(**kwargs) -> "Connection":
        """Creates an instance of a connection."""
        return MemgraphConnection(**kwargs)


class MemgraphConnection(Connection):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        encrypted: bool,
        lazy: bool = True,
    ):
        super().__init__(host, port, username, password, encrypted)
        self.lazy = lazy
        self._connection = self._create_connection()

    def execute(self, query: str) -> None:
        """Executes Cypher query without returning any results."""
        cursor = self._connection.cursor()
        cursor.execute(query)
        cursor.fetchall()

    def execute_and_fetch(self, query: str) -> Iterator[Dict[str, Any]]:
        """Executes Cypher query and returns iterator of results."""
        cursor = self._connection.cursor()
        cursor.execute(query)
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield {dsc.name: _convert_memgraph_value(row[index]) for index, dsc in enumerate(cursor.description)}

    def is_active(self) -> bool:
        """Returns True if connection is active and can be used"""
        return self._connection is not None and self._connection.status == mgclient.CONN_STATUS_READY

    def _create_connection(self) -> Connection:
        sslmode = mgclient.MG_SSLMODE_REQUIRE if self.encrypted else mgclient.MG_SSLMODE_DISABLE
        return mgclient.connect(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            sslmode=sslmode,
            lazy=self.lazy,
        )


def _convert_memgraph_value(value: Any) -> Any:
    """Converts Memgraph objects to custom Node/Relationship objects"""
    if isinstance(value, mgclient.Relationship):
        return Relationship.parse_obj(
            {
                "_type": value.type,
                "_id": value.id,
                "_relationship_type": value.type,
                "_start_node_id": value.start_id,
                "_end_node_id": value.end_id,
                **value.properties,
            }
        )

    if isinstance(value, mgclient.Node):
        return Node.parse_obj(
            {
                "_type": "".join(value.labels),
                "_id": value.id,
                "_node_labels": set(value.labels),
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
