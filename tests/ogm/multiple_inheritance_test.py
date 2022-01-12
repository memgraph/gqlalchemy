from gqlalchemy import Memgraph, Node, Relationship, Field
from typing import Optional


db = Memgraph()

class User(Node):
    name: Optional[str] = Field(index=True, unique=True, db=db)


class Streamer(Node, _node_labels={"User", "Streamer"}):
    id: Optional[str] = Field(index=True, unique=True, db=db)
    name: Optional[str] = Field(index=True, unique=True, db=db, label="User")

def test_multiple_inheritance():
    user = User(name="Ivan").save(db)
    streamer = Streamer(id=7, name="Pero").save(db)
    print(Node._subtypes_)
    assert False
