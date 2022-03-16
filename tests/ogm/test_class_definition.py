from gqlalchemy import Node, Field
from typing import Optional


def test_multiple_inheritance(memgraph):
    class User(Node):
        name: str = Field(index=True, exists=True, unique=True, db=memgraph)

    class UserOne(Node, label="User1"):
        name: str = Field(index=True, exists=True, unique=True, db=memgraph)

    class UserTwo(Node, labels={"User2"}):
        name: str = Field(index=True, exists=True, unique=True, db=memgraph)

    class Streamer(User):
        id: str = Field(index=True, exists=True, unique=True, db=memgraph)
        followers: Optional[int] = Field()

    class StreamerOne(User, label="Streamer1"):
        id: str = Field(index=True, exists=True, unique=True, db=memgraph)
        followers: Optional[int] = Field()

    class StreamerTwo(User, labels={"Streamer2"}):
        id: str = Field(index=True, exists=True, unique=True, db=memgraph)
        followers: Optional[int] = Field()

    user = User(name="Kate").save(memgraph)
    userOne = UserOne(name="Mrma").save(memgraph)
    userTwo = UserTwo(name="Boris").save(memgraph)
    streamer = Streamer(id=7, name="Ivan", followers=172).save(memgraph)
    streamerOne = StreamerOne(id=7, name="Bruno", followers=173).save(memgraph)
    streamerTwo = StreamerTwo(id=7, name="Marko", followers=174).save(memgraph)

    assert "name" in Streamer.__fields__
    assert user.name == "Kate"
    assert streamer.name == "Ivan"
    assert streamer.followers == 172

    assert User.label == "User"
    assert User.labels == {"User"}

    assert UserOne.label == "User1"
    assert UserOne.labels == {"User1"}

    assert UserTwo.label == "UserTwo" # TODO: Main label should be Streamer2
    assert UserTwo.labels == {"User2"}

    assert user.label == "User"
    assert user.labels == {"User"}
    assert user._label == "User"
    assert user._labels == {"User"}

    assert userOne.label == "User1"
    assert userOne.labels == {"User1"}
    assert userOne._label == "User1"
    assert userOne._labels == {"User1"}

    assert userTwo.label == "UserTwo" # TODO: Main label should be User2
    assert userTwo.labels == {"User2"}
    assert userTwo._label == "User2"
    assert userTwo._labels == {"User2"}

    assert Streamer.label == "Streamer"
    assert Streamer.labels == {"Streamer", "User"}

    assert StreamerOne.label == "Streamer1"
    assert StreamerOne.labels == {"Streamer1", "User"}

    assert StreamerTwo.label == "StreamerTwo"
    assert StreamerTwo.labels == {"Streamer2"} # TODO: Missing User label

    assert streamer.label == "Streamer"
    assert streamer.labels == {"Streamer", "User"}
    assert streamer._label == "Streamer:User"
    assert streamer._labels == {"Streamer", "User"}

    assert streamerOne.label == "Streamer1"
    assert streamerOne.labels == {"Streamer1", "User"}
    assert streamerOne._label == "Streamer1:User"
    assert streamerOne._labels == {"Streamer1", "User"}

    assert streamerTwo.label == "StreamerTwo" # TODO: Main label should be Streamer2
    assert streamerTwo.labels == {"Streamer2"} # TODO: Missing label User
    assert streamerTwo._label == "Streamer2" # TODO: Missing label User
    assert streamerTwo._labels == {"Streamer2"} # TODO: Missing label User
