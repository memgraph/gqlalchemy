from gqlalchemy import Node, Field, Memgraph


memgraph = Memgraph()


class User(Node):
    name: str = Field(index=True, exists=True, unique=True, db=memgraph)


class Streamer(User):
    name: str = Field(index=True, unique=True, db=memgraph)
    id: str = Field(index=True, unique=True, db=memgraph)
    followers: int = Field()
    totalViewCount: int = Field()


def test_load_node():
    streamer = Streamer(name="Mislav", id="7", followers=777, totalViewCount=7777).save(memgraph)  # noqa F401
    loaded_streamer = memgraph.load_node(Node(id="7", _label="Stream"))
    assert loaded_streamer.name == "Mislav"
    assert loaded_streamer.id == "7"
    assert loaded_streamer.followers == 777
    assert loaded_streamer.totalViewCount == 7777
    assert loaded_streamer._labels == {"Streamer", "User"}
