import pytest
from gqlalchemy import Memgraph, Node, Field
from typing import Optional


db = Memgraph()


class User(Node):
    name: str = Field(index=True, exists=True, unique=True, db=db)


class Stream(User):
    id: str = Field(index=True, exists=True, unique=True, db=db)
    followers: Optional[int] = Field()


@pytest.fixture
def cleanup_class():
    yield
    del User  # noqa F821


@pytest.mark.usefixtures("cleanup_class")
def test_multiple_inheritance(memgraph):
    user = User(name="Kate").save(memgraph)
    streamer = Stream(id=7, name="Ivan", followers=172).save(memgraph)
    assert "name" in Stream.__fields__
    assert user.name == "Kate"
    assert streamer.name == "Ivan"
    assert streamer.followers == 172
    assert User.labels == {"User"}
    assert Stream.labels == {"Streamer", "User"}
    assert user._labels == {"User"}
    assert streamer._labels == {"Streamer", "User"}
    assert "name" in Stream.__fields__
