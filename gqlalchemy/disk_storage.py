import sqlite3
import contextlib

from typing import Any, List


class OnDiskPropertyDatabase:
    def save_node_property(node_id: int, name: str, value: Any):
        self.execute_query("SELECT ")
        pass

    def load_node_property(node_id: int, name: str, value: Any):
        pass

    def save_relationship_property(relationship_id: int, name: str, value: Any):
        pass

    def load_relationship_property(relationship_id: int, name: str, value: Any):
        pass


class SqliteDatabase(OnDiskDatabase):
    def __init__(self, database_name: str = "on_disk_properties.db"):
        self.database_name = database_name

    def execute_query(query) -> List[Any]:
        with contextlib.closing(sqlite3.connect(self.database_name)) as conn:
            with conn:  # autocommit changes
                with contextlib.closing(conn.cursor()) as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()

    def create_node_property_table():
        self.execute_query(
            "CREATE TABLE IF NOT EXISTS node_properties ("
            "node_id integer PRIMARY KEY,"
            "property_name text NOT NULL,"
            "property_value text NOT NULL,"
            ");"
        )

    def create_relationship_property_table():
        self.execute_query(
            "CREATE TABLE IF NOT EXISTS relationship_properties ("
            "relationship_id integer PRIMARY KEY,"
            "property_name text NOT NULL,"
            "property_value text NOT NULL,"
            ");"
        )

    def save_node_property(node_id: int, name: str, value: Any):
        self.execute_query(
            "MERGE INTO node_properties WITH (HOLDLOCK) "
            f"USING node_properties ON (node_id = {node_id})"
            " WHEN MATCHED THEN UPDATE"
            f"  SET property_name = {name}, property_value = {value}"
            " WHEN NOT MATCHED THEN INSERT"
            "  (node_id, property_name, property_value)"
            f"  VALUES ({node_id}, {name}, {value})"
        )

    def load_node_property(node_id: int, name: str, value: Any):
        return self.execute_query(
            "SELECT property_value "
            "FROM node_properties AS db "
            f"WHERE db.node_id = {node_id} AND db.property_name = {name}"
        )

    def save_relationship_property(relationship_id: int, name: str, value: Any):
        self.execute_query(
            "MERGE INTO relationship_properties WITH (HOLDLOCK) "
            f"USING relationship_properties "
            "  ON (relationship_id = {relationship_id})"
            " WHEN MATCHED THEN UPDATE"
            f"  SET property_name = {name}, property_value = {value}"
            " WHEN NOT MATCHED THEN INSERT"
            "  (relationship_id, property_name, property_value)"
            f"  VALUES ({relationship_id}, {name}, {value})"
        )

    def load_relationship_property(relationship_id: int, name: str, value: Any):
        return self.execute_query(
            "SELECT property_value "
            "FROM relationship_properties AS db "
            f"WHERE db.relationship_id = {relationship_id} "
            f"AND db.property_name = {name}"
        )
