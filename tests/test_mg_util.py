
from typing import Any, Dict, Iterator
from gqlalchemy.mg_util import MemgraphInstance

import pytest

from gqlalchemy import Memgraph, Node


def test_start_memgraph():
    instance = MemgraphInstance()
    db = instance.start_with_docker()

    print(db.execute_and_fetch("RETURN 100"))
