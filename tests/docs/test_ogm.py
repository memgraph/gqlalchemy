from gqlalchemy import Memgraph, Node, Relationship, Field, match
from typing import Optional

db = Memgraph()


class UserTmp(Node):
    id: str = Field(index=True, exist=True, unique=True, db=db)


class Streamer(UserTmp):
    id: str = Field(index=True, exist=True, unique=True, db=db)
    username: Optional[str] = Field(index=True, exist=True, unique=True, db=db)
    url: Optional[str] = Field()
    followers: Optional[int] = Field()
    createdAt: Optional[str] = Field()
    totalViewCount: Optional[int] = Field()
    description: Optional[str] = Field()


class ChatsWith(Relationship, type="CHATS_WITH"):
    lastChatted: Optional[str] = Field()


class TestMapNodesAndRelationships:
    def test_node_mapping(self):
        streamer = Streamer(  # noqa F401
            id="7",
            username="Ivan",
            url="myurl.com",
            followers=888,
            createdAt="2022-26-01",
            totalViewCount=6666,
            description="Hi, I am streamer!",
        ).save(db)

        result = next(match().node("Streamer", variable="s").where("s.id", "=", "7").return_().execute())["s"]

        assert result.id == "7"
        assert result.username == "Ivan"
        assert result.url == "myurl.com"
        assert result.followers == 888
        assert result.createdAt == "2022-26-01"
        assert result.totalViewCount == 6666
        assert result.description == "Hi, I am streamer!"

        loaded_streamer = result.load(db=db)

        assert loaded_streamer.id == "7"
        assert loaded_streamer.username == "Ivan"
        assert loaded_streamer.url == "myurl.com"
        assert loaded_streamer.followers == 888
        assert loaded_streamer.createdAt == "2022-26-01"
        assert loaded_streamer.totalViewCount == 6666
        assert loaded_streamer.description == "Hi, I am streamer!"

    def test_relationship_mapping(self):
        streamer_1 = Streamer(
            id="8",
            username="Kate",
            url="myurl.com",
            followers=888,
            createdAt="2022-26-01",
            totalViewCount=6666,
            description="Hi, I am streamer!",
        ).save(db)
        streamer_2 = Streamer(
            id="9",
            username="Mislav",
            url="myurl.com",
            followers=888,
            createdAt="2022-26-01",
            totalViewCount=6666,
            description="Hi, I am streamer!",
        ).save(db)
        chats_with = ChatsWith(
            _start_node_id=streamer_1._id, _end_node_id=streamer_2._id, lastChatted="2021-04-25"
        ).save(db)

        result = next(match().node().to("CHATS_WITH", variable="c").node().return_().execute())["c"]

        assert result._start_node_id == streamer_1._id
        assert result._end_node_id == streamer_2._id
        assert result.lastChatted == chats_with.lastChatted
        assert result._type == chats_with._type

        loaded_chats_with = chats_with.load(db=db)

        assert loaded_chats_with._start_node_id == streamer_1._id
        assert loaded_chats_with._end_node_id == streamer_2._id
        assert loaded_chats_with.lastChatted == "2021-04-25"
        assert loaded_chats_with._type == "CHATS_WITH"
