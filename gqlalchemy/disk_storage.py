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

import sqlite3
import contextlib

from typing import List


class OnDiskPropertyDatabase:
    def save_node_property(self, node_id: int, property_name: str, property_value: str):
        pass

    def load_node_property(self, node_id: int, property_name: str, property_value: str):
        pass

    def save_relationship_property(self, relationship_id: int, property_name: str, property_value: str):
        pass

    def load_relationship_property(self, relationship_id: int, property_name: str, property_value: str):
        pass


class SqliteDatabase(OnDiskPropertyDatabase):
    def __init__(self, database_name: str = "on_disk_properties.db"):
        self.database_name = database_name
        self.create_node_property_table()
        self.create_relationship_property_table()

    def execute_query(self, query) -> List[str]:
        with contextlib.closing(sqlite3.connect(self.database_name)) as conn:
            with conn:  # autocommit changes
                with contextlib.closing(conn.cursor()) as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()

    def create_node_property_table(self):
        self.execute_query(
            "CREATE TABLE IF NOT EXISTS node_properties ("
            "node_id integer PRIMARY KEY,"
            "property_name text NOT NULL,"
            "property_value text NOT NULL,"
            ");"
        )

    def create_relationship_property_table(self):
        self.execute_query(
            "CREATE TABLE IF NOT EXISTS relationship_properties ("
            "relationship_id integer PRIMARY KEY,"
            "property_name text NOT NULL,"
            "property_value text NOT NULL,"
            ");"
        )

    def save_node_property(self, node_id: int, property_name: str, property_value: str):
        self.execute_query(
            "MERGE INTO node_properties WITH (HOLDLOCK) "
            f"USING node_properties ON (node_id = {node_id})"
            " WHEN MATCHED THEN UPDATE"
            f"  SET property_name = {property_name},"
            "    property_value = {property_value}"
            " WHEN NOT MATCHED THEN INSERT"
            "  (node_id, property_name, property_value)"
            f"  VALUES ({node_id}, {property_name}, {property_value})"
        )

    def load_node_property(self, node_id: int, property_name: str, property_value: str):
        return self.execute_query(
            "SELECT property_value "
            "FROM node_properties AS db "
            f"WHERE db.node_id = {node_id} "
            " AND db.property_name = {property_name}"
        )

    def save_relationship_property(self, relationship_id: int, property_name: str, property_value: str):
        self.execute_query(
            "MERGE INTO relationship_properties WITH (HOLDLOCK) "
            f"USING relationship_properties "
            "  ON (relationship_id = {relationship_id})"
            " WHEN MATCHED THEN UPDATE"
            f"  SET property_name = {property_name},"
            "    property_value = {property_value}"
            " WHEN NOT MATCHED THEN INSERT"
            "  (relationship_id, property_name, property_value)"
            f"  VALUES ({relationship_id}, {property_name}, {property_value})"
        )

    def load_relationship_property(self, relationship_id: int, property_name: str, property_value: str):
        return self.execute_query(
            "SELECT property_value "
            "FROM relationship_properties AS db "
            f"WHERE db.relationship_id = {relationship_id} "
            f"AND db.property_name = {property_name}"
        )
