# Copyright (c) 2016-2022 Memgraph Ltd. [https://memgraph.com]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pytest
from typing import Optional

from gqlalchemy import Node, Field


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_node(database):
    class User(Node):
        id: int = Field(index=True, db=database)
        name: str = Field(unique=True, db=database)

    user = User(id=0, name="Kate").save(database)

    assert User.label == "User"
    assert User.labels == {"User"}

    assert "id" in User.__fields__
    assert "name" in User.__fields__

    assert user.id == 0
    assert user.name == "Kate"


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_node_inheritance(database):
    class User(Node):
        id: int = Field(index=True, db=database)
        name: str = Field(unique=True, db=database)

    class Admin(User):
        admin_id: int = Field(index=True, db=database)

    user = User(id=0, name="Kate").save(database)
    admin = Admin(id=1, admin_id=0, name="Admin").save(database)

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


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_node_custom_label(database):
    class User(Node, label="UserX"):
        id: int = Field(index=True, db=database)
        name: str = Field(unique=True, db=database)

    class Admin(User, label="AdminX"):
        admin_id: int = Field(index=True, db=database)

    user = User(id=0, name="Kate").save(database)
    admin = Admin(id=1, admin_id=0, name="Admin").save(database)

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


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_node_custom_labels(database):
    class User(Node, labels={"UserX", "UserY"}):
        id: int = Field(index=True, db=database)
        name: str = Field(unique=True, db=database)

    class Admin(User, label="AdminX", labels={"AdminX", "AdminY"}):
        admin_id: int = Field(index=True, db=database)

    admin = Admin(id=1, admin_id=0, name="Admin").save(database)

    assert User.label == "User"
    assert User.labels == {"User", "UserX", "UserY"}

    assert Admin.label == "AdminX"
    assert Admin.labels == {"AdminX", "AdminY", "User", "UserX", "UserY"}

    assert admin.label == "AdminX"
    assert admin.labels == {"AdminX", "AdminY", "User", "UserX", "UserY"}
    assert admin._label == "AdminX:AdminY:User:UserX:UserY"
    assert admin._labels == {"AdminX", "AdminY", "User", "UserX", "UserY"}


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_node_various_inheritance(database):
    class User(Node):
        name: str = Field(index=True, db=database)

    class UserOne(Node, label="User1"):
        name: str = Field(index=True, db=database)

    class UserTwo(User, label="User2", labels={"User3"}):
        name: str = Field(index=True, db=database)

    class Streamer(User):
        id: str = Field(index=True, db=database)
        followers: Optional[int] = Field()

    class StreamerOne(User, label="Streamer1"):
        id: str = Field(index=True, db=database)
        followers: Optional[int] = Field()

    class StreamerTwo(Streamer, label="Streamer2", labels={"Streamer3", "Streamer4"}):
        id: str = Field(index=True, db=database)
        followers: Optional[int] = Field()

    user = User(name="Kate").save(database)
    userOne = UserOne(name="Mrma").save(database)
    userTwo = UserTwo(name="Boris").save(database)
    streamer = Streamer(id=7, name="Ivan", followers=172).save(database)
    streamerOne = StreamerOne(id=8, name="Bruno", followers=173).save(database)
    streamerTwo = StreamerTwo(id=9, name="Marko", followers=174).save(database)

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


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_node_multiple_inheritance(database):
    class User(Node, labels={"UserX"}):
        id: int = Field(index=True, db=database)
        name: str = Field(index=True, db=database)

    class UserOne(Node, labels={"UserOneX"}):
        pass

    class UserTwo(Node, label="UserTwoX"):
        pass

    class Admin(UserOne, UserTwo, User, label="AdminX", labels={"AdminX", "AdminY"}):
        admin_id: int = Field(index=True, db=database)

    admin = Admin(id=1, admin_id=0, name="Admin").save(database)

    assert UserOne.label == "UserOne"
    assert UserTwo.label == "UserTwoX"

    assert Admin.label == "AdminX"
    assert Admin.labels == {"AdminX", "AdminY", "User", "UserX", "UserOne", "UserOneX", "UserTwoX"}

    assert admin.label == "AdminX"
    assert admin.labels == {"AdminX", "AdminY", "User", "UserX", "UserOne", "UserOneX", "UserTwoX"}
    assert admin._label == "AdminX:AdminY:User:UserOne:UserOneX:UserTwoX:UserX"
    assert admin._labels == {"AdminX", "AdminY", "User", "UserX", "UserOne", "UserOneX", "UserTwoX"}
