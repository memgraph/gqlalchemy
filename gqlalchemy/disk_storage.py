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

import sqlite3
import contextlib
from abc import ABC
from typing import Optional, List


class OnDiskPropertyDatabase(ABC):
    """An abstract class for implementing on-disk storage features with specific databases."""

    def save_node_property(self, node_id: int, property_name: str, property_value: str) -> None:
        """Saves a node property to an on disk database."""
        pass

    def load_node_property(self, node_id: int, property_name: str, property_value: str) -> Optional[str]:
        """Loads a node property from an on disk database."""
        pass

    def delete_node_property(self, node_id: int, property_name: str, property_value: str) -> None:
        """Deletes a node property from an on disk database."""
        pass

    def save_relationship_property(self, relationship_id: int, property_name: str, property_value: str) -> None:
        """Saves a relationship property to an on disk database."""
        pass

    def load_relationship_property(
        self, relationship_id: int, property_name: str, property_value: str
    ) -> Optional[str]:
        """Loads a relationship property from an on disk database."""
        pass

    def delete_relationship_property(self, node_id: int, property_name: str, property_value: str) -> None:
        """Deletes a node property from an on disk database."""
        pass

    def drop_database(self) -> None:
        """Deletes all entries from the on disk database."""
        pass


class SQLitePropertyDatabase(OnDiskPropertyDatabase):
    def __init__(self, database_path: str, memgraph: "Memgraph" = None):  # noqa F821
        self.database_name = database_path
        self._create_node_property_table()
        self._create_relationship_property_table()
        if memgraph is not None:
            memgraph.init_disk_storage(self)

    def execute_query(self, query: str) -> List[str]:
        """Executes an SQL query on the on disk property database.

        Args:
            query: A string representing an SQL query.

        Returns:
            A list of strings representing the results of the query.
        """
        with contextlib.closing(sqlite3.connect(self.database_name)) as conn:
            with conn:  # autocommit changes
                with contextlib.closing(conn.cursor()) as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()

    def _create_node_property_table(self) -> None:
        """Creates a node property SQL table."""
        self.execute_query(
            "CREATE TABLE IF NOT EXISTS node_properties ("
            "node_id integer NOT NULL,"
            "property_name text NOT NULL,"
            "property_value text NOT NULL,"
            "PRIMARY KEY (node_id, property_name)"
            ");"
        )

    def _create_relationship_property_table(self) -> None:
        """Creates a relationship property SQL table."""
        self.execute_query(
            "CREATE TABLE IF NOT EXISTS relationship_properties ("
            "relationship_id integer NOT NULL,"
            "property_name text NOT NULL,"
            "property_value text NOT NULL,"
            "PRIMARY KEY (relationship_id, property_name)"
            ");"
        )

    def drop_database(self) -> None:
        """Deletes all properties in the database."""
        self.execute_query("DELETE FROM node_properties;")
        self.execute_query("DELETE FROM relationship_properties;")

    def save_node_property(self, node_id: int, property_name: str, property_value: str) -> None:
        """Saves a node property to an on disk database.

        Args:
            node_id: An integer representing the internal id of the node.
            property_name: A string representing the name of the property.
            property_value: A string representing the value of the property.
        """
        self.execute_query(
            "INSERT INTO node_properties (node_id, property_name, property_value) "
            f"VALUES({node_id}, '{property_name}', '{property_value}') "
            "ON CONFLICT(node_id, property_name) "
            "DO UPDATE SET property_value=excluded.property_value;"
        )

    def load_node_property(self, node_id: int, property_name: str) -> Optional[str]:
        """Loads a node property from an on disk database.

        Args:
            node_id: An integer representing the internal id of the node.
            property_name: A string representing the name of the property.

        Returns:
            An optional string representing the property value.
        """
        result = self.execute_query(
            "SELECT property_value "
            "FROM node_properties AS db "
            f"WHERE db.node_id = {node_id} "
            f"AND db.property_name = '{property_name}'"
        )

        if len(result) == 0:
            return None

        # primary key is unique
        assert len(result) == 1 and len(result[0]) == 1

        return result[0][0]

    def delete_node_property(self, node_id: int, property_name: str) -> None:
        """Deletes a node property from an on disk database.

        Args:
            node_id: An integer representing the internal id of the node.
            property_name: A string representing the name of the property.
        """
        self.execute_query(
            "DELETE "
            "FROM node_properties AS db "
            f"WHERE db.node_id = {node_id} "
            f"AND db.property_name = '{property_name}'"
        )

    def save_relationship_property(self, relationship_id: int, property_name: str, property_value: str) -> None:
        """Saves a relationship property to an on disk database.

        Args:
            relationship_id: An integer representing the internal id of the relationship.
            property_name: A string representing the name of the property.
            property_value: A string representing the value of the property.
        """
        self.execute_query(
            "INSERT INTO relationship_properties (relationship_id, property_name, property_value) "
            f"VALUES({relationship_id}, '{property_name}', '{property_value}') "
            "ON CONFLICT(relationship_id, property_name) "
            "DO UPDATE SET property_value=excluded.property_value;"
        )

    def load_relationship_property(self, relationship_id: int, property_name: str) -> Optional[str]:
        """Loads a relationship property from an on disk database.

        Args:
            relationship_id: An integer representing the internal id of the relationship.
            property_name: A string representing the name of the property.

        Returns:
            An optional string representing the property value.
        """
        result = self.execute_query(
            "SELECT property_value "
            "FROM relationship_properties AS db "
            f"WHERE db.relationship_id = {relationship_id} "
            f"AND db.property_name = '{property_name}'"
        )

        if len(result) == 0:
            return None

        # primary key is unique
        assert len(result) == 1 and len(result[0]) == 1

        return result[0][0]

    def delete_relationship_property(self, relationship_id: int, property_name: str) -> None:
        """Deletes a node property from an on disk database.

        Args:
            relationship_id: An integer representing the internal id of the relationship.
            property_name: A string representing the name of the property.
        """
        self.execute_query(
            "DELETE "
            "FROM relationship_properties AS db "
            f"WHERE db.relationship_id = {relationship_id} "
            f"AND db.property_name = '{property_name}'"
        )
