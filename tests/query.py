from collections.abc import Iterator
from typing import Any, Dict

from memgraph_pymgogm import Memgraph


def query(command: str) -> Iterator[Dict[str, Any]]:
    """Queries Memgraph database and returns iterator of results"""
    db = Memgraph()
    yield from db.execute_and_fetch(command)
