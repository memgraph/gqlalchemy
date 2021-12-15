from gqlalchemy import Memgraph, Node, Property
from pydantic import Field
from typing import Optional

class Person(Node):
    _node_labels: set[str] = {"Person"}
    whatever: Optional[str] = Field(unique=True, db=Memgraph())

person = Person()
# print(person.__fields__["whatever"].field_info.extra)
# db = Memgraph()
