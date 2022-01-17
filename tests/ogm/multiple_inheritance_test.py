from gqlalchemy import Memgraph, Node, Relationship, Field
from typing import Optional


db = Memgraph()


class User(Node):
    name: Optional[str] = Field(index=True, unique=True, db=db)


class Streamer(User):
    id: Optional[str] = Field(index=True, unique=True, db=db)
    name: Optional[str] = Field(index=True, unique=True, db=db, label="User")


class Speaks(Relationship, type="SPEAKS"):
    pass


def test_multiple_inheritance():
    user = User(name="Ivan").save(db)
    streamer = Streamer(id=7, name="Pero").save(db)
    assert User.labels == {"User"}
    assert Streamer.labels == {"Streamer", "User"}
    assert user._labels == {"User"}
    assert streamer._labels == {"Streamer", "User"}
