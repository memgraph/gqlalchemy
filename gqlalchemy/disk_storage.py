import sqlite3
from typing import Any


class OnDiskPropertyDatabase:
    def saveNodeProperty(node_id: int, name: str, value: Any):
        pass

    def loadNodeProperty(node_id: int, name: str, value: Any):
        pass

    def saveRelationshipProperty(relationship_id: int, name: str, value: Any):
        pass

    def loadRelationshipProperty(relationship_id: int, name: str, value: Any):
        pass


class SqliteDatabase(OnDiskDatabase):
    def __init__(self, database: str):
        pass

    def saveNodeProperty(node_id: int, name: str, value: Any):
        pass

    def loadNodeProperty(node_id: int, name: str, value: Any):
        pass

    def saveRelationshipProperty(relationship_id: int, name: str, value: Any):
        pass

    def loadRelationshipProperty(relationship_id: int, name: str, value: Any):
        pass
