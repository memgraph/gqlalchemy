from gqlalchemy import Node, Field
from typing import Optional


def test_multiple_inheritance(memgraph):
    class User(Node):
        name: str = Field(index=True, exists=True, unique=True, db=memgraph)

    class Streamer(User):
        id: str = Field(index=True, exists=True, unique=True, db=memgraph)
        followers: Optional[int] = Field()

    user = User(name="Kate").save(memgraph)
    streamer = Streamer(id=7, name="Ivan", followers=172).save(memgraph)

    assert "name" in Streamer.__fields__
    assert user.name == "Kate"
    assert streamer.name == "Ivan"
    assert streamer.followers == 172
    assert User.labels == {"User"}
    assert Streamer.labels == {"Streamer", "User"}
    assert user._labels == {"User"}
    assert streamer._labels == {"Streamer", "User"}
