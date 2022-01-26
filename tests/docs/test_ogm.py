from gqlalchemy import Memgraph, Node, Relationship, Field, match
from datetime import datetime
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
    description: Optional[str]


class ChatsWith(Relationship, type="CHATS_WITH"):
    lastChatted: Optional[datetime] = Field()


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

        loaded_streamer = result.load(db=db)

        assert loaded_streamer.id == "7"
        assert loaded_streamer.username == "Ivan"
        assert loaded_streamer.url == "myurl.com"
        assert loaded_streamer.followers == 888
        assert loaded_streamer.createdAt == "2022-26-01"
        assert loaded_streamer.totalViewCount == 6666
