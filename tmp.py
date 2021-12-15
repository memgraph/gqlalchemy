from gqlalchemy import Memgraph, Node
from pydantic import Field
from typing import Optional


class Person(Node):
    whatever: Optional[str] = Field(unique=True, index=True, db=Memgraph())


person = Person()
