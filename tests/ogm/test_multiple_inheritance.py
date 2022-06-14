from typing import Optional

from gqlalchemy import Node, Field


def test_multiple_inheritance(memgraph):
    class User(Node):
        name: Optional[str] = Field(index=True, unique=True, db=memgraph)

    class Streamer(User):
        id: Optional[str] = Field(index=True, unique=True, db=memgraph)
        name: Optional[str] = Field(index=True, unique=True, db=memgraph, label="User")

    user = User(name="Ivan").save(memgraph)
    streamer = Streamer(id=7, name="Pero").save(memgraph)
    assert User.labels == {"User"}
    assert Streamer.labels == {"Streamer", "User"}
    assert user._labels == {"User"}
    assert streamer._labels == {"Streamer", "User"}
