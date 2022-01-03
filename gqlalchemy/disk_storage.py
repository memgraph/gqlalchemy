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
    def __init__(self, database: str):
        pass

    def execute_query(query) -> List[Any]:
        with contextlib.closing(sqlite3.connect(self.database_name)) as conn:
            with conn:  # autocommit changes
                with contextlib.closing(conn.cursor()) as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()

    def create_node_property_table():
        # node_id, property_name, property_value
        pass

    def create_relationship_property_table():
        # relationship_id, property_name, property_value
        pass

    def save_node_property(node_id: int, name: str, value: Any):
        self.execute_query("SELECT ")
        pass

    def load_node_property(node_id: int, name: str, value: Any):
        pass

    def save_relationship_property(relationship_id: int, name: str, value: Any):
        pass

    def load_relationship_property(relationship_id: int, name: str, value: Any):
        pass
