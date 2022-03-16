from gqlalchemy import Node, Field
from typing import Optional


def test_node(memgraph):
    class User(Node):
        id: int = Field(index=True, exists=True, unique=True, db=memgraph)
        name: str = Field(index=True, exists=True, unique=True, db=memgraph)

    user = User(id=0, name="Kate").save(memgraph)

    assert User.label == "User"
    assert User.labels == {"User"}

    assert "id" in User.__fields__
    assert "name" in User.__fields__

    assert user.id == 0
    assert user.name == "Kate"


def test_node_inheritance(memgraph):
    class User(Node):
        id: int = Field(index=True, exists=True, unique=True, db=memgraph)
        name: str = Field(index=True, exists=True, unique=True, db=memgraph)

    class Admin(User):
        admin_id: int = Field(index=True, exists=True, unique=True, db=memgraph)

    user = User(id=0, name="Kate").save(memgraph)
    admin = Admin(id=1, admin_id=0, name="Admin").save(memgraph)

    assert User.label == "User"
    assert User.labels == {"User"}

    assert "id" in User.__fields__
    assert "name" in User.__fields__

    assert user.id == 0
    assert user.name == "Kate"

    assert Admin.label == "Admin"
    assert Admin.labels == {"Admin", "User"}

    assert "id" in Admin.__fields__
    assert "admin_id" in Admin.__fields__
    assert "name" in Admin.__fields__

    assert admin.id == 1
    assert admin.admin_id == 0
    assert admin.name == "Admin"
    assert admin.label == "Admin"
    assert admin.labels == {"Admin", "User"}
    assert admin._label == "Admin:User"
    assert admin._labels == {"Admin", "User"}


def test_node_custom_label(memgraph):
    class User(Node, label="UserX"):
        id: int = Field(index=True, exists=True, unique=True, db=memgraph)
        name: str = Field(index=True, exists=True, unique=True, db=memgraph)

    class Admin(User, label="AdminX"):
        admin_id: int = Field(index=True, exists=True, unique=True, db=memgraph)

    user = User(id=0, name="Kate").save(memgraph)
    admin = Admin(id=1, admin_id=0, name="Admin").save(memgraph)

    assert User.label == "UserX"
    assert User.labels == {"UserX"}

    assert user.label == "UserX"
    assert user.labels == {"UserX"}
    assert user._label == "UserX"
    assert user._labels == {"UserX"}

    assert Admin.label == "AdminX"
    assert Admin.labels == {"AdminX", "UserX"}

    assert admin.label == "AdminX"
    assert admin.labels == {"AdminX", "UserX"}
    assert admin._label == "AdminX:UserX"
    assert admin._labels == {"AdminX", "UserX"}


def test_node_custom_labels(memgraph):
    class User(Node, labels={"UserX", "UserY"}):
        id: int = Field(index=True, exists=True, unique=True, db=memgraph)
        name: str = Field(index=True, exists=True, unique=True, db=memgraph)

    class Admin(User, label="AdminX", labels={"AdminX", "AdminY"}):
        admin_id: int = Field(index=True, exists=True, unique=True, db=memgraph)

    admin = Admin(id=1, admin_id=0, name="Admin").save(memgraph)

    assert User.label == "User"
    assert User.labels == {"User", "UserX", "UserY"}

    assert Admin.label == "AdminX"
    assert Admin.labels == {"AdminX", "AdminY", "User", "UserX", "UserY"}

    assert admin.label == "AdminX"
    assert admin.labels == {"AdminX", "AdminY", "User", "UserX", "UserY"}
    assert admin._label == "AdminX:AdminY:User:UserX:UserY"
    assert admin._labels == {"AdminX", "AdminY", "User", "UserX", "UserY"}


def test_node_various_inheritance(memgraph):
    class User(Node):
        name: str = Field(index=True, exists=True, unique=True, db=memgraph)

    class UserOne(Node, label="User1"):
        name: str = Field(index=True, exists=True, unique=True, db=memgraph)

    class UserTwo(User, label="User2", labels={"User3"}):
        name: str = Field(index=True, exists=True, unique=True, db=memgraph)

    class Streamer(User):
        id: str = Field(index=True, exists=True, unique=True, db=memgraph)
        followers: Optional[int] = Field()

    class StreamerOne(User, label="Streamer1"):
        id: str = Field(index=True, exists=True, unique=True, db=memgraph)
        followers: Optional[int] = Field()

    class StreamerTwo(Streamer, label="Streamer2", labels={"Streamer3", "Streamer4"}):
        id: str = Field(index=True, exists=True, unique=True, db=memgraph)
        followers: Optional[int] = Field()

    user = User(name="Kate").save(memgraph)
    userOne = UserOne(name="Mrma").save(memgraph)
    userTwo = UserTwo(name="Boris").save(memgraph)
    streamer = Streamer(id=7, name="Ivan", followers=172).save(memgraph)
    streamerOne = StreamerOne(id=8, name="Bruno", followers=173).save(memgraph)
    streamerTwo = StreamerTwo(id=9, name="Marko", followers=174).save(memgraph)

    assert "name" in Streamer.__fields__
    assert user.name == "Kate"
    assert streamer.name == "Ivan"
    assert streamer.followers == 172

    assert User.label == "User"
    assert User.labels == {"User"}

    assert UserOne.label == "User1"
    assert UserOne.labels == {"User1"}

    assert UserTwo.label == "User2"
    assert UserTwo.labels == {"User", "User2", "User3"}

    assert user.label == "User"
    assert user.labels == {"User"}
    assert user._label == "User"
    assert user._labels == {"User"}

    assert userOne.label == "User1"
    assert userOne.labels == {"User1"}
    assert userOne._label == "User1"
    assert userOne._labels == {"User1"}

    assert userTwo.label == "User2"
    assert userTwo.labels == {"User", "User2", "User3"}
    assert userTwo._label == "User:User2:User3"
    assert userTwo._labels == {"User", "User2", "User3"}

    assert Streamer.label == "Streamer"
    assert Streamer.labels == {"Streamer", "User"}

    assert StreamerOne.label == "Streamer1"
    assert StreamerOne.labels == {"Streamer1", "User"}

    assert StreamerTwo.label == "Streamer2"
    assert StreamerTwo.labels == {"User", "Streamer", "Streamer2", "Streamer3", "Streamer4"}

    assert streamer.label == "Streamer"
    assert streamer.labels == {"Streamer", "User"}
    assert streamer._label == "Streamer:User"
    assert streamer._labels == {"Streamer", "User"}

    assert streamerOne.label == "Streamer1"
    assert streamerOne.labels == {"Streamer1", "User"}
    assert streamerOne._label == "Streamer1:User"
    assert streamerOne._labels == {"Streamer1", "User"}

    assert streamerTwo.label == "Streamer2"
    assert streamerTwo.labels == {"User", "Streamer", "Streamer2", "Streamer3", "Streamer4"}
    assert streamerTwo._label == "Streamer:Streamer2:Streamer3:Streamer4:User"
    assert streamerTwo._labels == {
        "User",
        "Streamer",
        "Streamer2",
        "Streamer3",
        "Streamer4",
    }


def test_node_multiple_inheritence(memgraph):
    class User(Node, labels={"UserX"}):
        id: int = Field(index=True, exists=True, unique=True, db=memgraph)
        name: str = Field(index=True, exists=True, unique=True, db=memgraph)

    class UserOne(Node, labels={"UserOneX"}):
        pass

    class UserTwo(Node, label="UserTwoX"):
        pass

    class Admin(UserOne, UserTwo, User, label="AdminX", labels={"AdminX", "AdminY"}):
        admin_id: int = Field(index=True, exists=True, unique=True, db=memgraph)

    admin = Admin(id=1, admin_id=0, name="Admin").save(memgraph)

    assert UserOne.label == "UserOne"
    assert UserTwo.label == "UserTwoX"

    assert Admin.label == "AdminX"
    assert Admin.labels == {"AdminX", "AdminY", "User", "UserX", "UserOne", "UserOneX", "UserTwoX"}

    assert admin.label == "AdminX"
    assert admin.labels == {"AdminX", "AdminY", "User", "UserX", "UserOne", "UserOneX", "UserTwoX"}
    assert admin._label == "AdminX:AdminY:User:UserOne:UserOneX:UserTwoX:UserX"
    assert admin._labels == {"AdminX", "AdminY", "User", "UserX", "UserOne", "UserOneX", "UserTwoX"}
